# SASHIMI-Wのq5／q10と熱的WDMパワースペクトル

**現在のSASHIMI-Wが採用するViel et al. (2005)の係数と粒子質量の定義を維持するなら、物理的に採用すべきものはq10である。q5を同等に正しい熱的WDMの選択肢として残す根拠はない。** q5は、密度揺らぎの振幅に対して較正された抑制関数を、パワーに直接掛けた処方である。これは同じ粒子質量に対して小スケールのパワーを過大に残す。

ただし、q10にすれば現行モデルの全予測が厳密に正しくなるわけではない。振幅からパワーへの二乗、近似式の係数の精度、half-modeの定義、サブハロー模型と観測制限の再検証は、それぞれ区別して扱う必要がある。本報告は、文献と固定したソースコード、および独立した線形計算に基づいてqの判定を行うものであり、新しい衛星数やWDM質量制限を報告するものではない。

## 1. 判定の対象と物理量の定義

ここで比較する二つの処方は、同じCDMの線形物質パワースペクトルに対して

\[
Q_q(k)\equiv\frac{P_{\rm WDM}(k)}{P_{\rm CDM}(k)}
=\left[1+(\alpha k)^{2\nu}\right]^{-q/\nu},\qquad q\in\{5,10\},
\]

を掛けるものである。現行コードの係数は

\[
\nu=1.12,\qquad
\alpha=0.049\left(\frac{m_{\rm WDM}}{\mathrm{keV}}\right)^{-1.11}
\left(\frac{\Omega_{\rm WDM}}{0.25}\right)^{0.11}
\left(\frac h{0.7}\right)^{1.22}h^{-1}\mathrm{Mpc}
\]

である。したがって、ここでの判定は「同じ\(m_{\rm WDM},\alpha,\nu\)に対するq5とq10のどちらか」であり、自由な非熱的分布や別の質量較正を比較するものではない。係数とその適用対象はViel et al. (2005), Eqs. (4), (6), (7)で明示されている。[^2]

密度コントラスト\(\delta\)は振幅で、パワーはその二次統計量である。同じ原始揺らぎに対する線形発展を\(\delta_i(k,z)=D_i(k,z)\mathcal R(k)\)と書くと、

\[
\frac{P_{\rm WDM}}{P_{\rm CDM}}
=\left|\frac{D_{\rm WDM}}{D_{\rm CDM}}\right|^2.
\]

相対伝達関数を\(T_{\rm rel}\equiv\sqrt{P_{\rm WDM}/P_{\rm CDM}}\)と定義すれば、\(Q=T_{\rm rel}^2\)である。Vielらが\(-5/\nu\)を当てはめた対象は\(T_{\rm rel}\)なので、パワー比の指数は\(-10/\nu\)になる。**二乗という関係は物理量の定義から決まり、指数5や\(\alpha\)の数値はBoltzmann計算への近似的な較正から決まる。** 指数5そのものを第一原理から厳密に導いたという意味ではない。

単にパワー比を「transfer function」と呼ぶことは可能である。しかし、名称を変えるだけで振幅用の較正式をパワー用へ移せるわけではない。\(\sigma=\sqrt{S}\)を最後に取ることも、積分前の\(T^2\)の代わりにはならない。

## 2. 一次文献の照合

以下のページは原則として論文に印刷されたページを指す。PDFの通しページが異なる場合は併記した。文献の数よりも、定義、較正対象、実際の計算との対応を重視する。

