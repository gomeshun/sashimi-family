# SASHIMI main 保守計画：既知バグ修正と Picard 既定化

2026-09-11。ユーザー承認済みの実装計画（minor-updates への実装・検証・push 完了）。対象は各 `gomeshun/sashimi-{c,si,w,f}` の `main`。
共通 ITAMAE への migration とは独立した保守作業であり、migration の実行計画は引き続き
[sashimi-migration-goal.md](../sashimi-migration-goal.md) を正とする。
計画時の調査記録を以下に保持する。実装結果・最終 SHA・受入証拠は
[完了報告](main-maintenance-results-20260911.md) を参照。main と migration の gitlink は変更していない。

## 1. 方針と確認した基準

**既存 API を保ったバグ修正を旧 solver で検証し、その修正版に Picard を追加してから既定化する。**
バグ修正・数値 solver・依存ライブラリの積分規則の差を、一括変更の差として扱わない。
ここで Picard 化するのは潮汐質量損失 ODE であり、power/variance、EPS、SIDM の各積分を
すべて同じアルゴリズムへ置換する計画ではない。

以下の SHA は当日の `git ls-remote origin refs/heads/main` とローカル Git object を照合した。
現在の作業ツリーは別作業による migration/package-layout 改訂中なので、調査は
`git show <main SHA>:<file>` で取り出したソースに対して行った。

| Repo | 調査対象 main | 潮汐質量損失の現状 |
| --- | --- | --- |
| C | `e09571be7a1daaef343e97887e34449faf21db7b` | Picard の独立モジュールは存在するが、標準 solver dispatcher には未接続。既定は `pert2_shanks` |
| SI | `e17d3664dac677b604fd4ff02fb2af105a6937fa` | 既定は `pert2_shanks`。SIDM 計算には降着後の100時点の質量履歴が必要 |
| W | `99dfc3632eec0126080c0273ddf78f84fe09216c` | `rs_rhos_calc` 内の直接 `odeint`。公開 `method` 選択肢なし |
| F | `68d617e94d254054cf65bb9a92d6200fe1582dd8` | 既定は `pert2_shanks`。F 固有の背景・host history に接続 |

