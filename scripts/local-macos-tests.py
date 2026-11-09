#!/usr/bin/env python3
"""Run the local release gates; stores complete logs and a machine-readable result."""
import json, os, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/validation'
QT = ROOT / 'build/tooling/qt/6.11.1/macos/bin/qmake'
env = os.environ.copy()
env.update(DYLD_LIBRARY_PATH=str(ROOT / 'libs/mac/lib'), QT_QPA_PLATFORM='offscreen')
OUT.mkdir(parents=True, exist_ok=True)
results = {}
def run(name, argv, cwd=ROOT, timeout=180):
    with (OUT / (name + '.log')).open('w') as log:
        try:
            p = subprocess.run([str(a) for a in argv], cwd=cwd, env=env, stdout=log, stderr=subprocess.STDOUT, timeout=timeout)
            results[name] = p.returncode
        except subprocess.TimeoutExpired:
            results[name] = 'timeout'
    print(name, results[name], flush=True)
    return results[name] == 0
for name, project in [('security','tests/security/security.pro'), ('pairing','tests/security/pairing.pro'), ('updates','tests/updates/updates.pro'), ('power','tests/power/poweractions.pro'), ('vrr','tests/vrr/vrr.pro')]:
    d = ROOT / 'build/checks' / name; d.mkdir(parents=True, exist_ok=True)
    if run(name+'-qmake', [QT, ROOT/project, 'CONFIG+=release', 'QMAKE_APPLE_DEVICE_ARCHS=arm64'], d) and run(name+'-build', ['make','-j8'], d):
        for exe in sorted(d.rglob('tst_*')):
            if exe.is_file() and os.access(exe, os.X_OK) and not exe.suffix:
                run(exe.name, [exe] + ([ROOT/'app'] if exe.name=='tst_overlay' else []), d)
for suite in ['test_macos_bundle_signature.py','test_daily_release.py','test_nightly_notes.py']:
    run(suite, [sys.executable,'-B','-m','unittest','discover','-s','scripts/tests','-p',suite,'-v'])
flags = ['-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer']
obj = OUT/'lz4.o'
if run('lz4-sanitizer-build', ['clang', *flags,'-c','third-party/lz4/lz4.c','-o',obj]):
    for name in ['framing','compression']:
        exe = OUT/('sanitized-'+name)
        if run(name+'-sanitizer-build', ['clang++','-std=c++17',*flags, f'tests/pyrowave/tst_pyrowave{name}.cpp','app/streaming/video/pyrowave/pyrowaveframing.cpp','pyrowave/compression/pyrowavecompression.cpp', obj,'-o',exe]):
            run(name+'-sanitizer', [exe])
summary = {'source_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'results':results}
(OUT/'results.json').write_text(json.dumps(summary,indent=2)+'\n')
sys.exit(any(value != 0 for value in results.values()))
