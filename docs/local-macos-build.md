# Locally maintained Moonlight for Apple Silicon

Start here when maintaining the build installed in `~/Applications/Moonlight.app`.
Source: `~/repos/external/moonlight-qt`, branch `local/macos-hardened`.
Origin is `jp-dubya/moonlight-qt`; `upstream` is Nonary; `moonlight-upstream` is official Moonlight.
The initial baseline is Nonary `19758e5e62bfb1388798aa4c68370b8e2c06d5e9` (daily.199).

## What is maintained

This branch adds UUID-only artwork cache paths with canonical containment and symlink rejection,
atomic artwork writes, redacted request logs, and official upstream pairing/certificate/version
validation and owner-only exclusive log creation. Invalid saved host identifiers are ignored.
Valid existing host settings/pairings retain their protocol identities. Artwork can be regenerated.
VRR and PyroWave remain available. Clipboard synchronization is not added; explicit clipboard
paste remains an optional client-to-host shortcut. Host updates/configuration are separate work.
Local builds skip upstream update notifications. All updates are manual and reviewed.

## Bootstrap

Use Xcode command-line tools and Python 3.11+. From the source root:

```sh
git submodule update --init --recursive
python3 -m venv build/tooling/venv
build/tooling/venv/bin/pip install 'aqtinstall @ git+https://github.com/miurahr/aqtinstall.git@073e34d7c2ab4ae6961ed7cca690b3abd5ba5a7e'
build/tooling/venv/bin/aqt install-qt mac desktop 6.11.1 clang_64 -O build/tooling/qt -m qtshadertools qtimageformats
python3 setup-deps.py
```

The Mac dependencies are the official v8 macOS-universal archive; the downloader verifies a
pinned SHA-256 before extraction. Record any intentional dependency changes and review their
source before changing the pinned digest. The SDK is Qt 6.11.1; Qt warns that Apple's 27.2 SDK
is newer than its tested SDK. Treat successful builds as local evidence, not vendor certification.
Tooling and outputs are ignored under `build/`; dependencies are ignored under `libs/`.

## Build and verify

Commit reviewed source, then run `python3 scripts/local-macos.py build`.
It builds native arm64, stages runtime libraries, removes the unused Mimer SQL plugin,
ad-hoc signs the bundle, checks dependencies/signatures, and smoke-tests `--help`.
Each immutable `build/releases/<UTC>-<commit>/` contains the app, ZIP, manifest, hashes and logs.
This is a local signature, not a Developer ID signature or notarization.

Before building, run `python3 -B scripts/local-macos-tests.py`. It runs security, pairing,
updates, power and VRR suites, sanitized PyroWave framing/compression tests, and Python
release/package checks. It needs loopback networking and stores results in `build/validation/`. Keep results with the release. Only passing required
checks qualify a release for installation; a successful compile alone is insufficient.

`python3 scripts/local-macos.py verify build/releases/<release>` repeats package checks.
`python3 scripts/local-macos.py install build/releases/<release>` installs while the app is closed.
`python3 scripts/local-macos.py rollback build/releases/<previous-release>` restores an earlier
verified release the same way. Existing installed apps are backed up before replacement.
The installer never deletes preferences or pairing state. Keep current and previous releases.

## Updating

Fetch upstreams, inspect changes and official security fixes, select an exact baseline, and
reapply the small local patch series on a new branch. Resolve conflicts, rerun validation,
commit, and build again. Increment the local version in the build helper when releasing.
Tag installed revisions `local-macos-YYYYMMDD.N`; push source and tags to origin.
Do not publish personal logs, manifests with machine paths, credentials, or pairings.
Inherited Actions are disabled; do not re-enable release workflows without reviewing them.

The installed app retains Moonlight's bundle identity and preferences. Do not run stock
Moonlight and the local fork simultaneously. The existing AWDL wrapper launches the exact
installed path; its sudoers rule and networking behavior are independently maintained.

After installation verify visible launch/exit, host pairing, HEVC/H.264, VRR, then PyroWave,
controller input, and reconnect. Without a reachable compatible host, report those checks as
pending; never infer live streaming performance from unit tests. Uninstall by closing and
removing only `~/Applications/Moonlight.app`; keep source/artifacts and preferences for recovery.

## Windows host upgrade

For an existing Apollo Windows host, see [the Vibepollo upgrade guide](windows-apollo-upgrade.md),
including backups, stable installer verification, client compatibility and PyroWave testing.
