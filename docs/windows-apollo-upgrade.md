# Upgrade an Apollo Windows host to Vibepollo

Checked on 2026-11-09 for this fork's `6.2.0-daily.199-local.1` Mac client.
This is a host-upgrade guide, not a security audit of Vibepollo or a record of a completed host upgrade.

## Which clients need changing?

Not every client needs an upgrade. Vibepollo supports standard Moonlight clients using
H.264, HEVC or AV1 where the client and host support those codecs. Other existing clients
should be tested individually after migration; do not assume every platform exposes the
same features or permissions.

Use Nonary's compatible Moonlight fork (including this patched Mac build) for PyroWave
and its VRR playback improvements. PyroWave is selected explicitly in each client's codec
settings; it is not automatically imposed on all devices. A conventional Moonlight device
can continue using its ordinary codec while the Mac uses PyroWave.

See the [stable host's codec compatibility table](https://github.com/Nonary/Vibepollo/blob/2.0.6/docs/pyrowave-protocol.md#compatibility).
The documented PyroWave bitstream ID is `186f0393`, matching the client baseline reviewed here.

## Prepare the Windows PC

1. Finish active streams and arrange direct access to the gaming PC. Installation may stop
   streaming services or change display drivers; do not rely on the stream being upgraded
   as your only way back into the PC.
2. Record the current Apollo version and retain its installer for rollback.
3. Back up Apollo's actual configuration location outside its installation directory,
   including applications, pairing state, credentials and artwork. If unsure, preserve the
   entire installation folder plus any separately configured data directory. Record current
   display/virtual-display settings. Backups containing credentials should remain private.

## Install stable Vibepollo 2.0.6

This version was the latest stable release when checked. Newer numeric versions may be
prereleases: verify the release label rather than assuming the largest number is stable.

1. Open the [2.0.6 release page](https://github.com/Nonary/Vibepollo/releases/tag/2.0.6) and download
   **VibepolloSetup-v2.0.6.exe** on Windows.
2. Verify the download in PowerShell:

   ```powershell
   Get-FileHash "$HOME\Downloads\VibepolloSetup-v2.0.6.exe" -Algorithm SHA256
   ```

   Expected SHA-256 for that exact asset when checked:

   ```text
   C488977AC49E391DFD963D97439A01A9C56D4FF21A6061226ADB6D69D0AAE9E4
   ```

   If it differs, stop and check the release asset's current published digest. Do not reuse
   this checksum for another version or run a mismatched download.
3. Run the installer. It detects Apollo and asks permission to uninstall it before installing
   Vibepollo. Let the installer coordinate this transition instead of manually uninstalling
   Apollo first. Review driver selections; avoid factory-reset or configuration-removal options.
4. Restart Windows if requested. Open Vibepollo's web interface using its tray/Start-menu entry.
5. Confirm applications, paired clients, permissions and display settings carried over. Automatic
   migration is not a substitute for the backup. If data is missing, keep the backup intact and
   investigate the migration before resetting the host or removing paired clients.

The [installer source](https://github.com/Nonary/Vibepollo/blob/2.0.6/packaging/windows/bootstrapper/VibeshineInstaller.cs)
contains the Apollo detection/uninstall prompt. The [release notes](https://github.com/Nonary/Vibepollo/releases/tag/2.0.6)
describe Windows installer fixes in this release.

## Validate ordinary streaming first

On the Mac, run `moonlight`. Use HEVC or H.264 initially and confirm video, audio, keyboard,
mouse/controller input, disconnect/reconnect and clean exit. Test the other clients you use
before retiring the backup. Pair again only if migration did not preserve that client's pairing;
check host permissions if a paired client cannot launch or control a session.

## Enable VRR and PyroWave separately

For the patched Mac client:

| Setting | Starting choice |
| --- | --- |
| Renderer | Auto |
| V-Sync | On |
| VRR | On with a compatible variable-refresh display |
| Requested FPS | No higher than the display supports |
| Initial format | SDR, 4:2:0 |
| Codec for the PyroWave test | PyroWave, selected explicitly |

Use Vibepollo's virtual-display mode when testing its automatic VRR capture integration.
Keep the initial requested FPS within the Mac display's capabilities; do not manually set
Windows to the host's internally managed high virtual-refresh mode.

Disconnect any active stream before running **Calibrate PyroWave** in the Mac client.
PyroWave uses substantial bandwidth and is intended for wired LANs. Prefer Ethernet on both
ends for the first test; HEVC may be the better choice when the Mac uses Wi-Fi. Apply a
calibrated recommendation rather than guessing a very high bitrate. Test HDR and 4:4:4 only
after basic streaming is working.

The [host PyroWave guide](https://github.com/Nonary/Vibepollo/blob/2.0.6/docs/pyrowave-protocol.md)
and [Mac rendering notes](https://github.com/Nonary/moonlight-qt/blob/19758e5e62bfb1388798aa4c68370b8e2c06d5e9/docs/macos-vrr-pyrowave.md)
explain requirements and validation limits. Passing calibration does not prove sustained gameplay
smoothness. Retain HEVC/H.264 as a fallback if a codec or display combination is unreliable.

## Recovery

If migration or streaming fails, retain installer logs and the backup; avoid repeated resets.
For rollback, stop active streams, use the installed product's normal uninstall flow, reinstall
the recorded Apollo version and restore its saved configuration while its service is stopped.
Review display-driver choices rather than blindly removing shared drivers. Do not run Apollo
and Vibepollo streaming services concurrently. Keep the backup until all clients you use have
been validated.

Client build, installation and rollback instructions: [local-macos-build.md](local-macos-build.md).
