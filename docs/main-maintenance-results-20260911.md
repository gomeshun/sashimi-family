# SASHIMI standalone 保守作業の完了報告

2026-09-11。[承認済み計画](main-maintenance-plan-20260911.md) の実装・数値検証・レビュー準備を完了し、C/SI/W/F の `minor-updates` へ push した。各 PR は draft のまま保持する。main の merge、tag、release、PyPI/TestPyPI 公開は行っていない。

## ブランチと検証対象

| Repo | 基準 main | 完了 commit | Draft PR |
| --- | --- | --- | --- |
| C | `e09571b` | [`c8f8029`](https://github.com/gomeshun/sashimi-c/commit/c8f80295e86f61dcf39ee3d427217d3ae12099ba) | [#22](https://github.com/gomeshun/sashimi-c/pull/22) |
| SI | `e17d366` | [`fecbd2c`](https://github.com/gomeshun/sashimi-si/commit/fecbd2c33c63d79124bde22bcd0172a434f4e0e6) | [#18](https://github.com/gomeshun/sashimi-si/pull/18) |
| W | `99dfc36` | [`0a997ab`](https://github.com/gomeshun/sashimi-w/commit/0a997abbf031b9630769b81d286b504a3c59bae3) | [#17](https://github.com/gomeshun/sashimi-w/pull/17) |
| F | `68d617e` | [`013db64`](https://github.com/gomeshun/sashimi-f/commit/013db646aa99a29da72f45ef6bf0b831558573a8) | [#31](https://github.com/gomeshun/sashimi-f/pull/31) |

完全な SHA、CI job URL、確認時刻は [監査記録](main-maintenance-audit-20260911.json) に保存した。各最終 commit の push と PR の両 CI で Python 3.10〜3.13 が成功している。各作業ツリーは clean。元の migration 作業ツリーは切り替えていない。

family のこのブランチは文書だけを追加する。`compatibility.toml` と5個の gitlink は migration の記録なので変更しない。standalone の検証対象は上表の各リポジトリの commit であり、family の gitlink から standalone 版を選ぶ設計にはしていない。

## 修正項目と根拠

各 repo の `validation/maintenance` に、修正前に失敗した再現試験、凍結 main の A、独立 patch を適用した B、全配列・mask・入力 hash・依存記録を保存した。F の生データと patch は private F 内に保持する。

| 計画 ID | 完了した変更 | 主な独立検証・回帰試験 |
| --- | --- | --- | --- |
| SI-1 | 全断面積の分母を既存微分 API の角度積分と整合 | `test_total_is_angular_integral`、catalog 非依存試験 |
| SI-2 | 有効分岐だけを評価し、桁落ち域を同値な正の積分で計算 | 65桁参照、overflow/分岐境界、弱/強相互作用 catalog |
| SI-3 | EPS 支持域と有限 zero-gap 極限、真の異常の明示 | Na model 1/2/3、host node 1/64/200、zero-gap |
| SI-4 | 単一 host node の `(Nz,Nm)` shape を維持 | 赤方偏移数と質量点数が異なる配列 |
| SI-5 | 未形成 node の逆向き SIDM 進化を避ける | 形成域 B、形成済み全配列・weight の一致、除外 node の0/false |
| SI-6 | NFW 逆関数を正確な数値解法へ変更 | 高精度逆関数、0、極端な半径、ct=0.77 の両側 |
| W-0 | `np.alen` 廃止と現行 `simpson` 対応 | 旧依存 A、独立 endpoint-rule ablation、現行 CI |
| W-1 | 平坦な背景、D(0)=1、整合した成長微分 | H(0)、密度和、有限差分、単独/組合せ ablation |
| W-2 | physical mass の h 変換と微分の D² | scalar/array、連鎖律、成長次数恒等式 |
| W-3 | 同じ sharp-k 積分と moving-boundary derivative | 元 spectrum 節点ごとの独立適応積分・有限差分、負 weight を clipping しない |
| W-4 | 各降着赤方偏移の質量を EPS と積分に使用 | evolved mass row の照合、zmax 延長時の局所率不変性 |
| W-5 | 有効な濃度候補のみ評価、NFW 逆関数を修正 | 有限な future-redshift 候補の保持、高精度境界 |
| W-6 | 生存集団の厳密な総数/累積、引数転送 | weight [2,3,5] で7、全破壊0、厳密な >、空/単一、両 mass 表示 |
| W-7 | 承認済み q10 を両 filter に適用 | 0.5/2/5 keV の power・variance・構造・catalog、q5/q10 分離 |
| F-1 | 成長微分の h⁻² と分散微分の D 一乗を訂正 | growth 有限差分、D²、単独 ablation |
| F-2 | native top-hat の分散と微分を同じ直接積分に統一 | query 順序、範囲外 query、cold/warm、有限差分、全 catalog |
| F-3 | 各降着質量 row と EPS/積分座標を統一 | m22=0.1/1/10、局所率、構造/weight の分離 |
| F-4 | NFW と EPS の支持域・極限を修正 | 高精度 inverse、閾値両側、各 Na model、zero-gap |
| F-5 | 保存 power/prior/boost の計算 identity を検証 | particle mass・solver・設定・source/helper/table hash、旧データ拒否、atomic combine |

W は14、F は8通りの独立 correction ablation を再生成し、符号を含む効果を `ablation-effects.json` に記録した。F の旧 `reset_interp_sigmaTopHat` は入力を検証する deprecated no-op として残した。W の既存 `dlnSigmadlnM_interp(M=...)` keyword も最終監査で保持を確認した。

## Picard と受入結果

C/W/F は `method="picard_table"`、SI は全100時点の履歴を計算する `method="picard"` を既定にした。C PR #5 の helper を基礎に、各 variant の背景・host history・係数を保持した。旧 solver は明示指定で利用できる。未知の kwargs、無効入力、外挿は黙って受け入れない。

| Repo | テスト数 / Python | solver 最大相対誤差 | catalog 最大質量相対誤差 | 全 catalog 中央値 speedup |
| --- | ---: | ---: | ---: | ---: |
| C | 36 | 0.000163482 | 0.000275143 | 1.075x |
| SI | 69 | 0.000284253 | 2.70303e-05 | 1.138x |
| W | 42 | 0.000266883 | 0.000444313 | 2.921x |
| F | 65 | 0.000164061 | 0.000275165 | 1.215x |

合計212テストを4環境で実行し、848件すべて成功。独立にインストールした環境で ITAMAE distribution/import が存在しないことを確認した。最初の環境記録は作業ディレクトリ内の同名 namespace を誤検出していたため、`python -I` による記録へ訂正した。

| 受入要件 | 確認した証拠 |
| --- | --- |
| 独立精度と参照収束 | 対数質量 DOP853 1e-11/1e-12 と 3e-13/3e-14、質量誤差 gate 1e-3、参照差 gate 1e-8 を全系統で通過。SI は全時点 |
| 支持域 | host 1e8/1e12/1e15、zobs 0/0.5/2、降着境界、log10 mass ratio -24〜+3。W の無効な native host は失敗記録を保持 |
| 反復と解像度 | 2/3/4回と複数格子の初期試験を保存。最終3回＋第4回の収束評価、endpoint 48×32×129、SI 全履歴で gate を通過 |
| 同じ修正版の catalog | 質量関数、N_sat、生存 bound mass fraction、Vmax、利用可能な n=0 boost、SI core/collapse。smooth 集計の最大相対差は各系統とも1%未満 |
| 境界 | pilot 前の絶対誤差基準、変化 node と weight、最寄りの正 weight node、solver/格子 refinement を保存。比較対象で survival/collapse mask 変更0 |
| cache/API | host・背景・粒子・観測赤方偏移・数値設定の識別と無効化、scalar/array/empty、無進化、旧 positional 引数、default と明示 Picard の公開入口一致 |
| fallback | 検証 envelope 外・反復未収束を warning と件数/理由で記録。代表通常 catalog の fallback は0 |
| 性能 | 同じ host/環境、solver ごと3個の新規プロセス、構築/初回/再利用/全 catalog/peak RSS を分離。全系統で凍結 speedup gate 1.05x を通過 |
| 処方と solver の分離 | A main → 修正済み旧 solver → 同一修正版 Picard の三段階配列と集計 |
| 旧例・レビュー | 元 notebook の import/tuple/observable を保った縮小格子実行、API/差分/入力 hash の自己レビュー、4 draft PR と CI |

各 repo の `docs/standalone-maintenance.md` に再実行コマンドと制約があり、`validation/maintenance/acceptance.json` と `final-review.json` が最終根拠を指す。初期の不合格な速度測定・未分割 ODE 参照・数値試験の失敗を削除せず、最終結果と区別して保存した。

## 適用範囲と残る別課題

- 自動 Picard envelope は `0 <= zobs <= zacc <= 7` と `-24 <= log10(ma/Mvir) <= 3`。必要な範囲へ表を構築し、域外や未収束は記録付き直接 ODE に進む。真の native 物理域外はエラーを保持する。
- W の 2 keV / host 1e8 Msun は要求赤方偏移内で既存の host/concentration が成立しない。小 host と0.5 keV の参照失敗も保存した。係数や mass definition を変えて通してはいない。独立参照では既存の濃度探索の不連続境界を明示分割した。
- 数値ゲートは有限個の入力に対する結果であり、任意の物理条件での保証や simulation 較正ではない。速度は明示した代表格子の測定であり、公開 default の全解像度の性能値ではない。
- 旧 notebook は縮小格子で実行した。C の recursive boost table 再生成は除外し、n=0 を確認した。F の既存 explicit Colossus と CDM sentinel は実行したが、cutoff 以下での backend 同等性は主張しない。
- C の従来 NFW/EPS の横展開、新しい物理、下流 prior/likelihood、観測制約、recursive-boost 較正は計画どおり別課題。F の旧保存結果を新しい結果として認証しない。
- main 統合後の migration 対応表更新は、将来 main merge が承認・実行された時点の作業とする。今回の draft PR の作成は merge/release の実行を含まない。
