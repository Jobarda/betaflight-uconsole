# Artifact validation — 2026-11-16

This is a source repository ZIP, not a compiled Configurator release or hardware
certification. No connection to a target device or modification to an existing
installation was made during preparation.

Performed in the preparation environment:

- Manual review of all shipped code and documentation, including installation paths,
  archive handling, release permissions, rollback, privacy and test-status claims.
- Python unit checks: archive checksum/name validation, traversal/link/special-file
  rejection, valid extraction, successful update state, failed-update restoration,
  scoped uninstall and in-memory HTTP request handling. Systemd and link switches
  are mocked in transaction tests; this is not Linux integration evidence.
  Final local run: 10 tests, 9 passed, 1 network test explicitly skipped.
- Python syntax and Python 3.9 grammar compatibility checks.
- Repository documentation link-target and immutable-lock structure checks.
- Privacy scan of every shipped text file and the final ZIP entries: no personal
  account names, host paths, device identifiers or private network addresses found.
  Only the standard loopback address is used. Public platform names are intentional.
- ZIP contents match the reviewed repository files; SHA-256 companion supplied.

Execution limits:

- The real loopback HTTP test was attempted but this environment denied the network
  request. It is explicitly skipped for the local test run using
  `BETAFLIGHT_TEST_NO_NETWORK=1`; CI does not set that flag. In-memory handler checks
  passed. The built-asset smoke script still needs a real upstream build.
- The local shell could not start because this environment denied its runtime
  initialization. Shell syntax and systemd validation are configured in Linux CI
  but were not executed here. Workflow YAML was manually reviewed, not executed.
- Outbound source/build access was unavailable to the local build runtime. Upstream
  release, commit, scripts and Node pin were verified from public upstream pages;
  `npm ci`, compilation, GitHub workflows, dependency source/license completeness,
  repeated-build reproducibility and published-release downloads remain untested.
- Debian 11 ARM64 installation, real user systemd behavior, Chromium compatibility,
  USB/Web Serial, browser cache behavior, reboot/offline and rollback on actual
  hardware remain untested for this new package.

Run CI and the documented release/target checklists before publishing binaries.
The prior independent local success report is documented separately in TESTING.md;
it is not evidence that this new code has been installed or hardware tested.
