# Unofficial community beta — automated candidate

Build-only candidate; ARM64 device, Debian 11 browser/USB, installer and systemd
integration are hardware unverified. Automated success is not hardware certification.
No relation to a previously tested local installation is implied.

Attached upstream.lock.json identifies the exact source/toolchain; bundle manifest
records the upstream npm lock digest. SHA256SUMS provides corruption detection,
not publisher authentication. Source and dependency notices are inside the bundle;
packaging source is available from the release tag's source archives.

Maintainer: complete docs/RELEASING.md, replace this paragraph with actual test results,
review license/source completeness, and document known limitations before publishing.
No user device is upgraded automatically.
