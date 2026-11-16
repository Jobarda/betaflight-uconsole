#!/usr/bin/env python3
"""Build only from the reviewed immutable lock; run inside the pinned Node toolchain."""
import hashlib, json, os, pathlib, shutil, subprocess, tarfile, gzip
ROOT = pathlib.Path(__file__).resolve().parents[1]
def run(*args, cwd=None):
    return subprocess.check_output(args, cwd=cwd, text=True).strip()
def main():
    lock = json.loads((ROOT/'upstream.lock.json').read_text())
    assert run('node','--version') == 'v'+lock['node'], 'Node version mismatch'
    assert run('npm','--version') == lock['npm'], 'npm version mismatch'
    work = ROOT/'work'
    work.mkdir(exist_ok=True)
    src = work/'upstream'
    if src.exists():
        raise SystemExit('work/upstream exists; use a fresh checkout for each build')
    run('git','init',str(src))
    run('git','remote','add','origin',lock['repository'],cwd=src)
    run('git','fetch','--depth=1','origin',lock['commit'],cwd=src)
    run('git','checkout','--detach','FETCH_HEAD',cwd=src)
    assert run('git','rev-parse','HEAD',cwd=src) == lock['commit']
    assert (src/'.nvmrc').read_text().strip() == lock['node']
    assert json.loads((src/'package.json').read_text())['version'] == lock['tag']
    lockhash = hashlib.sha256((src/'package-lock.json').read_bytes()).hexdigest()
    os.environ['SOURCE_DATE_EPOCH'] = run('git','show','-s','--format=%ct',cwd=src)
    os.environ['TZ'] = 'UTC'
    os.environ['HUSKY'] = '0'
    subprocess.run(['npm','ci','--no-audit','--no-fund'],cwd=src,check=True)
    subprocess.run(['npm','run','build'],cwd=src,check=True)
    assert hashlib.sha256((src/'package-lock.json').read_bytes()).hexdigest() == lockhash
    assert (src/'dist/index.html').is_file()
    stage = work/'bundle'
    stage.mkdir()
    shutil.copytree(src/'dist',stage/'web')
    shutil.copytree(ROOT/'runtime',stage/'runtime')
    shutil.copytree(src,stage/'source',ignore=shutil.ignore_patterns('.git','node_modules','dist'))
    # Preserve installed production dependency files and notices, not only a list of URLs.
    deps = run('npm','ls','--omit=dev','--all','--parseable',cwd=src).splitlines()
    for item in sorted(deps, key=len):
        dep = pathlib.Path(item)
        if dep == src or 'node_modules' not in dep.relative_to(src).parts:
            continue
        dest = stage/'source'/dep.relative_to(src)
        if not dest.exists():
            shutil.copytree(dep,dest,ignore=shutil.ignore_patterns('.bin'))
    shutil.copytree(ROOT/'scripts',stage/'packaging-source/scripts',ignore=shutil.ignore_patterns('__pycache__'))
    shutil.copytree(ROOT/'packaging',stage/'packaging-source/packaging')
    shutil.copytree(ROOT/'runtime',stage/'packaging-source/runtime')
    for name in ['VERSION','upstream.lock.json','LICENSE','NOTICE.md']:
        shutil.copy2(ROOT/name,stage/'packaging-source'/name)
    for name in ['LICENSE','NOTICE.md','upstream.lock.json','VERSION']:
        shutil.copy2(ROOT/name,stage/name)
    (stage/'manifest.json').write_text(json.dumps({'schema':1,'upstream':lock,'package_lock_sha256':lockhash,'hardware_verified':False},indent=2)+'\n')
    out = ROOT/'dist'
    out.mkdir(exist_ok=True)
    name = 'betaflight-uconsole-'+(ROOT/'VERSION').read_text().strip()+'-bf-'+lock['tag']+'.tar.gz'
    target = out/name
    epoch = int(os.environ['SOURCE_DATE_EPOCH'])
    with target.open('wb') as raw, gzip.GzipFile(filename='',mode='wb',fileobj=raw,mtime=epoch) as gz, tarfile.open(fileobj=gz,mode='w') as tf:
        for path in sorted(stage.rglob('*')):
            if path.is_symlink():
                raise RuntimeError('Symlink in bundle')
            info = tf.gettarinfo(str(path),arcname=str(path.relative_to(stage)))
            info.uid = info.gid = 0
            info.uname = info.gname = ''
            info.mtime = epoch
            info.mode = 0o755 if path.is_dir() else 0o644
            if path.is_file():
                with path.open('rb') as f: tf.addfile(info,f)
            else: tf.addfile(info)
    (out/'SHA256SUMS').write_text(hashlib.sha256(target.read_bytes()).hexdigest()+'  '+name+'\n')
    print(target)
if __name__ == '__main__': main()