| 文献 | 確認箇所 | 確認できる内容 | 判定への意味 |
|---|---|---|---|
| Bode, Ostriker & Turok (2001) | Appendix A, p.21, Eqs. (A8), (A9)と直後 | \(T=[1+(\alpha k)^{2\nu}]^{-5/\nu}\)。N体計算へ入力するパワーには\(\lvert T\rvert^2\)を掛けると明記。ここでは\(\nu=1.2\) | 原型から振幅とパワーは別物。[^1] |
| Viel et al. (2005) | pp.2–3, Eqs. (4), (6), (7) | \(T=\sqrt{P_{\Lambda\rm WDM}/P_{\Lambda\rm CDM}}\)、\(\nu=1.12\)、\(\alpha\)の係数0.049 | 現行係数に対する直接の根拠はq10。[^2] |
| Viel et al. (2012) | p.3, Eq. (1)、同ページ本文、p.6 Fig.2 | 掲載式は\(T^2=P_{\rm WDM}/P_{\rm CDM}\)に指数\(-5/\nu\)を付ける。一方、本文の抑制尺度と図はこの掲載式と整合しない | 引用元自身に不整合がある。q5の独立較正を示す論文とは読めない。[^3] |
| Schneider et al. (2012) | p.3, Eqs. (4), (5), (8) | 平方根の定義、振幅に指数\(-5/\nu\)、振幅half-mode | q10と\(T=1/2\)の尺度を明確に区別。[^5] |
| Benson et al. (2013) | p.2, Sec.2.1, Eq. (1) | CDMの伝達振幅を指数\(-\eta/\nu\)、\(\eta=5,\nu=1.2\)の関数で修正 | EPS模型の文脈でも振幅の処方。係数・尺度はVielと同一ではない。[^8] |
| Bose et al. (2016) | p.3, Eqs. (1)–(5) | \(P_{\rm WDM}=T^2P_{\rm CDM}\)、振幅用のViel式、\(T(k_{\rm hm})=1/2\) | SASHIMI-Wのhalf-modeの引用元は明確にq10。[^6] |
| Ludlow et al. (2016) | Sec.2.1、Table 1、half-modeの注記 | COCO-WDMなどのシミュレーションで濃度模型を調べる | 濃度模型側の入力スペクトルも追跡すべき根拠。q変更だけで濃度較正が検証済みになるわけではない。[^7] |
| Murgia et al. (2017) | pp.2,4（PDF pp.3,5）, Eqs. (2.1)–(2.5) | 熱的WDMはq10。一般の非熱的モデルには振幅の3パラメータ式を導入。half-modeは\(T^2=1/2\)と定義 | q10でもpower-halfの定義は合法。half-modeの名称だけでは比較できない。[^9] |
| Dekker et al. (2022), SASHIMI-W | arXiv v2 pp.3–4, Eq. (2)、出版版123026-3–4 | q5をパワー比として掲載。half-modeもBoseの振幅halfの式をpower-halfとして説明 | 物理量の取り違えが二箇所で現れる。[^4] |
| Decant et al. (2022) | Eqs. (3.5)–(3.7)、Appendix C | q10を維持し、高質量側で\(\alpha\)の係数を修正。CLASSの流体近似を切った比較 | 修正対象は較正係数であり、パワーへの二乗ではない。[^10] |
| Vogel & Abazajian (2023) | Eqs. (7)–(9)、Table II、Figs.1–3 | CLASSから新しい\(\alpha,\nu\)を較正。振幅に指数\(-5/\nu\) | 新しい熱的WDMの較正でもパワーはq10。[^11] |
| Nadler et al. (2025), COZMIC I | Eqs. (1), (2), (4), (5)、Appendix A.1 | パワー比を明示的に指数\(-10/\nu\)で記述。初期条件にはCLASSの伝達関数を直接使用 | 最近のシミュレーションとの対応もq10側。[^12] |

### 2.1 原典が明示していること

Bodeらは、密度の成長モードの振幅を比較して伝達関数を定義し、その後でN体初期条件のパワーへ二乗を掛けると述べている。Vielらはさらに、パワー比の平方根をEq. (4)で定義してからEq. (6)を与え、CMBFASTまたはCAMBを用いた較正を説明する。両論文は\(\nu\)や係数こそ異なるが、振幅からパワーへの二乗という点では一致している。[^1][^2]

ここでBodeの\(\nu=1.2\)、Vielの\(\nu=1.12\)、さらに後年の\(\nu=1.049\)を混ぜてはいけない。いずれも振幅用のフィットであることと、それぞれのフィット係数が数値的に同じであることは別の主張である。

