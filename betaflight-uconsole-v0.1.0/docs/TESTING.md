# Testing and evidence

## Prior local report

A separate pre-existing Debian ARM64 setup was reported healthy through its user
service and local HTTP check, then reported functional after a reboot with Wi-Fi
disconnected. No source commit, browser version, flight-controller inventory or
formal log was supplied. No personally identifying setup details are retained here.
This report is not a test of the new package.

## New repository status

See VALIDATION.md for checks actually run while preparing this artifact.
GitHub Actions execution, upstream compilation, install/uninstall on Debian 11,
real systemd integration, browser UI, ARM64 USB/Web Serial, cold boot and offline
operation of this pinned build remain UNTESTED unless a later release records them.
Archive validation/transaction unit tests are simulations, not hardware validation.

## Required target matrix

Record package checksum, upstream commit, OS release, architecture, Chromium version,
and anonymized controller/firmware compatibility (no serial numbers or usernames).

1. On a spare Debian 11 ARM64 graphical system, confirm install needs no root,
   creates only documented paths, refuses collisions and leaves existing apps intact.
2. Verify user service health, loopback-only bind and launcher after user login.
3. Remove propellers; test serial chooser, connect, Setup display, disconnect and reconnect.
4. Reboot; log in and repeat with Wi-Fi disabled. Note network-only features separately.
5. Test a second valid bundle, close/reopen Chromium and check version/UI and USB.
6. Try a corrupted archive/checksum; confirm current build remains unchanged.
7. Force candidate HTTP health failure; confirm old current target and service restore.
8. Roll back manually and repeat browser/USB checks. Test a first-install failure cleanup.
9. Uninstall and confirm all unrelated apps, service units, files and permissions remain.
10. Test occupied port, existing managed paths, no user manager, low disk space,
    interrupted update, unsupported browser, missing prerequisites and download failure.

CI runs archive safety/rollback tests and built-index HTTP smoke checks. It does not
provide complete browser tests or dependency vulnerability clearance. Add hardware
results only when performed; retain hardware-unverified labeling otherwise.
