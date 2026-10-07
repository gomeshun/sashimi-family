# Migration・リリース準備：確認待ち引き継ぎ（2026-09-11）

**再開（2026-09-11）：以下のF質量グリッド修正についてユーザーが明示承認した。確認待ちは解消し、実装・検証を再開した。[採用記録](adoption-2026-09-10.md)を参照。以下の確認待ち欄と候補SHAは中断時点の記録として保持し、最終検証後に新しい引き渡しへ置き換える。**

**状態：作業途中。リリース準備完了・最終ピアレビュー待ちとはまだ判定しない。**

ユーザーの就寝時の中断許可に従い、確認待ちの判断を推測せず再開できるよう、完了分と残作業を分けて記録する。main統合、auto-merge、release tag、PyPI/TestPyPI upload、公開workflowの有効化、private Fの公開範囲変更は行っていない。

## 未回答の判断は1件

**Fの降着量へ渡すvirial massを、各降着赤方偏移の値へ修正するか。**

現在の製品は、降着ループ全体で最後の赤方偏移のvirial-mass配列を再利用している。物理・数値設定を固定した独立probe（m22=0.1,1,10、Mhost=1e12 Msun、zmax=3）では、各時点へ直すと生存数が約0.23–0.26%、質量比が約0.85–1.51%減少し、個々の重みは最大約3.06%変わった。これは採否前の感度比較であり、製品の新しい科学仕様としては未採用。

| 選択肢 | 影響 |
| --- | --- |
| **各降着赤方偏移へ修正する（推奨）** | 各時点の定義に一致する質量を使う。Wで修正した配列再利用と同種の問題を解消する。独立B patch、仕様ID、B/C比較、最終F収束試験を更新する。 |
| 現行を維持し制約として明記する | 現行値を保持する。ただし最終時点の質量を全時点へ使う制約を科学仕様・レビュー資料に残す。 |

推奨理由は降着時点と質量定義の整合であり、数値が増減したことや見栄えではない。すでに質問済みで、未回答や時間経過を承認とは扱っていない。根拠はprivate Fの `validation/accretion-mass-grid/report.json` と、再現可能な `validation/references/accretion-grid-4b40b47/`。元の失敗・比較・全配列と生成SHAを保持している。下流のprior/likelihood再解析、新しい係数fit、CLASS再実行はこの選択に含めない。

## 完了した主な作業

- C/SI/W/Fをvariant所有のcomponentに分け、ITAMAE共通実行・重み・検証へ接続。標準importから名前付きcatalogと既存observableを利用できる。製品内physics_mode経路は除去し、旧値は独立A/B参照に保存。
- coreのmetadata/shape/domain、NFW逆関数、ODE、power/variance、cache・provenance契約を実装し、独立toy/解析解と異常系で検証。
- C/SIの高解像度・quadrature・solver比較、SIの直接断面積・形成境界・弱/強相互作用・Cとの構造定義比較を保存。最終EPS修正後の全配列も確認。
- Wはユーザー提供の独立調査に基づき、現行Viel係数のq10だけを通常APIに採用。q5指定を明示的に拒否し、amplitude-half既定を保ちpower-halfを明示指定可能にした。0.5/2/5 keVで各21配列が旧q10固定条件とbitwise一致。旧q5結果・cache履歴は保持。
- Fは修正別A/B、transfer/node/cutoff・native/ITAMAE/Colossus分散とEPS比較を保存。Colossusの符号失敗を隠さず実験的opt-inを維持。質量グリッドの採否だけは先取りしていない。
- 候補版はC 2.0.0rc1、core/SI/W/F 0.2.0rc1。MIT、CITATION、CHANGELOG、移行案内、通常版依存と非稼働の公開手順テンプレートを整備。
- 親Issue #1、#5–#17、core #4/#5、F #4/#5/#6を現方針へ更新。旧本文は折り畳んだ歴史記録として保存。各variantの既存draft umbrellaを更新し、core draft PR #28を作成。いずれもmainへ統合していない。

## 配布物の実行証拠

[監査概要](../validation/artifacts/merged-candidate-packaging-20260911/README.md)と[機械可読summary](../validation/artifacts/merged-candidate-packaging-20260911/summary.json)に、正確なSHA・環境・ハッシュ・由来を保存。

| 対象 | Python 3.11 | Python 3.12 | Python 3.13 |
| --- | ---: | ---: | ---: |
| core installed regression | 309 pass | 309 pass | 309 pass |
| C installed regression | 95 pass | 95 pass | 95 pass |
| SI installed regression | 49 pass | 49 pass | 49 pass |
| W installed regression | 87 pass | 87 pass | 87 pass |
| F installed regression | 94 pass | 94 pass | 94 pass |
| 全5者の標準API数値・重み・保存読込・由来・衝突確認 | pass | pass | pass |
| sdist再構築後の全5者数値確認 | pass | pass | pass |

