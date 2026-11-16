# Build and update architecture

The repository lock pins upstream 2026.6.2 at
`091127c1a5b15268321b0e5b71b8cec89f1de56b`, Node 24.12.0, npm 11.6.2.
The builder fetches that commit, checks package version and .nvmrc, uses `npm ci`,
and asserts package-lock.json did not change. It runs the upstream `vite build`
through `npm run build`. No upstream application source patch is applied.

References verified during preparation:
- https://github.com/betaflight/betaflight-configurator/releases/tag/2026.6.2
- https://github.com/betaflight/betaflight-configurator/commit/091127c1a5b15268321b0e5b71b8cec89f1de56b
- https://github.com/betaflight/betaflight-configurator/blob/2026.6.2/package.json
- https://github.com/betaflight/betaflight-configurator/blob/2026.6.2/.nvmrc

Normalized tar ownership, mode, ordering, timestamps and gzip metadata improve
reproducibility. This is a reproducible-input recipe, not a proven byte-identical
build: npm lifecycle scripts, external dependencies, upstream nondeterminism,
runner image changes and network availability remain factors. The Linux runner
image is versioned by OS label, not an immutable image digest. Compare checksums
from two isolated clean builds before claiming byte reproducibility.

Dependencies use upstream's committed npm lockfile, including integrity fields
where upstream provides them. A Git dependency or lifecycle script can have a
different trust model. Do not claim all dependency execution is hermetic.

The scheduled detector excludes prereleases/drafts, resolves annotated tags to
commits, accepts strict numeric release tags and Node major 24 only. It writes a
candidate lock in the workflow workspace. That lock travels with the build and
release; it does not silently change this repository's reviewed default lock.
New Node majors, changed upstream output structure, missing lockfiles or failed
builds stop the workflow. npm changes require manual review. Duplicate own release
tags, including drafts, suppress repeat builds. To retry a failed draft after fixes,
delete the draft/tag through GitHub deliberately or increase the packaging version.

Detection and build use read-only repository credentials. The build checkout does
not persist credentials and receives no publish secret. Only the separate draft
job has contents-write access. Actions are pinned to commit SHAs. The draft tag
points at the packaging workflow commit, while the separate attached lock identifies
the upstream build. Review and commit a new default lock if you want local builds
to follow a candidate. The initial pinned build can be run locally; the scheduled
workflow always follows upstream's latest stable release.

Static web assets are architecture-independent; this is not an ARM64 Chromium,
Node, NW.js or firmware binary. Target support depends on browser/OS capabilities.
