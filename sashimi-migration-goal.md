# SASHIMI migration・リリース準備の開発 goal

更新（2026-09-11）：ユーザーから受領した独立調査に基づき、現行Viel係数の熱的WDMはq10へ統一し、q5を通常APIから廃止する。以下に残るq5/q10両選択肢の維持要件は、この追加判断で置き換える。旧q5の固定参照は保持し、旧指定・キャッシュを黙ってq10へ読み替えない。係数・宇宙論・他の処方や観測制限は同時変更しない。[採用記録](docs/adoption-2026-09-10.md)を参照。

合意日：2026-09-10。以下は実装担当の agent に渡す開発プロンプトである。

この文書は、旧実装計画と開発プロンプトを統合した、migration・リリース準備の唯一の実行計画である。README、[golden fixture policy](docs/golden-fixture-policy.md)、関連 Issue/PR に残る旧方針と矛盾する場合は、この文書を優先して関連記述を更新する。互換性確認済みの revision 集合は引き続き [compatibility.toml](compatibility.toml) を正とし、計画内に別の恒久的な revision 集合を作らない。[2026-09-04 の監査](docs/migration-status-2026-09-04.md) は歴史的記録、[科学開発ロードマップ](docs/scientific-roadmap.md) は今回の対象外の新機能を扱う。

## 1. 目的と到達点

このリポジトリで管理している SASHIMI ファミリーの ITAMAE migration を完了し、ITAMAE と SASHIMI-C/SI/W/F を公開 PyPI リリースに向けてピアレビューできる状態まで準備してください。

調査や計画作成だけで終了せず、実装、科学的検証、文書整備、配布物の検証、レビュー資料の作成まで進めてください。今回の goal は **「migration ブランチ上でのリリース準備完了・ピアレビュー待ち」** です。main 統合と公開はレビュー後の別工程として残し、この段階で停止してください。

- ITAMAE は共通の数値計算・単位・宇宙論 backend・実行機構・カタログ契約・provenance を担当する。
- 各 SASHIMI は CDM/SIDM/WDM/FDM 固有の物理処方とモデル構成を担当する。
- 各 variant は共通実行系を利用し、共有できる数値計算や実行制御の重複を解消する。
- migration 前に提供していた物理量を、新しい公開 API から計算できるようにする。
- 将来の公開対象は `sashimi-itamae`、`sashimi-c`、`sashimi-si`、`sashimi-w`、`sashimi-f` とする。ITAMAE の import 名は `itamae` を維持する。
- SASHIMI-F も公開予定に含め、canonical source、著作権表示、ライセンス、同梱データの配布条件を整理する。権利や公開条件を推測で決めず、必要事項はユーザーに確認する。

新しい位置分布、位相空間、軌道モデル、FDM soliton/core-halo relation、バリオン効果などは今回の完了条件に含めず、後続の科学開発として管理する。既存機能の維持に必要な状態・profile 契約は今回の対象とする。

## 2. 最新状態と作業ブランチの確認

親リポジトリと各 submodule の作業状態・ブランチ・リモートを確認し、既存の未コミット変更や進行中の作業を保護する。最新のリモート情報を取得し、計画・実装・Issue・CI の食い違いを整理する。

以下を読む。

