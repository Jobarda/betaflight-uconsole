#!/usr/bin/env python3
"""Explicit, per-user install/update/rollback. Never run with sudo."""
import argparse, fcntl, hashlib, json, os, pathlib, re, shutil, socket, subprocess, sys, tarfile, tempfile, time, urllib.request
HOME = pathlib.Path.home()
BASE = HOME/'.local/share/betaflight-uconsole'
UNIT = HOME/'.config/systemd/user/betaflight-uconsole.service'
DESKTOP = HOME/'.local/share/applications/betaflight-uconsole.desktop'
MARKER = 'betaflight-uconsole-managed-v1'
def ctl(*args, check=True):
    return subprocess.run(['systemctl','--user',*args],check=check,stdout=subprocess.DEVNULL)
def owned():
    if BASE.is_symlink() or not (BASE/MARKER).is_file():
        raise RuntimeError('Refusing unmanaged installation')
def switch(target):
    temp = BASE/'next'
    temp.unlink(missing_ok=True)
    temp.symlink_to(target)
    temp.replace(BASE/'current')
def health():
    expected = hashlib.sha256((BASE/'current/web/index.html').read_bytes()).digest()
    for _ in range(25):
        try:
            ctl('is-active','--quiet','betaflight-uconsole.service')
            with urllib.request.urlopen('http://127.0.0.1:5176/index.html',timeout=1) as r:
                if r.status == 200 and hashlib.sha256(r.read()).digest() == expected: return
        except (OSError,subprocess.CalledProcessError): pass
        time.sleep(.2)
    raise RuntimeError('HTTP health check failed')
def validate_archive(archive, checksum, directory):
    if archive.stat().st_size > 512*1024**2: raise ValueError('Archive too large')
    expected = checksum.read_text().strip().splitlines()
    if len(expected) != 1: raise ValueError('Expect exactly one SHA256SUMS entry')
    parts = expected[0].split()
    if len(parts) != 2 or parts[1] != archive.name or not re.fullmatch('[a-f0-9]{64}',parts[0]):
        raise ValueError('Checksum filename or format mismatch')
    if hashlib.sha256(archive.read_bytes()).hexdigest() != parts[0]: raise ValueError('Checksum mismatch')
    with tarfile.open(archive,'r:gz') as tf:
        members = tf.getmembers()
        if len(members) > 100000: raise ValueError('Too many archive members')
        if sum(m.size for m in members) > 1024**3: raise ValueError('Archive too large')
        names = set()
        for m in members:
            p = pathlib.PurePosixPath(m.name)
            if p.is_absolute() or '..' in p.parts or '\\' in m.name or ':' in m.name or not (m.isfile() or m.isdir()) or m.name in names:
                raise ValueError('Unsafe archive member')
            names.add(m.name)
        tf.extractall(directory,members=members)
    for name in ['web/index.html','runtime/server.py','runtime/launch.sh','manifest.json','LICENSE','NOTICE.md','source/package-lock.json']:
        if not (directory/name).is_file(): raise ValueError('Missing '+name)
    manifest = json.loads((directory/'manifest.json').read_text())
    if manifest.get('schema') != 1: raise ValueError('Unsupported manifest')
    return parts[0]
def activate(archive, checksum):
    owned()
    with tempfile.TemporaryDirectory(dir=BASE) as tmp:
        stage = pathlib.Path(tmp)/'bundle'
        stage.mkdir()
        digest = validate_archive(archive,checksum,stage)
        release = BASE/'releases'/digest
        release.parent.mkdir(exist_ok=True)
        if not release.exists(): stage.rename(release)
    old = os.readlink(BASE/'current') if (BASE/'current').is_symlink() else None
    # Runtime is stable packaging code, installed from this repository, not downloaded updates.
    switch('releases/'+digest)
    try:
        ctl('restart','betaflight-uconsole.service')
        health()
    except Exception:
        if old:
            switch(old)
            ctl('restart','betaflight-uconsole.service',check=False)
        else:
            ctl('stop','betaflight-uconsole.service',check=False)
            (BASE/'current').unlink(missing_ok=True)
        raise
    if old and old != 'releases/'+digest: (BASE/'previous').write_text(old)
def fetch(url, path):
    if not url.startswith('https://github.com/'): raise ValueError('GitHub HTTPS URL required')
    with urllib.request.urlopen(url,timeout=60) as r, path.open('wb') as out:
        count = 0
        while True:
            block = r.read(1024*1024)
            if not block: break
            count += len(block)
            if count > 512*1024**2: raise ValueError('Download too large')
            out.write(block)
