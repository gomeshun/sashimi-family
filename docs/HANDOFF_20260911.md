# SASHIMI migration・リリース準備のレビュー引き渡し

2026-09-11。**migration上のリリース準備完了・ピアレビュー待ち。実装・科学検証・配布物・同一親SHAでの公開/private最終CIは完了。**

実行計画は [sashimi-migration-goal.md](../sashimi-migration-goal.md)、恒久的な互換性記録は [compatibility.toml](../compatibility.toml) を参照する。下記SHA表は今回の検証対象の記録。[中断時点の引き継ぎ](HANDOFF_checkpoint_20260911.md) と以前の検証結果は履歴として保持している。

## 変更とレビュー対象

- C/SI/W/Fの物理処方をvariant所有のcomponentへ分け、ITAMAEの共通実行・単位・数値計算・重み・検証・provenanceへ接続した。標準importから名前付きcatalogと既存observableを利用できる。製品内の`physics_mode`と旧式を実行する継承経路は除去した。
- 凍結した旧実装A、修正を一つずつ適用した独立参照B、新製品Cを別プロセスで比較した。旧fixture・生成SHA・失敗結果・旧cache識別子を保持し、許容誤差を広げて未知の差を通していない。
- coreのmetadata/shape/domain、NFW逆関数、ODE、power/variance、cache契約は独立toy・解析解・異常系で検証した。C/SIの高解像度試験、SIの直接断面積・形成境界・弱/強相互作用とCとの構造定義比較を保存した。
- Wはユーザー提供の独立調査に基づき、現行Viel係数ではq10のみを通常APIに採用。q5指定は明示的に拒否する。0.5/2/5 keVの固定条件で各21配列が旧q10とbitwise一致する。amplitude-half既定と明示的なpower-halfを区別した。
- Fはユーザー承認済みの各降着赤方偏移のvirial-mass gridを降着率・対数質量積分へ採用。仕様を`sashimi-f:fdm:2026-09-11:v3`へ進め、旧structure-prior出力の誤再利用も防いだ。独立B patch、3質量での全catalog比較、60件の収束計算、notebook更新まで完了した。

