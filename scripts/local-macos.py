#!/usr/bin/env python3
"""Build, verify, install, or roll back this account's hardened Moonlight."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
QT = ROOT / 'build/tooling/qt/6.11.1/macos'
BUILD = ROOT / 'build/macos-arm64'
RELEASES = ROOT / 'build/releases'
INSTALLED = Path.home() / 'Applications/Moonlight.app'

def run(*args, cwd=ROOT, env=None, log=None):
    subprocess.run([str(a) for a in args], cwd=cwd, env=env, check=True,
                   stdout=log, stderr=subprocess.STDOUT if log else None)

def output(*args):
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()

def closed(app):
    # Use the same exact executable-path check as the staging helper.
    import importlib.util
    spec = importlib.util.spec_from_file_location('stage', ROOT / 'scripts/stage-macos-build.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    module.require_staged_app_closed(app)

def verify(release):
    app = release / 'Moonlight.app'
    run('codesign', '--verify', '--deep', '--strict', app)
    run('lipo', app / 'Contents/MacOS/Moonlight', '-verify_arch', 'arm64')
    import importlib.util
    spec = importlib.util.spec_from_file_location('stage', ROOT / 'scripts/stage-macos-build.py')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    count = module.audit_dependencies(app, release / 'dependencies.log')
    print(f'Verified {count} Mach-O files')

def build():
    if output('git', 'status', '--porcelain'):
        raise RuntimeError('Commit reviewed source changes before building an installable release.')
    sha = output('git', 'rev-parse', 'HEAD')
    version = '6.2.0-daily.199-local.1'
    release = RELEASES / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + sha[:12])
    release.mkdir(parents=True)
    BUILD.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy(); env['CI_VERSION'] = version
    with (release / 'build.log').open('w') as log:
        run(QT / 'bin/qmake', ROOT / 'moonlight-qt.pro', 'QMAKE_APPLE_DEVICE_ARCHS=arm64',
            'CONFIG+=release', 'CONFIG-=debug', cwd=BUILD, env=env, log=log)
        run('make', '-j8', 'release', cwd=BUILD, env=env, log=log)
    # Stamp identity before the staging helper seals the app.
    plist = BUILD / 'app/Moonlight.app/Contents/Info.plist'
    import plistlib
    info = plistlib.loads(plist.read_bytes())
    info.update(MoonlightNightlyVersion=version, MoonlightSourceCommit=sha, CFBundleVersion='6.2.199.1')
    plist.write_bytes(plistlib.dumps(info))
    run(sys.executable, ROOT / 'scripts/stage-macos-build.py', '--source-app', BUILD / 'app/Moonlight.app',
        '--qt-dir', QT, '--deploy-dir', release)
    verify(release)
    archive = release / 'Moonlight-arm64.zip'
    run('ditto', '-c', '-k', '--keepParent', release / 'Moonlight.app', archive)
    manifest = {'source_commit': sha, 'version': version, 'architecture': 'arm64', 'qt': '6.11.1',
                'submodules': output('git', 'submodule', 'status', '--recursive').splitlines(),
                'sdk': output('xcrun', '--show-sdk-version'), 'compiler': output('clang', '--version'),
                'sha256': hashlib.file_digest(archive.open('rb'), 'sha256').hexdigest(),
                'live_host_validation': 'pending; no host upgrade performed'}
    (release / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    (release / 'SHA256SUMS').write_text(manifest['sha256'] + '  ' + archive.name + '\n')
    print(release)

def install(release):
    release = release.resolve()
    if release.parent != RELEASES.resolve(): raise RuntimeError('Choose a direct child of build/releases.')
    manifest = json.loads((release / 'manifest.json').read_text())
    archive = release / 'Moonlight-arm64.zip'
    with archive.open('rb') as stream:
        if hashlib.file_digest(stream, 'sha256').hexdigest() != manifest['sha256']:
            raise RuntimeError('Release archive checksum mismatch')
    verify(release); closed(INSTALLED)
    INSTALLED.parent.mkdir(exist_ok=True)
    staged = INSTALLED.with_name('Moonlight.installing.app')
    if staged.exists(): raise RuntimeError(f'Inspect and remove stale staging path first: {staged}')
    run('ditto', release / 'Moonlight.app', staged)
    run('codesign', '--verify', '--deep', '--strict', staged)
    if INSTALLED.exists():
        backup = RELEASES / ('backup-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
        backup.mkdir(); run('ditto', INSTALLED, backup / 'Moonlight.app')
        shutil.rmtree(INSTALLED)  # exact installed app only, after backup; no user data
    staged.rename(INSTALLED)
    (RELEASES / 'installed.json').write_text(json.dumps({'release': str(release), **manifest}, indent=2) + '\n')
    print(f'Installed {INSTALLED}; settings and pairings were preserved')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['build', 'verify', 'install', 'rollback'])
    parser.add_argument('release', nargs='?', type=Path)
    args = parser.parse_args()
    try:
        if args.action == 'build': build()
        elif not args.release: parser.error('Specify a release directory')
        elif args.action == 'verify': verify(args.release.resolve())
        else: install(args.release)  # rollback deliberately selects a previous verified release
    except (RuntimeError, subprocess.CalledProcessError) as error:
        sys.exit(str(error))
