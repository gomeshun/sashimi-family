# Physical walkthrough and src-layout validation

`summary.json` records exact sources, artifact hashes, all 668 installed tests per Python 3.11–3.13, source-archive rebuilds, standalone installs, runtime relocation and archived-notebook preservation. `recorded-ci.json` audits the downloaded public/private CI for parent `b6a22141faf2d191a49885d127464789514fd775` with no overrides.

The notebook execution SHA and the artifact SHA have different roles. Fresh execution records the code actually used. Later commits save the outputs or adjust CI, tests and documentation. Runtime source relocation is checked separately, and installed-artifact tests use the exact final SHA recorded by the family manifest.

Public distributions are saved in `review-artifacts/20260911-layout-physical/dist/`. Private F distributions and all five components' full local evidence are in `sashimi-f/artifacts/layout-physical-20260911/`. The full evidence includes the effective manifest, its baseline/overrides, build logs, test XML/reports, rebuilt wheels, the verification driver, and notebook catalogs. Environments can be recreated; the temporary virtual environments themselves were not copied.

To rebuild, check out the five recorded revisions, validate the committed parent manifest/gitlinks, then run `scripts/build_candidate_artifacts.py` with that manifest and a new output directory. Install those wheels in isolated environments and use `scripts/check_installed_candidate.py`, `scripts/smoke_installed_family.py` and `scripts/check_sdist_rebuild.py`. All output directories must be new. Do not overwrite frozen results or inject a different source revision.

Re-audit the saved CI from the family repository:

```sh
python3 scripts/summarize_recorded_family.py \
  --parent-sha b6a22141faf2d191a49885d127464789514fd775 \
  --public-evidence review-artifacts/20260911-layout-physical/recorded-ci \
  --private-evidence sashimi-f/artifacts/layout-physical-20260911/recorded-ci \
  --output /tmp/layout-physical-ci-reaudit.json
```

CI setup failures during the review were fixed without changing equations: SI's moved equation tests were collected from the standard tests directory, and W's src package is installed before its regressions. W's physical notebook retains two warning categories from the existing EPS intermediate expression; final catalog columns and weights were checked separately. Local grid refinements are sensitivity checks, not external scientific calibration.

The F notebook used 10,654,592 KiB peak resident memory in a complete 395.69-second local run. Two earlier private CI attempts received runner shutdown signals; no OOM trace was available. Since the measured peak exceeds the standard private Linux runner RAM (8 GB in the current [GitHub specification](https://docs.github.com/en/actions/reference/runners/github-hosted-runners)), its workflow adds 8 GiB temporary swap and records resource use without changing the physical grid. The probe, failed logs and retry are preserved privately.

The pre-memory-fix layout artifacts remain in the sibling directories ending in `-before-ci-memory-fix`; their source identities and same-parent CI at `7529210557eb0141f6553c1cb773f363368d22ad` remain historical evidence. The final artifacts use `b6a22141faf2d191a49885d127464789514fd775`.

All five notebook CI outputs have been downloaded and checked against committed source cells and expected figure counts. The final F retry [34561543634](https://github.com/gomeshun/sashimi-f/actions/runs/34561543634) completed in 504.01 seconds with 7,376,200 KiB peak RSS; its VM reported 10 GiB total swap after the 8 GiB addition. The notebook and independent scientific comparison both passed. The calculation still uses the full physical grid.