### 2.2 Viel et al. (2012)の不整合をどう判断するか

SASHIMI-Wの引用文献[60]はViel et al. (2005)、[61]はViel et al. (2012)である。後者のEq. (1)には、確かにq5がパワー比として載っている。そのため「SASHIMI-Wだけに単発の誤植がある」と説明するのは不十分である。[^3][^4]

しかしViel et al. (2012)は、同じp.3で1 keVのパワーが約\(k=6\,h\,\mathrm{Mpc}^{-1}\)で半分になると説明している。同論文の\(\Omega_m=0.2711,\Omega_b=0.0451,h=0.703\)を掲載の\(\alpha\)へ代入すると、次の値を得る。これは掲載式をこちらで評価した数値である。

| 処方 | \(P_{\rm WDM}/P_{\rm CDM}=1/2\)の波数 | \(k=6\,h\,\mathrm{Mpc}^{-1}\)のパワー比 |
|---|---:|---:|
| q5 | 9.257 \(h\,\mathrm{Mpc}^{-1}\) | 0.7594 |
| q10 | 6.674 \(h\,\mathrm{Mpc}^{-1}\) | 0.5767 |

本文の概数とFig.2の線形抑制を示す点線はq10側を支持する。本文の約6という値を厳密な6.000とみなしてはいない。**論文内の証拠は、Eq. (1)の指数または左辺の記法に誤りがあるという解釈を強く支持する。** ただし、そのシミュレーションで使われた初期条件ファイルや生成コードを直接確認していないため、2012年の全シミュレーションの実入力が何だったかまでは断定しない。これは物理的なqの判定と、過去の計算を完全に再現する作業との境界である。

SASHIMI-WのarXiv v1、v2、著者所属機関が公開する最終出版版を照合したところ、いずれにもq5の記述が残っている。今回確認した公開版からは、この不整合が版の更新で解消したとは判断できない。著者からの訂正・説明を得たという意味ではなく、ここでの判定は式と計算の整合性に基づく。[^4]

## 3. 旧実装は実際にq5をパワーへ掛けている

固定したupstreamのcommitは`99dfc3632eec0126080c0273ddf78f84fe09216c`、今回の現行コードのsnapshotは`09322feb1e348f40fa93d0514f42dd02171a7282`である。コードとデータの取得元・ハッシュは[ソース記録](source_manifest.json)に保存した。

旧実装の[入力とsharp-k分散](sources/w-upstream/sashimi_w.py)では、CAMBの物質パワーテーブルを`Pk_file`として読み、積分の被積分関数へ\([1+(\alpha k)^{2\nu}]^{-5/\nu}\)を直接掛ける。該当箇所は同ファイル94–108行である。111行で取る平方根は\(S\to\sigma\)であり、伝達振幅の二乗ではない。138–142行のtop-hat分散でも同じq5が掛かる。

したがって、次の解釈では説明できない。

- `Pk`という名前でも実体は振幅なのではないか：入力はCAMBの物質パワーで、積分も\(k^2P(k)\)の形式である。
- 後段で二乗しているのではないか：\(S\to\sqrt S\to S\)は分散と標準偏差の変換であり、\(P T\)を\(P T^2\)へ変えない。
- 単位や\(h\)の変換なのではないか：\(\alpha k\)は無次元である。単位変換はqを変えない。
- \(\sigma_8\)の規格化で吸収できるのではないか：規格化は波数によらない定数を掛ける操作で、\(Q_5/Q_{10}\)の波数依存性を除けない。

現行の[伝達関数の実装](sources/w-current/sashimi_w_itamae_migration.py)はこの違いを明示し、同じ関数をsharp-kとtop-hatへ使っている。したがって今回の問題は、現在のコードがq5／q10を取り違えているというより、**歴史的q5を物理的選択肢として今後も提供すべきか**という判断である。両者を明示した移行段階の診断価値はあるが、科学的に同等なモデルという意味は与えられない。