- この文書、親の README、compatibility.toml、golden fixture policy
- [親 migration Epic #1](https://github.com/gomeshun/sashimi-family/issues/1) と関連 Issue/PR
- ITAMAE の README、PLAN.md、実行系・protocol・provenance
- 各 variant の itamae-migration ブランチ、公開 API、テスト、notebook、packaging、CI

### 作業先と権限

- 各 ITAMAE/SASHIMI の実装変更は `itamae-migration`、またはそこから派生した小さな作業ブランチで行う。子 PR の統合先も `itamae-migration` とする。
- 親 `sashimi-family` の計画・manifest・gitlink・CI の変更も、main から分岐した migration 用の作業ブランチで管理する。親 main は合意済み計画と互換性管理の共有先であり、各 variant の実装作業先とは区別する。
- 作業ブランチでの commit・push、PR 作成・更新、検証済み子 PR の migration ブランチへの統合は自律的に進めてよい。
- **main への直接 push、main を統合先とする PR のマージ、main 向け自動マージの予約・有効化は行わない。** main 統合はピアレビュー後の明示的な指示を待つ。
- ブランチを誤認したまま pull・編集・push しない。force push や既存作業を失わせる操作で状態を揃えない。

今回ユーザーが明示的に依頼した、この統合文書と関連参照の親 `sashimi-family` main への commit・push は許可されている。この文書化の許可を、将来の実装・互換性候補の main 統合や各 submodule の main 更新への包括的な許可として扱わない。

親 manifest に記録された互換性確認済みの組合せと、各 migration ブランチの最新候補を区別する。submodule を無条件に最新 head へ進めない。候補の組合せは作業ブランチで明示して検証し、main の manifest を先に変更する循環を作らない。

### 過去の調査メモ

2026-09-10 の調査では次の状態だった。これは着手時の確認用であり、完了状態や最新 revision を保証するものではない。

- 親 main は `3d9f6bc`。親 main では計画・互換性管理が進み、各 variant の migration 実装は `itamae-migration` で進んでいた。
- 配布名を `sashimi-itamae` に変更済み。F の CI 循環、子 PR の CI、family manifest の一本化、usage walkthrough は対応済み。
- ITAMAE は PopulationPipeline に加えて PopulationComponents と段階別 protocol を導入済み。実行系の堅牢化は未完了。
- C/SI は pipeline 接続済み。C は survival component の抽出だけが進み、他の段階の分解は残っていた。
- C の Picard 同期は完了し、default は `pert2_shanks` のまま。
- W/F は共通 pipeline への実行接続が未完了。
- C の最新変更を親 manifest へ昇格する親 PR #33 は未マージ。この goal はその main 向け PR のマージを許可しない。
- F の最新 head と親 pin に CI 設定の差があった。
- F の旧 API にある `fdm_subhalo_observables` は、移行用 facade に公開されていなかった。
- 公開 family CI の対象は ITAMAE/C/SI/W。F を含む全5パッケージの検証範囲を別途確認する必要がある。

完了済みの課題を再実装せず、既存 Issue の実際の残作業を更新して進める。

### 候補検証と manifest 更新の契約

既存の仕組みを維持・補強し、次の3種類の結果を区別する。

1. **Component regression**：候補 component と、その component が宣言する正確な ITAMAE 入力で回帰試験を行う。親への昇格を前提にしない。
2. **Candidate family**：親の基準 commit と manifest/gitlink の一致を確認し、一時的な effective manifest で検証対象だけを候補 SHA に置き換える。協調変更はすべての override を列挙する。基準親 SHA、effective manifest、全 artifact の SHA を保存する。一時 override を未更新の親 gitlink と比較して失敗させない。
3. **Recorded family candidate**：全組合せの検証後、親の作業ブランチで manifest と gitlink を同じ commit に記録し、override なしで検証する。main 上の組合せへの昇格は別途指示を待つ。

- PR head と GitHub の synthetic merge SHA のどちらを試験するか job ごとに明記し、checkout・build・provenance・assertion を同じ SHA に揃える。
- 新候補が古い親 pin と一致することを要求しない。component-local の ITAMAE build pin と不変の fixture 生成元は、family の恒久的な互換性集合とは役割が違うので一律に削除しない。
- 各 job が利用する ITAMAE のソースは一つとする。同じ package を異なる local/VCS URL から重複要求しない。
- private F を含む検証は、利用権限のある private CI 等で全5パッケージを実行する。公開側だけの成功や、別の親 SHA を使った過去の F 成功を流用しない。
- `scripts/check_compatibility.py` は committed HEAD の gitlink を読む。候補 manifest と gitlink の commit 後に実行し、作業ツリー上の manifest 編集だけで検証済みとしない。
- main と migration ブランチの双方の差分を確認する。main の変更を migration 側へ取り込む場合も参照 SHA・solver・threshold を保存し、テキスト上の merge 成功に加えて数値検証を行う。

## 3. legacy を製品から除去する

製品内の legacy 再現用計算経路を廃止し、旧版の再現性を独立した検証コード・ワークフローで維持する。

- 製品 API の `physics_mode="legacy"|"consistent"` を廃止する。
- 検証済みの計算仕様を製品の標準経路とする。
- 新 API を標準の `sashimi_c` / `sashimi_si` / `sashimi_w` / `sashimi_f` import から利用できるようにする。
- 名前付き WeightedSubhaloCatalog を基本とし、SI の `cdm_reference` / `sidm` などの状態を保持する。
- 旧 tuple への対応は必要最小限の形式変換に限定し、旧計算を実行する裏口を残さない。
- 旧クラスから必要な物理処方・observable を移し、継承や `super()` 経由の依存を解消してから旧計算コードを除去する。
- API と数値結果の変更は破壊的変更として明示し、対応する版管理と移行案内を整備する。

宇宙論、物理処方、solver、分散 backend など、科学的意味のある選択は明示的に保持する。legacy 廃止に便乗して物理 default を変更しない。W の q5/q10 は独立した明示指定を維持し、C の Picard default 化も別の科学的・数値的検証事項として扱う。

各 variant の文書や関連 Issue に残る「製品内 legacy 維持」を要求する記述は、この方針に合わせて明示的に改訂する。

## 4. 旧版との consistency と科学的妥当性を別々に検証する

次の3対象を用いる独立した比較ワークフローを構築する。

### A. 凍結した旧実装

- 再現対象となる repository、SHA、依存環境、入力データを固定する。
- variant ごとに「どの旧版を再現するのか」を明記する。
- 同じ checkout 内の変更され続ける旧モジュールだけを参照基準にしない。
- 再現対象に複数の候補があり科学的意味が異なる場合は、ユーザーに確認する。

### B. 検証専用の修正参照

- A に個々の修正を適用する小さな patch として管理する。
- 修正の式、理由、出典、影響する物理量を記録する。
- 製品から import せず、通常の配布物の実行依存にしない。

### C. 新しい製品実装

- 採用する計算仕様を実装する。
- A/B と別環境・別プロセスで実行して比較する。

### 比較の役割と受入規則

- A と B：修正による科学的・数値的変化を一要因ずつ測る。
- B と C：同じ計算仕様・条件に揃えた migration の一致を検証する。
- 変更のない計算では A と C を直接比較する。

宇宙論、単位、質量定義、入力スペクトル、数値グリッド、solver、seed と比較規則を固定し、許容誤差には根拠を付ける。修正を束ねた最終比較に加えて、各修正の独立した効果を記録する。

現行 consistent を名称だけで正しいと認定しない。比較の一致に加えて、解析式、独立した数値積分・微分、既知の極限、収束性、関連する一次資料で検証する。修正参照と製品で同じ誤りを共有する可能性にも注意する。

原因不明の差分を許容誤差の拡大や golden の上書きで通さない。負の重みの clipping、絶対値化、無断の再規格化で問題を隠さない。

科学的解釈や採用方針に確認が必要な場合は、比較結果と選択肢を整理してユーザーに尋ね、回答を得るまでその判断に依存する変更を確定しない。

### Fixture と provenance の保存規則

- 小さな全カタログと代表的 observable を fixture にし、生成 repository/SHA、ITAMAE SHA（使用時）、A/B/C の役割、B の patch 識別子、constructor・計算パラメータ、宇宙論、単位、用途、許容誤差と根拠を記録する。
- 既存 fixture の生成元を新しい検証 SHA で上書きしない。生成と再検証の履歴を別に記録する。
- 既存の `physics_modes` / `mode_policy` は過去の計算を識別する記録として保全する。新仕様の fixture/metadata は必要な schema 更新を行い、過去の legacy 値を新しい仕様へ付け替えない。
- 旧 tuple の列順序、単位、選択 mask、重みの意味を名前付き出力へ対応付ける。形式変換で無言の並べ替えや単位変更を行わない。
- scalar/array、単位変換、重み因子、有限性・非負性、serialization round trip、ソースツリー外での利用を含める。高解像度の収束計算は小規模 PR 試験から分離してよいが、準備完了までに実行証拠を揃える。

## 5. 既存物理量の機能維持を確認する

カタログ生成だけで migration 完了とせず、旧実装の API・文書・実行例から機能一覧を作成し、新 API とテストへ対応付ける。最低限、次を含める。

| Variant | 維持する計算機能 |
| --- | --- |
| C | 降着時・進化後の構造量、質量関数、累積衛星数、質量比、消滅ブースト、既存 prompt-cusp 計算、MC カタログ |
| SI | CDM/SIDM の構造量・重み・生存状態、既存の断面積・gravothermal/profile 計算 |
| W | WDM 構造量、質量分布、質量・速度閾値による衛星数 |
| F | FDM 構造量、質量関数、累積衛星数、質量比、消滅ブースト、MC カタログ |

必要な入力表、前計算、補助スクリプトも追跡し、ソース checkout に依存せず配布後に利用できるようにする。既存機能の欠落を発見した場合は、黙って対象外にせず準備完了までに解消する。対象範囲の変更が必要ならユーザーに確認する。

科学的検証では、SI の CDM 極限と状態境界、W の修正別効果と q5/q10、F の cutoff 近傍の微分・backend 差、C の既存 prompt-cusp と solver 経路を含める。

## 6. 共通実行系・metadata・cache を仕上げる

ITAMAE の PopulationPipeline / PopulationComponents を利用し、初期化、進化、生存判定、列生成を variant 所有の component として構成する。

- C の残る段階を分解し、SI、W、F に適用する。
- 共通の段階実行、検証、重み輸送、結合、診断は ITAMAE に集約する。
- 降着モデル、濃度関係、質量損失・profile・生存の物理処方は各 variant に保持する。
- 一つの variant に特有の前提を共通機構へ持ち込まない。
- metadata 不一致、shape、非有限値、空結果、異常系、分割実行を検証する。

新成果物には計算仕様の版、選択した処方、宇宙論、backend、単位、source revision を記録する。旧成果物の physics_mode は履歴として保持し、修正版として読み替えない。metadata と cache の識別を更新し、旧仕様の cache を誤って再利用しない。

### 6.1 責務・単位・状態・重み

計算の流れは `host → host history → accretion measure → EPS/accretion → concentration quadrature → initial structure → evolution → survival → weighted catalog → observables` とし、共通 controller と variant の処方を分ける。

既存の Protocol と component を優先して使う。HostHistoryModel、VarianceModel、AccretionRateModel、ConcentrationModel、InitialStructureModel、MassLossLaw、ProfileEvolutionModel、SurvivalModel に相当する責務を明示し、便利さのために C の式を ITAMAE の隠れた default にしない。汎用機構には SASHIMI 非依存の unit test と toy model の integration test を設ける。

- backend 設定は明示的または不変とする。Colossus 等の可変 global state は復元・隔離し、import や計算順序に結果を依存させない。
- 乱数 API は明示的な `numpy.random.Generator` または seed を受け取り、並列実行でも再現性・順序の契約を保持する。
- ITAMAE 境界の canonical units、physical/comoving、`h` の因子、質量定義、shape/broadcast、入力範囲、補間・外挿規則を文書化する。旧浮動単位と canonical 値を同じ配列で混在させない。
- `weight_base`、`weight_host_history`、`weight_concentration`、`weight_survival` などの独立因子を保持し、最終重みを検証する。`weight_orbit` は実際に適用する場合に限り意味を定義し、今回 orbit 機能を追加する理由にしない。
- SI の状態間で初期 node identity と base weight を対応付け、状態固有の survival/validity と追加列を維持する。将来の profile がすべて NFW 派生であると仮定する階層を作らない。

### 6.2 Power・variance・cache の共通契約

ITAMAE は安定した power identifier、tabulated spectrum の補間・外挿、variant から与える transfer function の合成、top-hat/sharp-k window、積分分散、理想 sharp-k の moving-boundary derivative、有限積分範囲の扱いを提供する。

content-addressed cache key には power 内容・filter・質量 grid・宇宙論/backend・数値解像度・計算仕様を含める。mismatch/corruption は検出して不適切な再利用を防ぎ、微分は解析解または独立した高精度参照と比較する。W の q5/q10 や F の transfer 式は variant が所有する。

### 6.3 Variant ごとの実装・科学検証要件

**C**

- 初期化・進化・列生成・降着 slice 準備の component 化を完了する。Yang 降着、host history、濃度・scatter、stripping 係数、profile response、survival、prompt-cusp 処方は C に保持する。
- 丸めた定数・臨界密度と backend に整合する定数との差を参照 A/B で隔離する。background だけ変え、host-history/concentration/EPS 係数が旧宇宙論のままの混合モデルを許可しない。未対応の宇宙論は明示的に拒否する。
- 全カタログ、質量関数、累積数、profile、消滅関連量を検証する。Picard と旧 solver の比較は default 変更から分離する。

**SI**

- 断面積、補間・漸近処理、gravothermal/profile 進化、survival は SI が所有する。既存の legacy は修正済み SI を指すため、既知の誤った修正前の式を復活させない。
- 物理定義を揃えた CDM reference と C を比較し、断面積の直接計算との一致、小相互作用極限、collapse 境界、強相互作用の代表点、重みを検証する。
- 捨てる分岐を先に計算して発生する回避可能な RuntimeWarning は、安定な分岐評価で解消する。真の無効領域・失敗を warning 抑制で隠さない。

**W**

以下の旧挙動を独立した参照で保存し、修正の効果を一つずつ検証する。

1. baryon を含めない旧 OmegaL による非平坦な和。
2. `D(0)=1` に正規化されていない成長近似。
3. `S(M,z)=D(z)^2 S(M,0)` に対して `dS/dM` に D を一つだけ掛ける旧処理。
4. `Msun/h` 数値座標の表への physical mass の入力。
5. 濃度境界での逆向きの h 変換。
6. 降着ループでの最終赤方偏移の virial-mass grid の再利用。

旧 signed weight は参照の結果として保持し、製品の非負カタログに流し込まない。q5/q10 ごとのカタログ回帰、half-mode metadata、power/variance/concentration の一貫性を確認する。half-mode mass の一致だけで二つの処方を同等としない。default 変更を提案する際は、宇宙論と質量定義を揃えた公開式・simulation・衛星数等の独立した根拠を示してユーザーに確認する。

**F**

- transfer function、filter/cutoff の処方、FDM 固有の校正、backend の科学的選択は F が所有する。現在の tidally evolved NFW という制約を明記し、新 soliton を今回の要件にしない。
- native `dS/dM` の D 対 D²、選択した growth factor と host-history derivative の整合性、旧 NFW 補間逆関数と正確な逆関数による `ct_th` 近傍の生存判定を、それぞれ検証する。
- transfer の原式、振動 node/cutoff 付近の微分・符号、native/ITAMAE/Colossus 分散、降着量を比較する。既存 structure-prior 比較を活用するが、mode をまとめて切り替えた結果を修正別検証の代用にしない。
- cutoff 以下の Colossus 微分符号差が未解決の間は実験的な明示 opt-in と provenance を維持し、native と交換可能と表示しない。下流の prior/likelihood に関係する差は影響と制約を記録し、下流 repository の変更や大規模再解析が必要ならユーザーに確認する。

## 7. リリース準備と配布物の検証

- 新 API の usage walkthrough と科学比較 notebook を分離して整備し、全セルをクリーンな環境で実行する。
- README、API 移行表、CHANGELOG、CITATION、ライセンス、release notes を整備する。
- 初期の必須対応範囲は既存 CI に合わせて Python 3.11–3.13 とする。
- 利用者向け依存関係を sashimi-itamae の予定リリース版への版依存として整備する。Git URL や開発用 checkout を必要としない構成にする。
- 未公開の依存パッケージは、固定した候補 artifact をローカル wheelhouse 等から供給して検証する。PyPI 公開済みとは扱わない。
- レビュー対象の migration ブランチの正確な SHA から wheel と sdist の両方を作り、sdist からの wheel 再構築も確認する。
- sdist の再構築は Git checkout 外で、source-revision 環境変数の注入なしに行い、build hook・入力データ・埋込み revision の保存を検証する。runtime provenance も環境変数や周囲の Git repository に依存させない。
- 配布名 `sashimi-itamae` と import 名 `itamae` を区別し、C の extras、SI/W/F の依存、lock/source 設定、distribution metadata lookup、artifact checker を揃える。wheel metadata に開発用の uv source 設定が引き継がれるとは仮定しない。
- 各パッケージ単独と全5パッケージ同居を、ソースツリー外のクリーン環境で検証する。
- import だけでなく、各 variant の代表的な物理量計算を実行する。
- 同梱データ、実行時 cache の書込み先、runtime file 衝突、artifact 内の source revision を確認する。
- 検証した候補 SHA の組合せを親の作業ブランチの manifest に記録し、gitlink と同一変更で更新する。候補 artifact と manifest の対応を検証する。
- リリース workflow、予定版、公開順序、検証コマンドを準備する。公開 job は明示的な承認操作なしに起動しない構成にする。
- 本番公開は ITAMAE、続いて各 SASHIMI の順を予定するが、今回実行しない。

**PyPI へのアップロード、公開 workflow の起動・予約・自動実行の有効化は行わない。** 公開にはピアレビュー後のユーザーの明示的な指示が必要である。TestPyPI へのアップロードも公開を伴うため、今回のローカル検証を代替する目的で無断実行しない。公開を起動し得る tag の作成・push も行わない。

リポジトリの公開範囲変更はユーザーに確認する。公開予定の合意を、直ちに private repository の公開設定を変更する指示として扱わない。

認証・公開権限・インデックス上の依存解決など、実際の公開操作に依存する検証は、未実施項目として正確に記録する。main 統合後と公開後の検証手順は引き渡し資料に残す。

### CI と完了前の必須検証

- ITAMAE：Ruff、format check、mypy、pytest/coverage、最小依存、Astropy/Colossus backend、Python matrix、build と clean artifact smoke。
- 各 variant：migration lint、A/B/C と製品 golden、invariant、固定 ITAMAE 入力、build、clean install、最小数値計算。新 API と形式変換を検証し、旧 runtime import の共存を完了条件として残さない。
- Family：正確な5者の組合せ、manifest/gitlink、catalog schema、runtime file 非衝突、provenance、各 variant の小カタログ・代表 observable。
- PR CI は `itamae-migration` 向け子 PR で実際に動くことを確認する。main 向け umbrella の検証は可能だが自動マージを有効にしない。
- normalized quadrature、適用可能なモデルの `m_bound <= m_acc`、profile 逆関数、scalar/array、serial/chunked、native/Astropy 単位、global state 復元、seeded realization、serialization を検証する。
- 無効な質量・半径・単位、未対応宇宙論、補間範囲外、欠落した optional dependency、cache 破損、不正 backend、廃止 API の指定に対し、明示的な失敗または文書化した validity flag を確認する。silent NaN や silent fallback で継続しない。
- 数値 grid・quadrature・solver の収束試験を行う。重い試験の実行経路は PR CI と分けてよいが、未実行の必須試験を成功扱いしない。

## 8. 確認事項が生じた場合の相談方針

migration・リリース準備中に、ユーザーの判断や確認が必要な点が出てきた場合は、必ずユーザーに尋ねる。完了報告まで保留したり、推測で確定したりしない。

例えば、次の事項を含む。

- 科学的処方、修正の採否、default、比較基準、許容誤差の判断
- 原因不明の数値差や、結果の物理的解釈
- API・互換性・既存機能の扱いに関する未決定事項
- 当初の対象範囲、対応環境、優先順位の変更
- ライセンス、著作権、canonical source、公開条件、版管理
- 既存作業と競合する変更や、計画からの重要な逸脱

質問の前に、コード・文書・履歴で解決できる事実を調べる。質問時には次を簡潔に示す。

1. 何を決める必要があるか
2. 確認した根拠・比較結果
3. 選択肢と推奨案、その影響
4. 回答待ちで止まる作業と、独立して進められる作業

回答を得るまで、確認事項に依存する実装・仕様・公開条件を確定しない。回答待ちの間は独立した作業を進める。未回答や時間の経過を承認と解釈しない。

既に合意済みの方針や、結果・公開契約に影響しない通常の実装判断については、同じ確認を繰り返さず進める。ユーザーの回答とその反映先を判断記録に残す。

## 9. 作業方法

「改善・実証のループ」で進める。各変更について、問題、仮説、変更内容、実行条件、結果、失敗、判断を Markdown/notebook に記録する。

科学的変更と構造変更を分離し、小さなレビュー可能な commit/PR にする。必要な commit・push・PR 更新は第2節のブランチ制約内で行い、既存の Issue を優先して進捗を管理する。重複 Issue や完了済み作業の再実装を避ける。

テスト成功を科学的妥当性の証明と同一視しない。性能改善だけのために検証範囲や物理機能を削らない。

### 実施順序と既存課題への対応

| 順序 | 作業と完了条件 | 既存の追跡先 |
| --- | --- | --- |
| 1 | 最新状態・作業先・既存機能を監査し、完了済み GOV/SYNC の再実装を避ける | 親 #1、#4、#25、#26、#28、ITAMAE #3、F #2/#3 |
| 2 | 参照 A を凍結し、B/C の比較・fixture・metadata 更新を用意する | 親 #10/#11/#12、F #6、golden policy |
| 3 | 各修正の科学的検証と採用判断を記録し、製品の計算仕様を固定する | PHY-C/SI/W/F |
| 4 | 共通実行系を堅牢化し、C/SI の component 化、W/F の pipeline 接続、新 API、legacy 除去を完了する | ITAMAE #4/#5、親 #7/#8/#9、F #5 |
| 5 | 全既存物理量・notebook・公開契約・F upstream/権利・配布物を確認する | 親 #5/#6/#13/#14/#15、F #4 |
| 6 | migration 候補の正確な全5者を検証し、親の作業ブランチへ記録してピアレビューへ渡す | 親 #16、#17 の候補準備部分 |
| レビュー後 | 明示指示に従い main 統合、最終 SHA の再検証、公開を行う | 親 #17 の最終統合部分、公開手順 |

依存しない作業は並行してよいが、参照を失う削除や科学的判断の先取りをしない。CORE の構造変更は検証済み入力で進め、科学的修正と同一 PR に混ぜない。Issue の古い acceptance criteria が legacy 常設・即時公開を要求していたら本計画へ揃える。新しい実験・比較・高額な計算の必要性が未決ならユーザーに確認する。

性能改善は一致と invariant を確認した後に行う。繰返し積分の削減、vectorization、chunking、cache、逆関数の再利用、コピー削減、決定的並列化の順に必要性を調べ、変更前後を回帰検証する。JAX 等の新 backend を今回の必須要件にしない。

### PR と記録の最小内容

PR は問題と変更後の挙動から始め、共通機構と variant の物理所有、API/単位/schema/cache/provenance の変更、A/B/C のどの比較を行ったか、適用した検証と結果、未実施項目、科学的根拠とユーザー判断を含める。構造変更・式修正・単位変更・API 改名・最適化を別のレビュー単位にし、不可分なら理由を示す。

ローカルでは CI と同じ runner・依存入力で適切な検証を行う。bug fix は修正前に失敗する保護テスト、共通機構は独立した unit/integration、refactor は実際の意味のある回帰を用意する。文書だけの変更に数値試験の追加は不要である。

## 10. 停止条件とピアレビュー用の引き渡し

以下が揃った段階で **「リリース準備完了・ピアレビュー待ち」** として停止する。

- 全 variant の既存物理量が新 API で利用できる。
- 製品内 legacy 計算が除去され、独立した旧版再現ワークフローがある。
- 必須の数値回帰・科学的検証・候補配布物検証が完了している。
- 必要なユーザー確認が済み、その判断が反映されている。
- 文書、移行案内、候補 artifact、再現手順、レビュー資料が揃っている。
- 実装変更と候補 revision は migration/topic ブランチに保持され、main 向け push・統合および PyPI 公開操作は行っていない。第2節で明示した今回の文書のみの main 更新は、この実装制約の例外である。

ピアレビュー資料には次を含める。

- 変更の要約と、レビュー対象の Issue/PR
- 各 repository の作業ブランチ、正確な候補 SHA、family manifest
- 候補 wheel/sdist の場所、版、ハッシュ、生成・検証手順
- 旧機能と新 API・テストの対応表
- A/B/C 比較、修正別の効果、科学的根拠
- 数値回帰・科学的検証・packaging 検証の結果
- ユーザーへの確認事項と回答・判断の記録
- 既知の制約、レビューで重点確認してほしい点
- main 統合・公開操作に依存する未実施の検証
- ピアレビュー承認後に必要な main 統合・再検証・公開の手順

必須検証の失敗や重要な確認待ちが残る場合は、「準備完了」とせず、阻害事項と再開手順を示す。

ピアレビュー後の修正・main 統合で SHA や artifact が変わった場合は、統合後の正確なソースから artifact を再作成し、影響する検証と全ファミリーの組合せ検証を実施する。旧候補の検証結果をそのまま新しい公開物の証拠にしない。

この goal の達成後は自動的に main 統合や公開工程へ進まない。main 統合と実際のリリースは、ピアレビュー後のユーザーからの明示的な指示を受けて行う別工程とする。