C の [既定化 PR #5](https://github.com/gomeshun/sashimi-c/pull/5) は当日確認で OPEN、
head `88ae730762fb153be7a7433bb563b0b8ab3ec2c2`、base `main`。
当該 head の既存 pytest CI は成功している。重複 PR を新設する前に、この提案を再利用する。
PR の既存誤差・速度報告はその入力・SHA・環境に限定された証拠であり、今回の再測定結果ではない。

## 2. 変更の境界

- `main` から repo ごとの `minor-updates` 作業ブランチと別 worktree を作る。既存の dirty な migration 作業ツリーを切り替えない。
- 旧クラス・関数名、tuple の順序・単位、従来の positional 引数を維持する。solver 用の追加引数は既存引数の末尾に追加する。
- ITAMAE 依存、named catalog への移行、`src/` への再配置、package/release 全面改訂を持ち込まない。
- migration の修正を使う場合は必要な式・数値 helper・試験だけを移植する。pipeline や backend の大きな commit をそのまま cherry-pick しない。
- 修正済み仕様を通常経路にする。旧バグは凍結ソースと出力で再現し、新しい通常 API に旧物理モードを増設しない。旧 solver の明示指定は維持する。
- 既存の宇宙論、物理係数、閾値、filter、mass definition のうち、個別の修正対象以外は固定する。丸めた重力定数の統一など、migration 由来の全数値変更との一致を今回の要件にしない。
- 実装・検証・`minor-updates` への push は承認済み。main 統合と公開は今回実行しない。

## 3. 各 variant のバグ修正

### SI：上流修正済みの問題を除外し、数値安定性と残る API バグを直す

現在の main は `1c6d13b` を含む。以下は修正済みなので再実装しない。

- integral approach で実行時刻の CDM 履歴を使う規格化。
- 速度多項式の係数 `9.044 → 9.077` とその微分。
- 診断用 collapse time と進化本体の effective cross section の統一。
- `dDdz` に混入していた余分な `h^-2`。

| 修正単位 | main に残る問題と変更 | 必須検証 |
| --- | --- | --- |
| SI-1 全断面積 | `sigma_total` の分母が二乗。既存の微分断面積の角度積分と一致する一乗へ修正 | 公開 differential API の独立角度積分、低速規格化・高速漸近、配列入力。effective/viscosity cross section とカタログは変化しないこと |
| SI-2 有効断面積の安定評価 | 捨てる分岐でも `exp(a)` を評価して overflow。大きな有限 `a` では差し引きによる桁落ち | 有効分岐だけを評価し、中間域は同値な正の積分、既存の大きな `a` の漸近式は維持。高精度参照、分岐境界、弱/強相互作用の比較 |
| SI-3 EPS 支持域と極限 | `Heaviside` を掛ける前に不正な割算を行い、`nan_to_num` で失敗を隠す。barrier gap が0の正規化には有限極限がある | `Na_model=1/2/3`、支持域外、zero-gap、host quadrature 1/64/200。支持域内の真の異常は明示エラー |
| SI-4 単一 host node の shape | `Na_calc` が2次元の降着質量を受けるのに、`N_herm=1` 分岐で `len(ma)` を質量軸長として reshape | 赤方偏移数と質量点数が異なる例。出力が `(Nz, Nm)` で各 node と対応すること |
| SI-5 未形成 node | 最終 weight の形成条件は main に存在するが、除外される node の逆向き履歴を先に計算して NaN を生む | 未形成 node を進化させず、有効 node の配列・weight は保持。除外出力の有限な placeholder と mask の意味を明記 |
| SI-6 NFW 逆関数 | 1000点の補間逆関数の誤差が truncation 境界へ伝播 | 単調な正確な数値逆関数と独立高精度逆関数を比較。閾値の両側、零入力、mask の変化を検証 |

SI-1 は [採用記録](https://github.com/gomeshun/sashimi-family/blob/7ce00a72f7da4b113261cd255eb85eda0fb6c453/docs/adoption-2026-09-10.md) に承認済みの式を使う。
SI-2〜5 は [有効断面積](https://github.com/gomeshun/sashimi-si/blob/ce5a3c11518a609ac056bb136653268b05b1ecd7/docs/effective-cross-section-accuracy.md)、
[形成境界](https://github.com/gomeshun/sashimi-si/blob/ce5a3c11518a609ac056bb136653268b05b1ecd7/docs/formation-validity.md)、
[EPS 極限](https://github.com/gomeshun/sashimi-si/blob/ce5a3c11518a609ac056bb136653268b05b1ecd7/docs/eps-normalization-limit.md) と独立 B patch を利用する。
ただし「shared executor が formation/CDM survival gate を落としていた問題」と
「canonical velocity の段階境界」は migration 固有であり、main のバグとしては計上しない。

### W：数値基盤、観測量集計、power の訂正を分ける

| 修正単位 | main に残る問題と変更 | 必須検証 |
| --- | --- | --- |
| W-0 実行互換性 | `np.alen`、`integrate.simps` の利用。新しい依存環境で実計算できない | 旧依存の A を保存。`len` 置換と積分 API 対応を分離し、偶数標本の Simpson 端点規則による差を明示 |
| W-1 背景・成長因子 | `OmegaL` が baryon を除いた密度から作られ、平坦性が崩れる。growth の規格化も整合させる | `OmegaM+OmegaL=1`、`H(0)=H0`、`D(0)=1`、`dDdz` と有限差分。一つずつの効果と組合せを保存 |
| W-2 質量単位・成長次数 | variance 表の `Msun/h` 数値座標に physical mass を直接渡す。濃度側の `h` 変換が逆。`dS/dM` に `D` 一乗しか掛けない | physical mass から表への変換、連鎖律、`dS/dM(M,z)=D(z)^2 dS/dM(M,0)`、scalar/array |
| W-3 分散と微分 | 粗い100質量点と移動する積分格子で、評価する `S` と微分が不整合。単位だけ直しても負 weight が残る参照例がある | 同じ sharp-k 積分と moving-boundary derivative を使う。入力 spectrum の補間節点を解像した独立積分・有限差分。projection/clipping で符号を直さない |
| W-4 降着質量 | 最後の赤方偏移の virial mass を全赤方偏移の EPS と質量積分に再利用 | 各赤方偏移で初期構造・進化に使う質量と EPS 入力・対数積分座標を一致。`zmax` 延長で既存 node の局所降着率が変わらないこと |
| W-5 濃度・NFW 境界 | 濃度探索で無効な分数乗を先に計算。truncation は粗い NFW 逆補間 | 有効な候補だけを評価。既存の有限な future-redshift 候補を保つ。NFW 閾値両側を確認 |
| W-6 生存する集団の集計 | `subhalo_distr` / `N_sat` / `N_sat_Vthres` が survival を無視。累積総数が最初の bin を落とす。`profile_change=True` を強制 | weight `[2,3,5]` の中央が破壊された例で総数7、全破壊で0。厳密な threshold 等号、空/単一要素、両 mass 表示、引数転送 |
| W-7 power の二乗 | 現行 Viel 係数では伝達振幅を power に一回しか掛けない q5 を使用 | 承認済み q10 を sharp-k と濃度用 top-hat の双方に適用。同じ係数・WMAP7 を保持。0.5/2/5 keV で power→variance→濃度→catalog を比較 |

W-7 は [q10 採用記録](https://github.com/gomeshun/sashimi-family/blob/7ce00a72f7da4b113261cd255eb85eda0fb6c453/docs/adoption-2026-09-10.md) を main に反映する独立の科学的訂正。
amplitude-half と power-half を区別し、Vogel 係数への更新・新しい宇宙論・観測限界の換算は含めない。
W-6 の `accretion=True` は「現在生存している集団を降着質量で表示」の合意を維持する。
累積数は選択された個別 node の厳密な `>` で評価し、総数を表示 bin から逆算しない。

W-0 の推奨最終仕様は migration と同じ現行 `simpson` 端点規則。ただし単なる名称置換として
bitwise 一致を要求せず、[独立参照の quadrature patch](https://github.com/gomeshun/sashimi-family/blob/7ce00a72f7da4b113261cd255eb85eda0fb6c453/validation/references/sashimi-w/patches/10-even-sample-quadrature.patch)
によって差を一つの変更として記録する。依存バージョンはその仕様を満たす範囲で固定する。
W-1〜5 の参照は [独立 correction ablations](https://github.com/gomeshun/sashimi-family/blob/7ce00a72f7da4b113261cd255eb85eda0fb6c453/validation/references/sashimi-w/README.md)。
そこに残る q10「未採用」の文章は歴史的状態であり、新しい採用記録が優先する。

### F：微分、mutable variance、降着時点の不一致を直す

| 修正単位 | main に残る問題と変更 | 必須検証 |
| --- | --- | --- |
| F-1 growth と微分 | `dDdz` の余分な `h^-2`、native `dS/dM` の成長因子が一乗 | `growthD` の有限差分、`D²` 恒等式、host history と weight の単独比較 |
| F-2 top-hat 分散 | sigma は質量補間、微分は直接積分。範囲外 query が表を再構築して後続結果を変える | 既存 native spectrum/window の直接積分で統一。query 順序・範囲外 query 挿入・cold/warm cache・有限差分・全 catalog |
| F-3 降着質量 grid | W と同じ最終赤方偏移の配列再利用 | EPS と各行の対数質量積分の双方を修正。m22=0.1/1/10、局所降着率の不変性、構造配列と重みへの効果を別々に確認 |
| F-4 NFW・EPS の数値境界 | 粗い NFW 逆関数と、EPS の除外域/正規化境界の不正計算 | 高精度 inverse、`ct_th=0.77` 両側、EPS 各モデルの支持域と極限、有効領域内の異常検出 |
| F-5 保存結果の識別 | 修正前後の prior/boost/cache 出力を同一視すると旧結果が再利用される | main に存在する各保存・再利用入口を棚卸し。solver、計算仕様、入力条件の識別を追加し、旧ファイルを誤認しない試験 |

F-2/F-3 の科学的選択は [採用記録](https://github.com/gomeshun/sashimi-family/blob/7ce00a72f7da4b113261cd255eb85eda0fb6c453/docs/adoption-2026-09-10.md) に解決済み。
根拠と独立参照は private F 内の [direct top-hat](https://github.com/gomeshun/sashimi-f/blob/4a258f389de488b3d35661780318687d11677718/docs/direct-top-hat.md)、
[redshift grid](https://github.com/gomeshun/sashimi-f/blob/4a258f389de488b3d35661780318687d11677718/docs/accretion-redshift-grid.md)、
[reference 索引](https://github.com/gomeshun/sashimi-f/blob/4a258f389de488b3d35661780318687d11677718/validation/references/README.md) を用いる。
F-2 では旧 cache-control helper を直ちに削除する migration の API 変更まで移植せず、
main の既存呼出しに対する互換性を保つ wrapper/deprecation 方針を実装時に明記する。
Colossus の cutoff 以下での不一致、新 soliton、下流 prior/likelihood の再計算は別課題。
private source・生 catalog・入力データは private F に置いたまま検証する。

## 4. 全 variant の Picard 導入と既定化

### 実装の単位

| Repo | 導入方法 | 固有の注意点 |
| --- | --- | --- |
| C | PR #5 を基礎に、既存独立テーブルを dispatcher・catalog・observable に接続。`method="picard_table"` を既定化 | main の既存表は mass-ratio 下限 -20 / 96点。PR は -24 / 128点への拡張も含む。単なる default 文字列変更ではない |
| F | 同じ Picard 数値手順を standalone helper として同梱し、F の solver に接続。終点テーブルを再利用 | Planck 背景、FDM mass、host history は F が供給。C の背景や係数をコピーしない |
| W | 既存クロージャの `Mzvir/A/zeta/tdyn/H` を保持した薄い solver 接続と終点テーブルを追加 | W の A・zeta は C/SI/F と異なる。公開各入口から `method` を転送し、明示 `odeint` を維持。host の高価な計算も含め測定 |
| SI | 共通の Picard 更新式を、全時系列を返す vectorized history solver に拡張。推奨名は `method="picard"` | `(Ntime,Nmass)` 履歴が必須。固定終点用テーブルを100個作る設計は避け、各降着 slice の要求時系列を一度に積分。SIDM 時間積分は既存のまま |

SI は補間テーブル方式と計算法を混同しない名前を使う。C/W/F は既存 C の
`picard_table` 名を利用する。family 全体の API 命名統一は migration 側の別課題。
helper の由来 SHA と parity test を各 repo に残し、他 variant や ITAMAE の import を
通常実行時に必要としない。新しい共通配布パッケージは作らない。

初期候補は C で実績のある3回 Picard 更新。SI/W/F に同じ3回で十分とは仮定せず、
2/3/4回と積分・補間解像度を比較する。計算能力の向上を理由に物理係数を変えない。

### キャッシュ・境界・互換性

- cache は solver/host ごとに所有し、観測赤方偏移、表の範囲・解像度・反復数を識別する。host mass、背景、粒子質量、host-history 設定の変更時に無効化する。
- 既存の有効な入力領域を先に採取する。固定した mass-ratio 範囲に入ると仮定せず、必要な範囲を覆う表を構築し、範囲外を無言で外挿しない。
- 検証済み領域外や未収束には、明示的に記録する直接 ODE への fallback を推奨する。件数・理由も性能報告に含める。真に無効な入力はエラーとする。
- `ma > 0`、有限値、時間方向、`z_acc=z_obs` の無進化、scalar/array/empty、SI の全履歴 shape を検証する。
- C/SI/F の従来 solver と W の `odeint` は明示指定で使えるようにする。solver 専用 kwargs を黙って捨てない。
- default 未指定と明示 Picard の一致を、solver 単体だけでなく各公開 catalog/observable から確認する。

### 既定化の受入基準案

1. **独立精度基準**：対数質量を DOP853 で解き、初期参照許容誤差は `rtol=1e-11, atol=1e-12`。さらに厳しい参照との一致を確認する。支持域での質量最大相対誤差 `1e-3` 以下を初期 gate とする。SI は終点だけでなく全時点に適用する。
2. **領域**：host mass は少なくとも `1e8/1e12/1e15 Msun`、観測赤方偏移は `0/0.5/2`、降着赤方偏移は通常域と境界、mass ratio は実際の既存 default catalog 全域を覆う。各 variant の対応域を超えるモデルを無理に実行せず、対象域を先に固定する。
3. **カタログ**：同じ修正版・同じ格子で Picard と高精度 ODE を比較する。質量関数、N_sat、bound mass fraction、Vmax、検証可能な boost、SI の core/collapse 指標を含める。滑らかな主要集計量の相対差 `1%` 以下を初期目標とし、これは検証結果や物理較正精度の主張ではない。
4. **境界**：survival/collapse 近傍は相対誤差一つで判定しない。mask が変わる node とその weight を列挙し、格子・solver refinement で位置を追う。ゼロ近傍の絶対誤差基準は pilot の結果を見る前に量と単位ごとに固定する。未説明の差を tolerance 拡大で通さない。
5. **性能**：表構築・一回目・再利用・全 catalog wall time・peak memory を分離する。同一環境で複数回測定し、代表的な通常 catalog で旧 default より実用的な高速化が確認できること。lookup 単独の高速化だけで既定化を完了扱いにしない。
6. **処方と solver の分離**：旧 main → 修正済み旧 solver → 同じ修正版の Picard の三段階を保存する。q10 や F の分散修正による差を Picard 誤差と取り違えない。

C PR #5 の既存45点検証では x3 の最大相対誤差 `4.36e-4`、cluster/microhalo 例では
`1.90e-4` と報告されている。これは C の初期設計根拠として使い、SI/W/F の精度保証には使わない。
閾値未達なら数値解像度・反復・領域処理を改善し、受入前の版では旧 default を維持する。

## 5. PR の順序と完了条件

1. **基準保存**：最新 main を再確認し、既存例の小さな A catalog、全配列、依存、入力 table hash、warning を保存。C は migration の旧 A と main が異なるため、今回の main 基準を別に作る。
2. **局所修正**：SI-1/2、F-1/3、W-6 のように独立に説明できる単位から着手。各問題を再現する試験が修正前に失敗し、修正後に通ることを確認する。
3. **数値基盤の修正**：SI の EPS/形成域、W-0〜5、F-2/4 を、上表の小さな commit/PR に分ける。W の単位修正だけを完成版として扱わず、variance closure まで確認する。
4. **仕様と参照**：W-7、F の保存結果識別を反映。独立 B の生成器を利用し、既存 main API の修正版を別プロセスで検証する。migration 固有の単位・定数・積分仕様の差は明示してから比較する。
5. **Picard**：C の既存 PR を再点検して第一例にする。F/W の終点計算、SI の全履歴へ展開する。各 repo で追加・精度/性能検証・default 変更を分け、上記 gate を通す。
6. **利用例とレビュー**：旧 import/tuple を使う各 main の notebook/example を実行。修正効果と solver 差、適用領域・制約を記した PR を揃えてレビューする。

各修正の成果物は「再現例・最小 patch・独立参照との差・固定入力での物理量の変化・対象 SHA」。
参照の既存 tolerance は同一仕様の比較に限り保持し、仕様の違う migration と main の差を
無理にゼロへ揃えない。修正前の出力、失敗結果、cache identity は保存する。
実装が main に入った後、migration 側へ同じ修正の対応表を反映し、将来の統合で逆戻りしないことを確認する。

## 6. 今回の中心範囲に混ぜないもの

- SI で既に main 修正済みの4問題、および migration executor の gate・canonical unit 修正。
- W の Vogel 係数/新宇宙論、F の新物理・backend の同等性認定、下流推論キャンペーン。
- C にも main の NFW 逆補間と EPS 境界の同種の問題が残る。今回の指定では C は Picard を中心とし、これらの C への横展開は追加の小さな保守単位として提案する。Picard PR には混ぜない。
- 計算速度・回帰・数値収束の成功を simulation 較正や observational constraint の更新と扱うこと。

## 調査に使った main の位置

以下の行番号は作業ツリーではなく、節1の固定 Git object に対する位置。

- C：`sashimi_c.py:582`（dispatcher）、`picard_tidal_stripping.py:53`（表の既定構成）、PR #5。
- SI：`sashimi_si.py:253`（全断面積）、`:334`（有効断面積）、`:1166`（EPS）、`:1468`（全質量履歴）、`:1519`（main に既存の形成・CDM gate）。
- W：`sashimi_w.py:56`（背景）、`:121`（粗い分散微分）、`:185`（濃度）、`:341`/`:394`（variance）、`:466`（catalog）、`:512`（W 係数）、`:585`以降（observable）。
- F：`sashimi_f.py:137`（growth 微分）、`:467`/`:536`/`:748`（variance）、`:1377`（降着率と積分）。

上記は計画時の調査記録。承認後に三段階カタログ、独立参照、benchmark、境界/格子試験と CI を実行し、[完了報告](main-maintenance-results-20260911.md) に結果を保存した。
