#!/usr/bin/env python3
"""Detect a stable release, resolve its immutable commit, and create a candidate lock."""
import json, os, pathlib, re, urllib.request
ROOT = pathlib.Path(__file__).resolve().parents[1]
def get(url):
    headers = {'User-Agent':'betaflight-uconsole-release-detector'}
    if os.environ.get('GH_TOKEN'): headers['Authorization'] = 'Bearer '+os.environ['GH_TOKEN']
    with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=30) as r:
        return json.load(r)
def main():
    api = 'https://api.github.com/repos/'
    repo = 'betaflight/betaflight-configurator'
    release = get(api+repo+'/releases/latest')
    tag = release['tag_name']
    if release['draft'] or release['prerelease'] or not re.fullmatch(r'\d+\.\d+\.\d+',tag):
        raise ValueError('Unsupported release tag; review manually')
    ref = get(api+repo+'/git/ref/tags/'+tag)['object']
    for _ in range(5):
        if ref['type'] == 'commit': break
        if ref['type'] != 'tag': raise ValueError('Unexpected ref type')
        ref = get(api+repo+'/git/tags/'+ref['sha'])['object']
    if ref['type'] != 'commit' or not re.fullmatch('[a-f0-9]{40}',ref['sha']): raise ValueError('No commit')
    sha = ref['sha']
    url = 'https://raw.githubusercontent.com/'+repo+'/'+sha+'/.nvmrc'
    with urllib.request.urlopen(url,timeout=30) as r: node = r.read().decode().strip()
    if not re.fullmatch(r'24\.\d+\.\d+',node): raise ValueError('New Node major requires maintainer review')
    lock = dict(repository='https://github.com/'+repo+'.git',tag=tag,commit=sha,node=node,npm='11.6.2')
    (ROOT/'upstream.lock.json').write_text(json.dumps(lock,indent=2)+'\n')
    own = os.environ['GITHUB_REPOSITORY']
    # Compare against ALL own releases, including drafts, with pagination.
    target = 'v'+(ROOT/'VERSION').read_text().strip()+'-bf-'+tag
    existing = False
    for page in range(1,101):
        items = get(api+own+'/releases?per_page=100&page='+str(page))
        existing |= any(item['tag_name'] == target for item in items)
        if len(items) < 100: break
    else: raise ValueError('Release pagination exceeded safety bound')
    with open(os.environ['GITHUB_OUTPUT'],'a') as out:
        out.write('build='+str(not existing).lower()+'\nnode='+node+'\ntag='+target+'\n')
    print(json.dumps(lock,indent=2))
if __name__ == '__main__': main()