### 3.1 規格化後にも残る差

固定したWMAP7テーブルに対して、独立した積分スクリプトでq5とq10を比較した。条件は\(\Omega_m=0.27,\Omega_b=0.0469,h=0.7,n_s=0.95,\sigma_8=0.82\)。旧実装のsharp-kカットオフと規格化質量を維持し、両方を同じ\(\sigma_8\)へ規格化している。ここでの質量分散は**その既存処方に対する比較**であり、フィルターの質量対応や規格化自体の物理的較正を保証するものではない。

| \(m_{\rm WDM}\) | \(M=10^6 M_\odot\)での\(S_5/S_{10}-1\) | \(M=10^8 M_\odot\) | \(M=10^{10} M_\odot\) |
|---|---:|---:|---:|
| 1 keV | +21.40% | +21.40% | +20.82% |
| 2 keV | +18.41% | +18.41% | +10.90% |
| 5 keV | +15.34% | +14.05% | +1.59% |

積分点数を32,769から65,537へ増やした代表点で、各\(S\)の最大相対変化は\(6.2\times10^{-9}\)未満だった。差はこの積分の数値誤差では説明できない。ただし、この表の百分率をそのままサブハロー数や観測制限の変化率として使うことはできない。[積分結果](results/analytic-comparison.json)と[再現スクリプト](scripts/analytic_comparison.py)を付属する。

## 4. 独立したBoltzmann計算

一次文献とは独立に、CLASS v3.3.4の固定ソースから線形の$P_{\rm WDM}$と$P_{\rm CDM}$を計算した。Boltzmann計算にはq5もq10も入力していない。温度を持つFermi–Dirac粒子の分布を与え、得られた物質パワーの比を、後から各フィットと比較する。[^14][^15]

条件は$h=0.6736,\omega_b=0.02237,\omega_{\rm DM}=0.12,A_s=2.1\times10^{-9},n_s=0.9649$、平坦宇宙、massless active neutrinos $N_{\rm ur}=3.046$、$z=0,99$である。WDMは2内部自由度、化学ポテンシャル0の熱的fermionで、暗黒物質の全量を置き換える。WDMの温度は、指定質量と現在の密度$\omega_{\rm WDM}=0.12$を満たすようにCLASSの背景密度から決めた。分布の振幅を自由に再規格化して質量と温度の不整合を隠す方法は用いていない。

最終温度$T_{\rm WDM}/T_\gamma$は1、2、5 keVでそれぞれ0.16011208、0.12708104、0.09363411である。現在のWDM密度の目標値からの相対差は$3\times10^{-13}$未満だった。CLASSが同期ゲージのために保持する微小なCDM成分は$\Omega_{\rm cdm}=10^{-10}$で、ここで比較する差に対して無視できる。原始振幅を揃え、計算後に各スペクトルを同じ$\sigma_8$へ再規格化する操作はしていない。

### 4.1 同じ物理的尺度での比較

次の表は、**CLASSのパワー比が0.5になる波数に、各フィットを評価した値**である。各列で違う波数を選んでいるのではない。$z=0$の結果を示す。

| 粒子質量 | CLASSのpower-half波数 [h/Mpc] | q5のパワー比 | 現行q10のパワー比 | Vogel 2023のq10 |
|---|---:|---:|---:|---:|
| 1 keV | 6.9443 | 0.7046 | 0.4964 | 較正範囲外 |
| 2 keV | 15.4125 | 0.6895 | 0.4754 | 0.4906 |
| 5 keV | 44.9245 | 0.6595 | 0.4349 | 0.5038 |

![線形熱的WDMのパワー比](figures/linear-power-comparison.png)

