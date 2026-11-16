# Security policy and trust boundaries

This unofficial beta has no promised maintenance SLA. Report vulnerabilities privately
through the hosting repository's GitHub Security Advisories when available. Do not
post credentials, personal logs or exploit details publicly; repository owners should
enable private reporting before inviting use. No private contact address is assumed.

The server binds only to 127.0.0.1 and serves only the web directory, not bundled
source or metadata. It has no authentication or TLS and is for one desktop user;
do not expose it to a LAN, reverse proxy or multi-user untrusted host. Browser device
permissions and local processes remain separate trust boundaries. The browser profile
can contain controller settings or other private data; do not publish it.

Downloads require HTTPS, explicit repository and explicit tag; no automatic device
update timer exists. SHA-256 validates integrity against a companion checksum file.
It does not authenticate the publisher if an attacker replaces both files. There
are no release signatures or signature verification in v0.1.0. Trust the repository,
GitHub account and Actions supply chain; verify a digest through another trusted
channel when available. Never pipe remote content into a shell.

Archives reject traversal, absolute paths, links, special files and duplicates, and
have expanded-size/download limits. Activation is an atomic same-filesystem symlink
change protected by an advisory manager lock. HTTP failure restores the old web build.
A power loss can leave an unused release directory or a changed current link; inspect
service health after boot and roll back explicitly. This is not a full filesystem
transaction or a browser compatibility test. Same-user attackers can modify the
installation and are out of scope. Tar extraction assumes a private staging directory.

Downloaded application JavaScript is executable browser content. Upstream build and
npm lifecycle scripts execute on CI under read-only privileges, but compromise can
still poison outputs. Do not give the build a signing key or write token. Review
upstream changes and dependency licenses/vulnerabilities before publishing a draft.
Runtime code is installed from the reviewed repository and is not replaced by the
web updater. Repository upgrades require a new deliberate install.

The installer never runs apt, sudo, firmware flashing, USB permission changes or
network-facing service changes. Uninstall removes managed data and the separate
browser profile. Keep backups of controller configuration outside the installation.
