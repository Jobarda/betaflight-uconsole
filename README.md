# betaflight-uconsole v0.1.0

Unofficial community beta packaging for a local Betaflight Configurator web build.
Target: Debian 11 ARM64 on a uConsole, with a Chromium browser supporting Web Serial.
This is a packaging project, not an official Betaflight or hardware vendor release.

**Status:** source repository and automation candidate; no prebuilt Configurator is
included in this ZIP. The new installer, workflow, updater and hardware compatibility
have not been validated end to end. See [testing status](docs/TESTING.md).

An earlier independently installed setup was reported to work after reboot and with
Wi-Fi disconnected. Its source revision is unknown; that result does not validate
this repository's pinned build. No existing installation is migrated or renamed.

## What is included

- Immutable upstream commit, exact Node/npm versions and upstream npm lockfile build.
- Daily stable upstream release detection, clean build, HTTP smoke check, draft releases.
- Optional explicit updates with SHA-256 checking, atomic activation and rollback.
- Per-user loopback static server, systemd user service and separate Chromium profile.
- Source inclusion, licensing notices, security model and hardware test checklist.

## Build the pinned version

Use a fresh Linux checkout with Git, Python 3.9+, Node 24.12.0 and npm 11.6.2.
Build tools run only on the build host. They are not needed on the target device.

```sh
npm install --global npm@11.6.2
python3 -m unittest discover -s tests -v
python3 scripts/build.py
python3 scripts/smoke.py
```

The output is `dist/betaflight-uconsole-0.1.0-bf-2026.6.2.tar.gz` plus
`dist/SHA256SUMS`. The archive includes `web/`, upstream `source/`, runtime,
manifest and notices. Build from a fresh checkout each time. See
[reproducibility limits](docs/BUILD.md); bit-for-bit reproducibility has not been proven.

## Install a separately built bundle

Do not install on a working device until you have tested the candidate on a spare
system or accept the beta status. Keep any existing installation in place.
Prerequisites: a graphical Debian session, systemd user manager, `/usr/bin/python3`,
and Chromium installed through your distribution. No root installation is performed.
On Debian, an administrator can install prerequisites with
`sudo apt install python3 chromium`; do not run this project's manager with sudo.

Download and inspect this repository, the bundle, and its matching `SHA256SUMS`.
Run from the repository root as your regular desktop user:

```sh
python3 scripts/manage.py install \
  --archive dist/betaflight-uconsole-0.1.0-bf-2026.6.2.tar.gz \
  --checksums dist/SHA256SUMS
```

The installer refuses existing project paths or an occupied port. It creates only
`~/.local/share/betaflight-uconsole/`, its user unit, and its desktop entry; a lock
file is kept under `~/.cache/`. It uses port **5176** and does not touch older services.
Launch **Betaflight uConsole (Unofficial Beta)** from the desktop menu.
The service starts on user login, not before login; no lingering is enabled.

```sh
systemctl --user status betaflight-uconsole.service
curl -I http://127.0.0.1:5176/index.html
journalctl --user -u betaflight-uconsole.service
```

## Optional updates and removal

There is no background updater or automatic device installation. Replace
`OWNER/REPOSITORY` with the GitHub repository you explicitly trust. A checksum from
the same release detects corruption, not a compromised publisher.

```sh
python3 scripts/manage.py check --repository OWNER/REPOSITORY
python3 scripts/manage.py update --repository OWNER/REPOSITORY --tag v0.1.0-bf-2026.6.2
python3 scripts/manage.py rollback
python3 scripts/manage.py uninstall
```

Offline update: use `update --archive PATH_TO_BUNDLE --checksums PATH_TO_SHA256SUMS`.
Updates replace web assets only; repository/runtime upgrades require uninstall and
reinstall with the reviewed new repository. Rollback retains all downloaded bundles
until uninstall and restores the last successfully replaced web build. HTTP checks
cannot confirm serial connection, UI function, or compatibility with cached PWA data.
After an update fully close and reopen the separate Chromium window. Clear that
profile's site storage if stale content persists. Back up browser data first if needed.
Uninstall removes this project's bundles and separate browser profile. It leaves
browser packages, device permissions, other services and the cache lock file alone.

## USB and offline use

Remove propellers before bench tests. Authorize your controller in Chromium's serial
device chooser. Verify your distribution's serial-device group/udev policy; this
project never changes groups, installs broad USB rules, disables services, grants
world-writable permissions, or launches a browser as root. Re-login after any group
change made by your administrator. Do not use browser security-bypass flags.

Local assets are served offline. Firmware downloads, maps, presets, cloud functions
and other upstream network features may still need internet. Debian 11's available
Chromium may be too old for the pinned upstream app; browser compatibility and ARM64
hardware tests are required before claiming support. Do not bypass browser security
or replace OS libraries to force compatibility.

## Publish on GitHub

Create your own empty repository and upload/commit the extracted directory contents,
including `.github/`. No personal Git remote or contact address is embedded.
Enable Actions, then run **Detect and build upstream candidate**. It creates a
**draft**, never a public release automatically. Inspect logs, source/license
inventory, lock and checksums, complete [release gates](docs/RELEASING.md), then
publish manually. GitHub's scheduled jobs can be delayed or disabled for inactivity.

See [build](docs/BUILD.md), [testing](docs/TESTING.md), [security](SECURITY.md),
[privacy review](docs/PRIVACY.md), [license](LICENSE), and [notices](NOTICE.md).