図では、q5が同じ質量のCLASSスペクトルよりも小スケールのパワーを多く残す。1 keVではVielのq10が特によく合い、q5の誤差を係数の微調整や数値誤差として扱うことはできない。5 keVでは古いq10にも明確な較正誤差があるが、Vogelの係数を使うq10やDecantの修正係数で改善する。例えば5 keVの同じ波数で、Decantの修正は0.4998を返す。これは、二乗を省くことではなく、二乗を保ったまま較正を更新するという説明を支持する。

CLASSの$0.05\le P_{\rm WDM}/P_{\rm CDM}\le0.95$に入る、計算範囲内の波数で、q5の最大絶対誤差は1、2、5 keVについて0.242、0.219、0.179だった。現行q10では0.0113、0.0309、0.0713、新しいVogel q10では2、5 keVで0.0186、0.00994である。これはパワー比そのものの差であって、誤って百分率と混同してはいけない。1 keVに対するVogel式は較正した質量範囲外なので、優劣の根拠にしない。

### 4.2 精度と適用範囲

基準計算は`ncdm_fluid_approximation=3`、`tol_ncdm_synchronous=1e-4`、`l_max_ncdm=24`、`k_per_decade_for_pk=30`を用いた。代表の2 keVについて、CDMとWDMの両方を`1e-5`、40、60へ厳しくし、摂動積分許容誤差も$10^{-6}$から$2\times10^{-7}$へ変更した。

この精度変更による$z=0$のパワー比の最大絶対変化は$2.96\times10^{-4}$、上記の遷移領域での最大相対変化は0.122%だった。power-half波数は15.41250から15.40995 h/Mpcへ変わり、相対変化は0.017%未満である。$z=99$でも同様だった。この精度確認は2 keVに対するもので、全質量・全宇宙論についての誤差上限を保証したものではない。

この計算は新旧論文の全条件を再現する実験ではなく、熱的分布と物質パワーとの対応を独立に確認する実験である。active neutrinoを質量0としたため、$m_\nu=0.06$ eVを含めたVogelの全設定とは一致しない。したがって新較正式のsub-percentの優劣を認定する根拠には使わず、q5の大きな差と、古い較正の誤差が別物であることの確認に使う。$z=99$でもq5／q10の判定は変わらず、各質量のpower-half波数の$z=0$との差は約0.1–0.2%であった。

比較は$0.01\le k\le80\,h\,\mathrm{Mpc}^{-1}$に限定し、出力を範囲外へ外挿していない。カットオフの深部、非線形成長、混合WDM、非熱的sterile neutrino、高質量spin-3/2模型などへの一般化は今回の数値確認に含まない。

## 5. half-modeの定義と質量換算

q10に対して、次の二つの尺度は異なる。

\[
k_{P=1/2}=\frac{1}{\alpha}
\left(2^{\nu/10}-1\right)^{1/(2\nu)},\qquad
k_{T=1/2}=k_{P=1/4}=\frac{1}{\alpha}
\left(2^{\nu/5}-1\right)^{1/(2\nu)}.
\]

Bose et al. (2016)とSchneider et al. (2012)は後者をhalf-modeとして用いる。一方、Murgia et al. (2017)は前者を用いる。**どちらの定義も、閾値を明示して一貫して使えば正しい。** 問題は定義の選択そのものではなく、片方の式をもう片方の意味で引用・換算することである。[^5][^6][^9]

SASHIMI-W本文は\(P/P_{\rm CDM}=0.5\)と述べながら、Boseの\(2^{\nu/5}\)を含む式を引用している。q5をパワー比とした論文内では代数的に一致するが、引用元の熱的WDMの物理的定義と一致しない。現行のq10側metadataは、この同じ数値式を\(T=0.5,P/P_{\rm CDM}=0.25\)として記録しており、その点は明示されている。

同じ\(\alpha,\nu=1.12\)で、同じpower-half閾値を比較すると、

\[
\frac{k_{P=1/2}^{(q5)}}{k_{P=1/2}^{(q10)}}=1.38695.
\]

\(M\propto k^{-3}\)という同じ質量対応を使えば、q5のpower-half質量はq10の0.37482倍となる。これは単なる小さな丸め誤差ではない。

