# Release procedure

1. Create a GitHub repository and enable Actions and private security reporting.
2. Review all source and pins; run CI. Trigger the upstream workflow manually first.
3. Inspect the draft's candidate lock, source commit and workflow logs. Download the
   bundle; verify SHA256SUMS and source/notices. Confirm no secrets, paths, browser
   state, personal names, network information or device identifiers are present.
4. Review upstream changes and dependency advisories. Verify the included dependency
   sources and notices cover everything bundled into web assets, including packages
   whose npm distribution may omit required corresponding source. Resolve any gaps
   before publishing. Include packaging source access alongside the binary release.
5. Run the target matrix in TESTING.md. Label automated build success separately
   from hardware results. If hardware is not tested, retain that limitation visibly.
6. Edit release notes with actual results, OS/browser versions and known limitations.
   Publish the draft manually when satisfied. v0.1.0 remains an unofficial beta.
7. Never overwrite an already published asset; increment packaging version if rebuilt.
   Commit the candidate lock for a new default if desired. Keep old releases for rollback.

Optional updates accept published non-prerelease-channel assets only. A beta-quality
package may still be published on that channel; the word beta in these documents
describes testing maturity. Keep drafts private until review. To use GitHub's formal
prerelease flag instead, use the offline update path; the online updater rejects it.
