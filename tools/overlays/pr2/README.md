# Reviewed PR #2 and PR #4 refinements

This layer preserves the reviewed design changes from GitHub PR #2 at `7affdbe1ecabc61cf1d081e8d5d152894c40fa11`, reconciled with the local `0.3.6-rc.6` product/copy/exception/formal-frontend contract.

The import tools first apply the existing rc.6 adapters, then replay these patches. `metadata.json` pins the exact baseline, patch and output digests. Unknown inputs fail instead of replacing reviewed content silently. Reapplying the refinement to its exact output is a no-op. Three new method documents are explicit local extensions with their own hashes and no invented upstream source.

To revise this layer, review the package and patch together, update the pinned digests intentionally, then run both import tools twice and the adapter regression. Do not refresh a digest merely to silence an unexpected upstream difference. The original imported source hashes remain in `package/design-source.json` and `package/figma-source.json`.

`integration_sha256` now means the rc.6 adapted baseline immediately before this layer; `sha256` means the merged current document. These patches are repository build resources; they are not installed as duplicate Skills or shipped in the runtime package.

## PR #4 integration (2026-11-09)

`integrated_prs` pins the follow-on 18 commits ending at `5f3c7a2715435fe608339610a3150fe1c6ab5882`. The same replay layer now covers the reviewed method, registry and runtime-script changes. Product owns the single copy baseline; design proposes reasoned edits and reuses specific valid approval rather than creating another final copy table.

The 109 separately curated visual-library files are pinned under `bundled_resources`. They stay in their single canonical package location, versioned in Git, and are validated and registered again by the importer. They are not recoverable from the older upstream designer repository: restore missing or changed resources from the reviewed Git revision before import. No duplicate image tree or automatic network retrieval is introduced.