また\(\alpha\propto m^{-1.11}\)から、q5の粒子質量\(m\)と同じpower-half波数を持つq10の質量は約\(1.34271m\)になる。しかし、この対応は**一点の尺度だけを合わせる近似換算**である。二つの関数形は全波数で一致せず、弱い抑制域や深いカットオフでは別の対応になる。したがって旧制限4.4 keVへ1.34271を掛けて、新しい制限が得られたと報告することはできない。

sterile neutrinoについては、元の運動量分布から得る\(P(k)\)を使い、熱的側と同じpower比の閾値で尺度を対応させる必要がある。SASHIMI-Wはこの換算を有効Jeans質量や崩壊閾値にも使うため、half-modeの誤解はスペクトル表示だけに留まらない。非熱的分布全体を熱的模型の一つの質量へ置き換える精度も、別途確認が必要である。[^4][^9]

## 6. q10と新しい較正式の関係

Viel et al. (2005)は\(k<5h\,\mathrm{Mpc}^{-1}\)で\(\nu=1.12\)がよく合うと説明する。後年の数keV以上の議論に対して、0.049という係数をそのまま使った近似が常に十分であるとは限らない。これはq10でも残る精度の問題である。[^2]

Decant et al. (2022), Appendix Cは、CLASSとの比較から質量域に応じて0.049、0.045、0.043という係数を示す。指数は振幅に対して\(-5/\nu\)、パワーに対して\(-10/\nu\)のままである。小スケール計算で流体近似を切る必要性も説明している。[^10]

Vogel & Abazajian (2023)は、完全に熱化したspin-1/2模型に対して

\[
T(k)=[1+(\alpha k)^{2\nu}]^{-5/\nu},\quad\nu=1.049,
\]
\[
\alpha=0.0437\left(\frac{m}{\mathrm{keV}}\right)^{-1.188}
\left(\frac{\omega_{\rm WDM}}{0.12}\right)^{0.2463}
\left(\frac h{0.6736}\right)^{2.012}h^{-1}\mathrm{Mpc}
\]

という新しい較正を与える。検討した質量は2、5、10、20、100 keVであり、宇宙論依存の較正はPlanck近傍で行われている。したがって、この式をWMAP7の現行コードへ導入する場合にも、想定する宇宙論・自由度・質量範囲の確認が要る。[^11]

COZMIC Iはこの新しい係数を明示しつつ、実際の初期条件生成にはCLASSの伝達関数を直接使っている。同じSASHIMI系の後年の混合WDM解析でも、CLASSから物質パワーを作る経路が使われている。いずれもq5を同等な熱的処方として再較正した証拠ではない。[^12][^13]

一般の非熱的模型では\(T=[1+(\alpha k)^\beta]^\gamma\)のように形状自由度を増やせる。したがって「q5に似た曲線を生む物理模型が宇宙に一切存在し得ない」とまでは主張しない。今回排除するのは、**Vielの同じ\(m,\alpha,\nu\)を付けたq5を、同じ熱的WDMとして正しいと扱うこと**である。[^9]

## 7. 実装方針に対する判断

q5／q10の科学的判定は、現行のViel処方についてq10としてよい。q5を通常の計算APIから廃止し、歴史的な再現性は固定commit・入力・結果の記録で保持する方針を支持する。q5を残す理由が「どちらが物理的に正しいか未確定だから」であれば、その未確定状態は今回の証拠で解消できる。

実装へ進む場合には、次の変更と検証を一まとまりで扱うことが適切である。

