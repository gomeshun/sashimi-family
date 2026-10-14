# 数値計算コードの docstring・テスト評価（2026-10-14）

対象は 4 リポジトリ、テスト定義 **324 件**。関数・クラス・テスト計 **1,042 定義**に NumPy スタイルの説明を整備した。物理量、単位、配列形状、数値計算上の仮定と使用範囲を記載し、各テストに目的、成功・失敗条件、検証の限界を付した。AGENTS.md に同じ規則を記録した。

提案は **維持 244 件、統合候補 51 件、条件の一部緩和候補 23 件、廃止・置換候補 6 件**。テストの削除、アサーションや許容誤差の変更は行っていない。

## リポジトリ別の結果

| 対象 | テスト定義 | 維持 | 統合 | 一部緩和 | 廃止・置換 | 個別評価 |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| itamae | 145 | 115 | 19 | 9 | 2 | [全件一覧](https://github.com/gomeshun/itamae/blob/codex/shared-picard-20261014/docs/test-scientific-audit.md) |
| sashimi-c | 72 | 53 | 14 | 5 | 0 | [全件一覧](https://github.com/gomeshun/sashimi-c/blob/codex/picard-migration-20261014/docs/test-scientific-audit.md) |
| sashimi-si | 56 | 41 | 9 | 3 | 3 | [全件一覧](https://github.com/gomeshun/sashimi-si/blob/codex/picard-migration-20261014/docs/test-scientific-audit.md) |
| sashimi-w | 51 | 35 | 9 | 6 | 1 | [全件一覧](https://github.com/gomeshun/sashimi-w/blob/codex/picard-migration-20261014/docs/test-scientific-audit.md) |

非公開コンポーネントの個別評価は、その非公開リポジトリで管理する。

## 廃止・置換を優先検討する候補

- **itamae: [test_execution_reuses_canonical_variance_protocol](https://github.com/gomeshun/itamae/blob/codex/shared-picard-20261014/tests/test_execution.py#L41)** — プロトコルの Python オブジェクト同一性だけを要求する。実行・分散アダプタの動作確認を残せる。正確な import 同一性が公開 API の約束なら維持する。
- **itamae: [test_population_components_delegate_to_canonical_pipeline](https://github.com/gomeshun/itamae/blob/codex/shared-picard-20261014/tests/test_execution_composition.py#L242)** — 返る具体的クラスだけを要求する。隣接する callback／component の計算結果比較を残せば、同等の実装を許せる。
- **sashimi-si: [TestCosmology.test_dark_energy_density_parameter_is_recovered_today](https://github.com/gomeshun/sashimi-si/blob/codex/picard-migration-20261014/tests/test_physics_equations.py#L689)** — 保存した定数同士の恒等式であり、本体の赤方偏移依存式を呼んでいない。背景式・成長因子の検証を残す。
- **sashimi-si: [TestNFWConstants.test_rmax_over_rs](https://github.com/gomeshun/sashimi-si/blob/codex/picard-migration-20261014/tests/test_physics_equations.py#L758)** — 独立に導いた値とテスト内の数値リテラルだけを比較するため、本体の係数変更を検知できない。実際の stage 出力の検証へ置き換える。
- **sashimi-si: [TestNFWConstants.test_vmax_and_rhos_normalizations](https://github.com/gomeshun/sashimi-si/blob/codex/picard-migration-20261014/tests/test_physics_equations.py#L774)** — 同様に本体の係数を参照しない。stage の単位恒等式に加えて実際の collapse-time 係数の検証を確保してから置換する。
- **sashimi-w: [test_callable_adapter_uses_same_continuous_derivative](https://github.com/gomeshun/sashimi-w/blob/codex/picard-migration-20261014/tests/test_itamae_variance.py#L101)** — 同じファイルの複数質量・赤方偏移を使う adapter テストと重複する。固有の z=2 ケースを残るテストへ移す。

## 統合・緩和の方針

- 例外の種類、正しい入力を受け付ける対照例、物理的に異なる境界条件は残し、同じ設定で繰り返す確認をまとめる。統合候補の件数は削除可能な検証条件の件数ではない。
- private 属性名、具体的なクラス、識別子の文字列、描画点数、キャッシュの更新時刻など、科学的出力を保証しない制約を切り離す。物理入力を変えたときのキャッシュ無効化や出所の追跡は残す。
- 同じ入力・保存形式の同一性に対する厳密比較は妥当である。凍結した計算結果との一致は再現性の確認として位置づけ、物理的精度や calibration の証明とは区別する。
- 解析解、独立積分、単位変換、EPS の小さな正の分散差、SI の形成時刻・速度単位、factorized weights の確認は維持する。近似 Shanks との一致だけから新 solver の精度を判定しない。

## 評価中に見つかった検証の不足

ITAMAE の Colossus 密度 wrapper は `Msun*h^2/kpc^3` からの長さ換算 `1e9` のみを掛け、canonical `Msun/Mpc^3` に必要な `h**2` を掛けていない。既存の比較は H と growth のみで、この不一致を検知しない。docstring に現状の単位と制約を明記した。本体の修正と密度の独立した単位検証は別途必要であり、今回の通過テスト数はこの不足を解消しない。

W の sharp-k cutoff 係数と sigma8 正規化を固定するテストは現行の計算処方を記録するもので、その物理的妥当性を独立に確認するものではない。積分・導関数・小さな分散差の検証と分けて評価した。

## 検証と由来

- Python 3.11.15 の既存テスト **647 ケース**通過。内訳にはパラメータ展開と、対象内に存在する family-manifest テストを含む。
- NumPy docstring を解析し、対象定義に説明があり、明示的な引数の記載漏れ・余計な引数がないことを確認した。
- 全 tracked Python ファイルの実行 AST は説明文を除いて編集前と同一。凍結参照データ・履歴スクリプトのバイト列も維持した。
- Ruff 全項目、ITAMAE の format/mypy を通過。実行済みのカタログ・誤差 sweep・スライドは元の計算 SHA の記録を保持する。
- 移植後の共有 Picard 実装に残っていた追加 MIT ヘッダーを削除した。上流管理者に代わるライセンスの選択をしない規則を AGENTS.md に加えた。
- 親の compatibility.toml と五つの gitlink は今回の文書整備で更新していない。各 PR の候補 revision と記録済み family set を区別する。