全wheel/sdistを正確なclean sourceから生成。sdistを無関係のGit repository内へ展開し、revision環境変数なしで再構築してruntime payloadのbitwise一致とmetadata一致を確認した。各package単独の最小環境はPython 3.11で確認した。元wheelの全回帰はtests・参照・build hookだけをsdistから取り出し、isolated Pythonがsite-packagesの製品をimportする形で実行した。

Fの初回c90b002では、配布されない旧analysis runnerをテストがimportしてcollectionが失敗した。F PR #27で製品関数を直接検証するテストに修正し、dc1b305の新配布物で全94テストが通った。計算式は変更していない。変更のない4者のartifactはハッシュ確認して再利用し、F変更後の全5者数値smokeを新規実行した。初回失敗は削除していない。

その後、coreをmerge SHA 6d8ee62、FをCI変更後のmerge SHA 3a34188へ揃え、3種類のPythonで全634テストを再実行して成功した。F PR #28では、元wheelとsdist再構築wheelによる全5者の実計算をprivate CIへ組み込んだ。PR headとmerge headの両方で全チェックが成功し、merge run `34503343420`の取得済みartifactから、同じ基準親97101de・同じ全5 source・3種類のPythonを照合した。旧snapshot、初回collection失敗、旧SHAの配布物は保持している。

この成功は暫定候補のpackaging証拠であり、Fの未採用仕様や最終recorded familyの成功を意味しない。

## 保存場所

いずれもこの作業環境のローカル成果物。公開repoへFの生catalogやprivate sourceをコピーしていない。

- 公開4者のwheel/sdist：`review-artifacts/20260911-merged/dist/`（gitignore、ハッシュは上記summaryに記録）。
- Fのwheel/sdist：`sashimi-f/artifacts/release-preparation-20260911-merged/dist/`（private、gitignore）。
- 全5者の全数値・テスト証拠：`sashimi-f/artifacts/release-preparation-20260911-merged/full-evidence/`（private、gitignore）。
- 元の作業環境とログ：`/tmp/sashimi-migration-20260910/rc-packaging-merged-core-20260911/`、`/tmp/sashimi-migration-20260910/rc-packaging-merged-family-20260911/`。元のinterim出力も別ディレクトリに保持。
- 再利用可能runner：`scripts/build_candidate_artifacts.py`、`scripts/check_installed_candidate.py`、`scripts/smoke_installed_family.py`、`scripts/check_sdist_rebuild.py`。

## ソースと作業状態

以下は一時effective manifestで検証した候補集合であり、恒久的な互換性集合を新設するものではない。canonicalは引き続きrootの`compatibility.toml`。この更新後の証拠の基準親commitは `97101de1c1473af2ad813d0d7914afc364a4e863`。

| Repo | ローカルbranch | 検証した完全SHA |
| --- | --- | --- |
| itamae | `codex/release-candidate-20260910` | `6d8ee62b65793df9b799977cbf1859b5233d4059` |
| sashimi-c | `codex/c-release-candidate-20260910` | `2caa94d990f034f17f8bdb32ca7d9c5ac0d50fd5` |
| sashimi-si | `codex/si-release-candidate-20260910` | `7cfbeb60fccd87150cf80a7b54c191eddf0a15a5` |
| sashimi-w | `codex/w-q10-only-20260911` | `0b3146678e68ea71735173e4effb313f872fb9b9` |
| sashimi-f | `codex/f-artifact-family-ci-20260911` | `3a34188347ccc6e795e6fb640f9db1870ff4383b` |

全child候補はorigin/itamae-migrationへ統合済み。 初回core artifactはtopic head dfa083d由来だったが、現在は実際のmigration merge 6d8ee62から再構築し、そのsource identityで全5者を再検証した。旧証拠のSHAを付け替えていない。親の作業branchは `codex/migration-release-20260910`。親のcommitted gitlinkとmanifestは旧確認済み集合のままで一致している。作業ツリーの5つのsubmoduleは上表の候補へ進めているため、親でmodifiedと表示されるのは意図した状態。**最終科学判断が済む前にgitlinksだけstageしない。**

この引き継ぎ文書と証拠のcommit SHAは親branchの履歴から確認できる。最後の確認時点で数値計算workerは終了し、未回収の計算jobはない。core draft PR #28は全チェック成功、draft・未統合・auto-merge無効を確認した。各variant umbrellaもdraftのまま。CのPicard default提案PR #5と親の旧C昇格PR #33は変更・統合していない。

## API・既存機能の対応