1. 振幅\(T\)とパワー比\(Q=T^2\)の関数・引数・metadataを明確に分け、sharp-kとtop-hatが同じ物理スペクトルを使うようにする。
2. q5選択を黙ってq10へ読み替えず、旧指定や旧キャッシュを識別できるようにする。過去の結果の意味を変えない。
3. half-modeは少なくとも\(P/P_{\rm CDM}=1/2\)と\(1/4\)を区別し、sterile neutrino換算の閾値も揃える。
4. q10化だけの比較と、新しい\(\alpha,\nu\)または直接Boltzmannスペクトルへの変更を分けて評価する。宇宙論、フィルター、崩壊閾値、潮汐処方などを同時に変えて差の由来を失わない。
5. \(P(k)\)、\(S(M)\)、\(dS/dM\)、濃度、最終カタログを順に比較し、観測制限を更新する場合は元の尤度・銀河形成条件・ホスト質量条件で再計算する。

このうち「q5を除くべきか」という判断は、過去の全衛星数計算を再実行しなくても下せる。一方、「更新後に何keVを除外できるか」「サブハロー数が何%変わるか」は、今回の線形パワーの判定からは確定しない。濃度やEPSの較正、tidal evolutionの妥当性まで今回の結論へ含めない。

本報告に伴う作業は独立した検証用ディレクトリ内の資料・計算・報告書作成であり、製品コードからq5を削除したものではない。

## 8. 再現性と記録

主要な記録は次のとおりである。

- [論文の取得URL・SHA256](papers/manifest.json)、[コードsnapshot](source_manifest.json)、[CLASSの固定ソース](sources/class-source.json)。
- [CLASS計算スクリプト](scripts/run_class.py)、各計算の`results/class/*/input.ini`、標準出力、出力ファイルのハッシュ。
- [CLASS比較結果](results/class-comparison.json)、[比較解析](scripts/analyze_class.py)、[固定パワーテーブルの積分結果](results/analytic-comparison.json)。
- [比較図](figures/linear-power-comparison.png)と[数値・出典を収録したスプレッドシート](outputs/q5-q10-review/q5-q10-supporting-data.xlsx)は同じJSONから生成した。スプレッドシートにはhalf-modeの要約、4,806行のパワー比較、78行の分散比較、出典を収録し、線形パワー、フィット、処方内の質量分散を区別して保存した。要約数値のJSONとの一致と、4シートの表示を確認した。

比較は2026年9月10日に固定した公開資料とローカルsnapshotに対するもの。初期の有質量active-neutrino・高波数の参照計算は計算範囲を絞るため完了前に停止し、その設定を別途保存した。そこから物理的・数値的な結論は採っていない。最終の独立計算は、上記の条件と精度確認を明示した完了済みの計算を用いる。

## Sources

