# PR #2 reviewed refinements

This layer preserves the reviewed design changes from GitHub PR #2 at `7affdbe1ecabc61cf1d081e8d5d152894c40fa11`, reconciled with the local `0.3.6-rc.6` product/copy/exception/formal-frontend contract.

The import tools first apply the existing rc.6 adapters, then replay these patches. `metadata.json` pins the exact baseline, patch and output digests. Unknown inputs fail instead of replacing reviewed content silently. Reapplying the refinement to its exact output is a no-op. Three new method documents are explicit local extensions with their own hashes and no invented upstream source.

To revise this layer, review the package and patch together, update the pinned digests intentionally, then run both import tools twice and the adapter regression. Do not refresh a digest merely to silence an unexpected upstream difference. The original imported source hashes remain in `package/design-source.json` and `package/figma-source.json`.

`integration_sha256` now means the rc.6 adapted baseline immediately before this layer; `sha256` means the merged current document. These patches are repository build resources; they are not installed as duplicate Skills or shipped in the runtime package.