レビュー入口は親draft [PR #34](https://github.com/gomeshun/sashimi-family/pull/34)、親Epic [#1](https://github.com/gomeshun/sashimi-family/issues/1)、core [PR #28](https://github.com/gomeshun/itamae/pull/28)、C [PR #3](https://github.com/gomeshun/sashimi-c/pull/3)、SI [PR #2](https://github.com/gomeshun/sashimi-si/pull/2)、W [PR #1](https://github.com/gomeshun/sashimi-w/pull/1)、private F [PR #1](https://github.com/gomeshun/sashimi-f/pull/1)。Fの最後の修正単位は [PR #29](https://github.com/gomeshun/sashimi-f/pull/29)。main向けumbrellaはdraftで保持する。

## ソースと候補配布物

各childの以下のSHAは`origin/itamae-migration`へ統合済み。親の作業branchは`codex/migration-release-20260910`。

| Repo | ローカル作業branch | 検証対象SHA | 候補版 |
| --- | --- | --- | --- |
| itamae | `codex/release-candidate-20260910` | `6d8ee62b65793df9b799977cbf1859b5233d4059` | 0.2.0rc1 |
| sashimi-c | `codex/c-release-candidate-20260910` | `2caa94d990f034f17f8bdb32ca7d9c5ac0d50fd5` | 2.0.0rc1 |
| sashimi-si | `codex/si-release-candidate-20260910` | `7cfbeb60fccd87150cf80a7b54c191eddf0a15a5` | 0.2.0rc1 |
| sashimi-w | `codex/w-q10-only-20260911` | `0b3146678e68ea71735173e4effb313f872fb9b9` | 0.2.0rc1 |
| sashimi-f | `codex/f-accretion-redshift-20260911` | `98e1f91d3d0b55c8652518b507c0fec8044c2aff` | 0.2.0rc1 |

配布名は`sashimi-itamae`、import名は`itamae`。各variantは通常の版依存`sashimi-itamae>=0.2.0rc1,<0.3`を宣言する。core/C/SI/Wの不変なwheel/sdistはハッシュ照合して再利用し、Fは最終merge SHAから再生成した。各artifactの完全なSHA-256・サイズ・環境・再構築記録は [候補artifact summary](../validation/artifacts/final-v3-candidate-20260911/summary.json) にある。

| 検証 | Python 3.11 | Python 3.12 | Python 3.13 |
| --- | ---: | ---: | ---: |
| core installed regression（不変artifactの証拠を再利用） | 309 pass | 309 pass | 309 pass |
| C installed regression（同上） | 95 pass | 95 pass | 95 pass |
| SI installed regression（同上） | 49 pass | 49 pass | 49 pass |
| W installed regression（同上） | 87 pass | 87 pass | 87 pass |
| F installed regression（今回のartifactで再実行） | 104 pass | 104 pass | 104 pass |
| 元wheelの全5者実計算・重み・保存読込・由来・非衝突（今回再実行） | pass | pass | pass |
| sdist再構築wheelの全5者実計算（今回再実行） | pass | pass | pass |

合計644テスト/版の証拠が揃っている。不変な540テストを今回再実行したとは扱わない。元sdistのtests・参照・build hookだけを取り出し、isolated Pythonがsite-packagesの製品をimportして試験した。全5 sdistsを無関係のGit repository内でrevision環境変数なしに再構築し、実行コード・同梱データ・metadataの一致とsource identity保持を確認した。単独最小環境はPython 3.11で確認済みで、今回core+Fを新しいartifactで再実行した。

各variantのusage/science notebookは別々にfresh kernelで実行し、図を目視確認した。Fの最終usageは4、scienceは6 code cells。coreの実行済み7セルと2図は [CI由来の保存notebook](../validation/artifacts/final-v3-candidate-20260911/itamae-usage-walkthrough.executed.ipynb) で確認できる。coreの必須Ruff/format/mypy/coverage、Python/backend/minimal/artifact CIも成功している。

## 証拠と再現手順

- 公開4者のwheel/sdist：`review-artifacts/20260911-final-v3/dist/`。
- private Fのwheel/sdist：`sashimi-f/artifacts/release-preparation-20260911-final-v3/dist/`。
- 全5者の数値・インストール済みテスト・ログ・再構築記録：上記privateディレクトリの`full-evidence/`。
- F merge-source candidate CI：[run 34549662699](https://github.com/gomeshun/sashimi-f/actions/runs/34549662699)。取得済み証拠は同privateディレクトリの`candidate-ci-34549662699/`。基準親97101deと全overrideを記録したcandidate modeであり、最終no-override検証と区別する。
- 科学検証の索引：[時系列worklog](migration-worklog-2026-09-10.md)、[独立参照手順](../validation/references/README.md)、各componentの`docs/`と`notebooks/scientific_validation.ipynb`。private Fの最終証拠は`validation/accretion-v3/`、`docs/accretion-redshift-grid.md`、`docs/resolution-v3.md`。

上記artifactディレクトリはGit管理対象外だが、このworkspaceへ永続コピー済み。public repoへprivate Fのソースや生catalogをコピーしていない。旧candidate、初回失敗、旧仕様結果はそれぞれ元の識別情報で残している。

同じ候補を再検証する場合は、まずcommitted HEADで`python3 scripts/check_compatibility.py`を実行し、manifestで指定したソースをcheckoutする。`scripts/build_candidate_artifacts.py`で両配布形式を作成し、`check_artifact_provenance.py`で照合する。独立環境へwheelhouseの候補をインストールし、`check_installed_candidate.py`と`smoke_installed_family.py`をソースツリー外で実行する。`check_sdist_rebuild.py`は無関係Git内での再構築・source identity保持を確認する。実際に使ったlocal driverとeffective manifestはprivate evidenceに保存済み。

## 既存機能と標準API

| 対象 | 標準入口と維持機能 | 主な検証 |
| --- | --- | --- |
| C | `SubhaloProperties.subhalo_catalog_calc`、`SubhaloObservables`のmass_function、Nsat_Mpeak/Vpeak、mass_fraction、boost、prompt-cusp入口、seeded MC | standard_api、boost_inputs、runtime/solver tests、science notebook |
| SI | `SubhaloProperties.subhalo_catalogs_calc`、`SIDM_cross_section`、`SIDM_parametric_model`の断面積・profile/gravothermal | migration、formation、cross_section、stage_velocity、states/resolution |
| W | `Subhalos.rs_rhos_catalog_calc`、N_sat/N_sat_Vthres、transfer/variance/half-mode | migration、q10 policy、variance、reference comparison |
| F | `FDMSubhaloProperties.subhalo_catalog_calc`、`FDMSubhaloObservables`のmass/count/fraction/boost/MC、process_m_22 | migration、population、boost、process、cutoff/backend、accretion-v3 |

Tuple関数は形式変換として維持する。SIのstate、survival/validity、独立weight因子、canonical unitsと由来は名前付き出力に保持する。Cのprompt-cuspの数値検証は、次項の承認済み延期に従う。

## 科学的結果とレビューの重点

Fの最後の修正は質量定義と降着時点の整合を回復するもので、係数やsolverは変えていない。m22=0.1/1/10の固定条件で、独立Bと製品Cは元の`rtol=2e-11`内で一致し、重みの最大相対差は約8.08e-12。修正前後の9構造配列とsurvivalはbitwise同一で、重み・observableが変化する。生存数は約0.23–0.26%、質量比は約0.85–1.51%減少し、個々の重みの最大変化は約3.06%。旧配列や生成metadataをv3へ付け替えていない。

60件のF収束計算は1変数ずつの比較で、同時連続極限の認定ではない。mass fractionの最終Nma 256→500差は最大約0.28%、dz 0.01→0.005差は約0.76–0.87%、concentration quadrature 5→7差は約8.3e-5%、host quadrature 64→200差は最大約0.0082%。coarse条件のperturbative→ODE差は約3.9%あり、既定solverを変更していない。全配列の有限性・非負weight・降着質量上限を確認し、RuntimeWarningは0件だった。

- C prompt-cuspの必要な外部入力表が得られないため、科学計算の検証はユーザー承認で延期した。欠落時の明示的エラーとAPI入口を維持し、代替データを創作していない。
- C/SIにも有限解像度残差がある。最細dz比較でbound mass約0.75–0.77%、Nma 256→500で約0.50%、coarse条件のperturbative→ODE差約3.82%。各比較の条件を揃えて解釈する。
- SI/Cの構造一致には文書化したdensity/mass定義の整合が必要。未比較の重力定数・velocityまで一致したとは主張しない。
- Fはtidally evolved NFWモデル。Colossusのcutoff以下での微分符号・EPS失敗は保持し、実験的opt-inのまま。nativeとの交換可能性、soliton、新たな下流prior/likelihood較正は主張しない。
- 回帰・収束・配布物の成功をsimulationへの較正、coverage、観測制限の更新と同一視しない。

## ユーザー判断・権利・公開条件

[採用記録](adoption-2026-09-10.md) にSI断面積、Fのdirect top-hat、Wの生存observable、q10、Fの各降着赤方偏移gridの承認と範囲を記録した。今回の準備に必要な科学判断の未回答はない。候補版・MIT・canonical source・C prompt-cusp延期の合意は時系列worklogにも記録している。

Fのplanned canonical sourceはユーザー確認済みの`gomeshun/sashimi-f`。別upstreamを推測で追加していない。MIT、Ando/Horigome/Elisa Gouvea Mauricio Ferreiraのnotice、ユーザー作成CAMB入力の由来を候補に含めた。ユーザーは公開前にElisaへ確認する。Fはprivateのままで、現段階の準備承認を公開設定変更の許可として扱わない。

## 親の記録と最終CI

`compatibility.toml`と5 gitlinks、公開family CIを **`8184e572c37af051011b85f1b797bfda6d7dfb7d`** の一つの親migration commitへ記録した。committed HEADの一致を確認した後、次の両CIで同じ親SHAを検証し、どちらも成功した。

- 公開4者：[run 34550691401](https://github.com/gomeshun/sashimi-family/actions/runs/34550691401)、Python 3.11–3.13。
- private全5者：[run 34550711351](https://github.com/gomeshun/sashimi-f/actions/runs/34550711351)、Python 3.11–3.13、`family_mode=promoted`、`overrides={}`。

両runの取得済みartifactを [監査runner](../scripts/summarize_recorded_family.py) で照合した。親SHA・manifest・全source identity、元wheel/sdistのハッシュ、再構築wheelの実ファイルハッシュとsource identity、両配布形式の実計算・非衝突・保存読込の成功を確認した。各Python版の元/再構築の物理量も一致した。[最終CI summary](../validation/artifacts/recorded-family-20260911/summary.json) と [保存場所・再監査手順](../validation/artifacts/recorded-family-20260911/README.md) を参照。

この結果を保存する後続コミットは、証拠・監査runner・文書の追加である。上記CIの検証対象SHAを後続コミットへ付け替えない。manifest、5 gitlinks、既存のCIと数値検証runnerは検証時と同一のまま保持する。

## ピアレビュー後の工程

1. 独立参照・仕様変更、SI状態境界、W q10とhalf-mode定義、F backend制約・v3収束、artifact由来をレビューする。必要な修正はmigration/topic branchへ小さなPRで反映する。
2. main統合には別の明示指示を得る。各repoのremote/main/migration差分と未コミット状態を確認し、core→variants→親の順を調整する。複数repoのmergeは順次操作であり、atomicな公開を仮定しない。
3. 実際の統合SHAからwheel/sdistを再生成し、影響する回帰・科学検証と正確な全5者検証を実行する。今回のartifactを新SHAの証拠へ読み替えない。
4. Fのcoauthor確認・公開範囲と、PyPI認証・権限・public-index依存解決をその時点で確認する。公開の明示許可後にcore→variantsの順で公開し、indexからのclean installを確認する。

main統合、auto-merge、release tag、PyPI/TestPyPI upload、公開workflowの起動・予約・有効化、Fのvisibility変更は今回実行しない。CのPicard default提案PR #5と親の旧C昇格PR #33は未統合のまま保持する。