[^1]: P. Bode, J. P. Ostriker & N. Turok, “Halo Formation in Warm Dark Matter Models,” ApJ 556, 93 (2001). [arXiv:astro-ph/0010389v3](https://arxiv.org/pdf/astro-ph/0010389v3), Appendix A, p.21, Eqs. (A8)–(A9).
[^2]: M. Viel, J. Lesgourgues, M. G. Haehnelt, S. Matarrese & A. Riotto, “Constraining Warm Dark Matter candidates including sterile neutrinos and light gravitinos with WMAP and the Lyman-alpha forest,” Phys. Rev. D 71, 063534 (2005). [arXiv:astro-ph/0501562v2](https://arxiv.org/pdf/astro-ph/0501562v2), pp.2–3, Eqs. (4), (6), (7).
[^3]: M. Viel, K. Markovic, M. Baldi & J. Weller, “The Non-Linear Matter Power Spectrum in Warm Dark Matter Cosmologies,” MNRAS 421, 50–62 (2012). [arXiv:1107.4094v2](https://arxiv.org/pdf/1107.4094v2), p.3, Eq. (1)と本文、p.6, Fig.2。
[^4]: A. Dekker, S. Ando, C. A. Correa & K. C. Y. Ng, “Warm dark matter constraints using Milky Way satellite observations and subhalo evolution modeling,” Phys. Rev. D 106, 123026 (2022). [arXiv v1](https://arxiv.org/pdf/2111.13137v1), [arXiv v2](https://arxiv.org/pdf/2111.13137v2), [最終出版版](https://pure.uva.nl/ws/files/114144314/Warm_dark_matter_constraints_using_Milky_Way_satellite_observations.pdf), Eq. (2)、half-modeの段落。出版版は123026-3–4、表紙付きPDFではpp.4–5。
[^5]: A. Schneider, R. E. Smith, A. V. Maccio & B. Moore, “Nonlinear evolution of cosmological structures in Warm Dark Matter models,” MNRAS 424, 684 (2012). [arXiv:1112.0330](https://arxiv.org/pdf/1112.0330), p.3, Eqs. (4)–(9).
[^6]: S. Bose et al., “The COpernicus COmplexio: Statistical Properties of Warm Dark Matter Haloes,” MNRAS 455, 318 (2016). [arXiv:1507.01998](https://arxiv.org/pdf/1507.01998), p.3, Eqs. (1)–(5).
[^7]: A. D. Ludlow et al., “The Mass-Concentration-Redshift Relation of Cold and Warm Dark Matter Halos,” MNRAS 460, 1214 (2016). [arXiv:1601.02624](https://arxiv.org/pdf/1601.02624), Sec.2、Table 1。
[^8]: A. J. Benson et al., “Dark Matter Halo Merger Histories Beyond Cold Dark Matter: I – Methods and Application to Warm Dark Matter,” MNRAS 428, 1774 (2013). [arXiv:1209.3018](https://arxiv.org/pdf/1209.3018), p.2, Sec.2.1, Eq. (1).
[^9]: R. Murgia, A. Merle, M. Viel, M. Totzauer & A. Schneider, “‘Non-cold’ dark matter at small scales: a general approach,” JCAP 11, 046 (2017). [arXiv:1704.07838v2](https://arxiv.org/pdf/1704.07838v2), Eqs. (2.1)–(2.5)、Appendix A。
[^10]: Q. Decant, J. Heisig, D. C. Hooper & L. Lopez-Honorez, “Lyman-alpha constraints on freeze-in and superWIMPs,” JCAP 03, 041 (2022). [arXiv:2111.09321v2](https://arxiv.org/pdf/2111.09321v2), Eqs. (3.5)–(3.7), (C.1)–(C.2)。
[^11]: C. M. Vogel & K. N. Abazajian, “Entering the Era of Measuring Sub-Galactic Dark Matter Structure: Accurate Transfer Functions for Axino, Gravitino & Sterile Neutrino Thermal Warm Dark Matter,” Phys. Rev. D 108, 043520 (2023). [arXiv:2210.10753v2](https://arxiv.org/pdf/2210.10753v2), Eqs. (7)–(9)、Table II、Figs.1–3。
[^12]: E. O. Nadler, R. An, V. Gluscevic, A. Benson & X. Du, “COZMIC. I. Cosmological Zoom-in Simulations with Initial Conditions Beyond Cold Dark Matter,” ApJ 986, 127 (2025). [arXiv:2410.03635v3](https://arxiv.org/pdf/2410.03635v3), Eqs. (1), (2), (4), (5)、Appendix A.1。
[^13]: C. Y. Tan, A. Dekker & A. Drlica-Wagner, “Mixed Warm Dark Matter Constraints using Milky Way Satellite Galaxy Counts” (2025). [arXiv:2409.18917v3](https://arxiv.org/pdf/2409.18917v3), Sec.II。ここではCLASS入力スペクトルの採用を参照し、同論文全体の熱的自由度・質量換算を検証したという意味ではない。
[^14]: J. Lesgourgues & T. Tram, “The Cosmic Linear Anisotropy Solving System (CLASS) IV: Efficient implementation of non-cold relics,” JCAP 09, 032 (2011). [arXiv:1104.2935](https://arxiv.org/pdf/1104.2935)。
[^15]: CLASS official repository, [v3.3.4固定commit](https://github.com/lesgourg/class_public/tree/e85808324f51fc694d12e3ed7439552a3c3f9540)。入力仕様は同commitの`explanatory.ini`、数値精度の既定値は`include/precisions.h`。