| 対象 | 標準入口と保持した機能 | 主な検証先 |
| --- | --- | --- |
| C | `SubhaloProperties.subhalo_catalog_calc`、`SubhaloObservables`のmass_function、Nsat_Mpeak/Vpeak、mass_fraction、boost、prompt-cusp、seeded MC | standard_api、boost_inputs、runtime/solver tests、science notebook |
| SI | `SubhaloProperties.subhalo_catalogs_calc`、`SIDM_cross_section`、`SIDM_parametric_model`の既存断面積・profile/gravothermal | migration、formation、cross_section、stage_velocity tests、states/resolution report |
| W | `Subhalos.rs_rhos_catalog_calc`、既存N_sat/N_sat_Vthres、transfer/variance/half-mode | migration、q10 policy、variance、reference comparison |
| F | `FDMSubhaloProperties.subhalo_catalog_calc`、`FDMSubhaloObservables`のmass/count/fraction/boost/MC、process_m_22 | migration、population、boost、process、cutoff/backend tests |

Tuple関数は表現変換として残す。旧式を呼ぶ裏口として使わない。SIのstate、survivalとvalidity、各weight因子、canonical unitsと由来は名前付き出力に保持する。

## 既知の制約と確認の重点

- C prompt-cuspの必要な外部入力表が得られず、科学計算の検証はユーザー承認で延期。明示的な欠落エラーを実装済み。代替データを創作していない。
- C/SIの細かなmass/redshift刻みでも有限の残差がある。記録した最細dzの比較でbound massは約0.75–0.77%、Nma 256→500で約0.50%変わる。coarse設定のperturbative→ODE差は約3.82%。solver既定は変更していない。
- SIのnative Cとの構造差はdensity/mass定義の整合を明記して説明した。未比較の重力定数・velocityまで一致と主張しない。
- Fはtidally evolved NFWモデルのまま。Colossusのcutoff以下での符号問題を保持し、nativeと交換可能とはしない。FDM solitonや下流再解析は対象外。
- TestPyPI/PyPIの認証、公開権限、public-index依存解決は未実施。Fの著者確認と公開範囲変更も後日の別gate。

## canonical source・権利・同期

Fのplanned canonical sourceはユーザー確認済みの `gomeshun/sashimi-f`。独立した別upstream remoteは設定されておらず、推測で追加しない。MIT、Ando/Horigome/Elisa Gouvea Mauricio Ferreiraのnotice、ユーザー作成CAMB入力の由来を候補に含めた。ユーザーは公開前にElisaへ確認する。現時点のprivate設定を維持する。

将来の同期ではoriginの対象branch/SHAをfetchし、current mainとmigrationの差分・入力/solver/thresholdを確認する。変更前のA/Bと生成metadataを保存し、topic branchで小さなPRへ分ける。履歴をforceで揃えず、必要な数値・配布物・exact-family検証を新しいSHAで実行する。

## 再開手順

1. F質量グリッドへの回答を確認し、[採用記録](adoption-2026-09-10.md)へ記す。未回答なら依存する科学仕様を確定しない。
2. 採用ならprivate Fで最小の独立B patchと製品変更を分けて実装。失敗する保護テスト、旧/新1要因比較、仕様/cache ID更新、0.1/1/10のfull-catalog・observable一致を確認。現行維持ならその明示判断と科学的制約を記録する。
3. Fの必要なmass/redshift/host・concentration quadrature/solver収束を、固定設定と独立outputで実行する。完了済みC/SI/Wや旧41-mass prior campaign、CLASSを無目的に再実行しない。F notebook・CITATION/README/CHANGELOGの最終科学記述を整える。
4. private Fの両配布形式・再構築CIはPR #28で実装・実行済み。科学変更をchild CIへ通してmigrationへ統合し、新SHAのF artifactと影響範囲を再検証する。公開4者が不変ならハッシュ確認したartifactを再利用する。
5. 一時effective manifestで全5者を確認する。その後、親のmanifestと5 gitlinksを**同じcommit**に記録し、[準備済みCI案](release-preparation/README.md)を適用する。旧manifestのまま新API用CIを有効にしない。
6. その同じ親SHAを指定して公開CIとprivate Fのno-override（workflowのpromoted）modeを実行し、artifact/sourceと入力集合を照合する。以前のcandidate-mode成功を流用しない。
7. 最終review資料・umbrella説明を最終集合へ更新し、必要な確認が全て済んだ時点で「migration上のリリース準備完了・ピアレビュー待ち」として停止する。mainへ進まない。

main統合・公開は、ピアレビュー後の別の明示指示を待つ。許可後も各repoを順序付きで統合し、実際のmerge SHAからartifactを再構築、影響検証と全familyを再確認する。公開順序はcore→variantsとし、配布後のindexからのclean installをその時点で確認する。