def main():
    if os.geteuid() == 0: raise SystemExit('Run as your regular desktop user, without sudo')
    p = argparse.ArgumentParser()
    p.add_argument('action',choices=['install','update','rollback','uninstall','check'])
    p.add_argument('--archive',type=pathlib.Path)
    p.add_argument('--checksums',type=pathlib.Path)
    p.add_argument('--repository',help='Explicit owner/repository for check/update')
    p.add_argument('--tag',help='Explicit published release tag for online update')
    args = p.parse_args()
    if args.action == 'check':
        if not args.repository or not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',args.repository): p.error('Set --repository owner/repository')
        with urllib.request.urlopen('https://api.github.com/repos/'+args.repository+'/releases/latest',timeout=30) as r: release = json.load(r)
        print(release['tag_name'],release['html_url'])
        return
    HOME.joinpath('.cache').mkdir(exist_ok=True)
    with (HOME/'.cache/betaflight-uconsole.lock').open('w') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        if args.action == 'install':
            if not args.archive or not args.checksums: p.error('Supply --archive and --checksums')
            if any(x.exists() or x.is_symlink() for x in [BASE,UNIT,DESKTOP]): raise RuntimeError('Existing managed paths found; no files changed')
            with socket.socket() as sock: sock.bind(('127.0.0.1',5176))
            # Validate before writing any installation files.
            with tempfile.TemporaryDirectory() as t: validate_archive(args.archive,args.checksums,pathlib.Path(t))
            repo = pathlib.Path(__file__).resolve().parents[1]
            BASE.mkdir(parents=True)
            try:
                (BASE/MARKER).touch()
                for name in ['server.py','launch.sh']: shutil.copy2(repo/'runtime'/name,BASE/name)
                UNIT.parent.mkdir(parents=True,exist_ok=True)
                shutil.copy2(repo/'packaging/betaflight-uconsole.service',UNIT)
                DESKTOP.parent.mkdir(parents=True,exist_ok=True)
                launcher = str(BASE/'launch.sh').replace('\\','\\\\').replace('"','\\"').replace('`','\\`').replace('$','\\$').replace('%','%%')
                DESKTOP.write_text('[Desktop Entry]\nType=Application\nName=Betaflight uConsole (Unofficial Beta)\nExec=/bin/sh "'+launcher+'"\nTerminal=false\nCategories=Utility;\n')
                ctl('daemon-reload')
                activate(args.archive,args.checksums)
                ctl('enable','betaflight-uconsole.service')
            except Exception:
                ctl('disable','--now','betaflight-uconsole.service',check=False)
                UNIT.unlink(missing_ok=True)
                DESKTOP.unlink(missing_ok=True)
                shutil.rmtree(BASE)
                ctl('daemon-reload',check=False)
                raise
        elif args.action == 'uninstall':
            owned()
            ctl('disable','--now','betaflight-uconsole.service')
            UNIT.unlink(missing_ok=True)
            DESKTOP.unlink(missing_ok=True)
            shutil.rmtree(BASE)
            ctl('daemon-reload')
        elif args.action == 'rollback':
            owned()
            previous = (BASE/'previous').read_text()
            if not re.fullmatch('releases/[a-f0-9]{64}',previous) or not (BASE/previous/'web/index.html').is_file(): raise ValueError('Invalid rollback target')
            current = os.readlink(BASE/'current')
            switch(previous)
            try:
                ctl('restart','betaflight-uconsole.service')
                health()
            except Exception:
                switch(current)
                ctl('restart','betaflight-uconsole.service',check=False)
                raise
            (BASE/'previous').write_text(current)
        else:
            owned()
            if args.archive and args.checksums: activate(args.archive,args.checksums)
            else:
                if not args.repository or not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',args.repository) or not args.tag or not re.fullmatch(r'[A-Za-z0-9_.-]+',args.tag): p.error('Supply local files or --repository owner/repository --tag release-tag')
                with tempfile.TemporaryDirectory() as tmp:
                    with urllib.request.urlopen('https://api.github.com/repos/'+args.repository+'/releases/tags/'+args.tag,timeout=30) as r: rel = json.load(r)
                    if rel['draft'] or rel['prerelease']: raise ValueError('Only published stable-channel packages accepted')
                    assets = {a['name']:a['browser_download_url'] for a in rel['assets']}
                    bundles = [n for n in assets if re.fullmatch(r'betaflight-uconsole-[A-Za-z0-9_.-]+\.tar\.gz',n)]
                    if len(bundles) != 1: raise ValueError('Expected exactly one bundle')
                    archive = pathlib.Path(tmp)/bundles[0]
                    sums = pathlib.Path(tmp)/'SHA256SUMS'
                    fetch(assets[archive.name],archive)
                    fetch(assets['SHA256SUMS'],sums)
                    activate(archive,sums)
if __name__ == '__main__':
    try: main()
    except Exception as e: print(str(e),file=sys.stderr); sys.exit(1)
