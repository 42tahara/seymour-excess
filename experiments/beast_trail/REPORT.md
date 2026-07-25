# 獣道 phase 1 — arc-slack 解剖 + LP 実験

## サマリ

**Part A 結論**: n=53 witness (score=5) の tight-弧部分グラフは **32 頂点の非自明 SCC** を含む — 弧不等式が広範囲に飽和している強い構造。深赤字コア {1,2,4,5,37..41} (m ∈ [-15, -12]) は互いに tight 弧で密に繋がっており、`o(u,v)=13..15` の推移三角形が赤字を「支払っている」。

**Part B 結論**: M_{n,c} の LP 緩和は **obj=0** (n=17..20, arc-ineq family あり/なし共に)。弧不等式の Big-M 形は分数内部で自明化するため下界を全く動かさない。整数バージョン (SCIP) は 120s では最適性証明に至らず、UB として feasible obj=17..25 を返すのみ。**LP アプローチ (現状の緩和形) は組合せ的恒等式候補を出すには弱すぎる**。

---

## Part A: 弧 slack 解剖

### 対象

- n=53: `champion_n53_ca40b396.json` (graph_sha1 `dc922e89...`), score=5 (excess=4, min-out=17)
- n=50: `/Users/srm/dev/seymour-excess/data/champion_28da4a1e.json` (graph_sha1 `17cd7dc8...`), score=5 (excess=5, min-out=10)

### 定義 (evaluate.py の変数と一致)

```
d1(v) = |N+(v)|                             out-degree
d2(v) = |N++(v)|   strict: excludes N+(v) and {v}
m(v)  = d2(v) - d1(v)                        Seymour deficit (負ほど赤字)
o(u,v) = |N+(u) ∩ N+(v)|                    common out-neighbors
α(u,v) = m(u) + d1(u) - d1(v) + o(u,v)      = d2(u) - d1(v) + o(u,v)
```

弧 u→v について α(u,v) ≥ 0 (oriented graph, digon なし)。等号は「N+(u) ⊇ N+(v) \\ N+(u) \\ {u}」で見た u から v 経由の外向き到達がロス無しの時。

### A-1: α ヒストグラム (`slack_n53_ca40b396.json`, `slack_n50_17cd7dc8.json`)

| n | arcs | α=0 | mean α | max α | tight 頻度 |
|---|-----:|----:|-------:|------:|-----------:|
| 53 | 1201 | 568 | 4.63 | 22 | **47.3%** |
| 50 |  639 | 100 | 4.12 | 13 | **15.6%** |

両者とも α は連続分布 + gap 後の高α帯という **双峰分布**:
- n=53: 0..4 / 17..22 (gap 12..16)
- n=50: 0..6 / 10..13 (gap 7..9)

### A-2: tight 弧部分グラフの構造 (n=53)

Tarjan で SCC を取ると:

- 非自明 SCC は **1 つのみ、サイズ 32** (`{0,1,2,4,5,11,13,14,15,16,17,18,25,29,30,32,33,34,35,36,37,38,39,40,41,42,46,48,49,50,51,52}`)
- 残りの頂点は tight 弧の singleton (in/out はあるが cycle に乗らない)

この 32 頂点上では
```
Σ_{v∈SCC} m(v) + Σ_{arc∈SCC (tight)} o(u,v) = 0
```
が **恒等式**として成立 (全弧 α=0 の telescoping)。ここに乗る m の総和と o の総和がぴったり相殺する — 組合せ的恒等式の候補として最有力。

n=50 (17cd7dc8) も同様に **21 頂点の非自明 tight SCC** を持つ (`{4,5,8,12,14,15,16,18,23,24,28,29,30,31,34,36,37,40,44,47,48}`)。両 witness で「大きな tight SCC」= 「弧不等式の共同飽和クラスタ」が共通構造。

### A-3: 深赤字頂点の in-arcs 内訳

**n=50 (17cd7dc8)**: m 分布は **滑らか** [-5, 0]:
- m=0: 5 頂点 (excess の全てを供給), m=-1: 22, m=-2: 17, m=-3: 4, m=-4: 1 (v=42), m=-5: 1 (v=21)
- 深赤字 (m ≤ -10) は **無し** — 全体的にちょうど「ボーダー赤字」

**n=53 (dc922e89)**:

深赤字 (m ≤ -10): `{1, 2, 4, 5, 37, 38, 39, 40, 41}` (9 頂点、m=-15..-12)

代表: v=38 (m=-15, d1=33, d2=18)
- in-degree = 18、Σ α = 18、Σ o = **270** (18 弧 × o=15)
- tight in-arcs: 8 本
- 送り主の内訳 (α=0):
  - u=18 (m=+1, d1=17), u=25 (m=-9), u=29 (m=-2), u=30 (m=-1), u=32 (m=-2), ...
  - どの u→38 弧も `o(u,38)=15` — 共通推移三角形が 15 個
  - v=38 の深赤字はこの多重推移三角形で「支払われている」

同様に v=2 (m=-14): in-degree 17、tight 13 本、o=13/arc。u=37, 38, 39, 40 など互いに深赤字の頂点が tight in-arcs を作る。

**観察 (n=53)**: 深赤字コアは **自分同士** で tight 弧を張り、大きな o で互いの m を相殺している。SCC の 32 頂点は、この深赤字コア + 隣接 keystone (m=0..1 の頂点 18, 36 など) をすべて含む。

**n=50 vs n=53 の対比**: n=53 は少数の頂点に赤字が集中 (m=-15 も出る) → tight SCC も大きい。n=50 は赤字を **薄く広く分散** (m ∈ [-5,0]) → tight SCC は 21 頂点で相対的に小さいが構造は類似。両者とも「tight SCC 上での Σm + Σo = 0 恒等式」を持つ。

### A-4: pure-ring 単体テスト (`test_pure_ring.py`) — PASS

n=24, k=3, t=8 の pure-ring で全前進弧の α を計算し **理論値と一致**:

- 全 cross-layer forward 弧が **tight** (192/213 本):
  - pure→pure: 3 本 (層跨ぎ)
  - pure→impure: 21 本, impure→pure: 21 本, impure→impure: 147 本 — 全て α=0
- intra-layer impure→pure 弧: α = t = 8 (nontight, 21 本)

**注**: ユーザの想定「impure→impure でのみ α=0」より広く、**全 cross-layer forward 弧が tight**。numpy 実装と pure-python 実装が完全一致 (`cross_check` 通過)。

---

## Part B: LP 下界実験

### モデル

M_{n,c} = excess2_search.build の LP 緩和:

- `a[i,j] ∈ [0,1]` (i≠j), `a[i,j]+a[j,i] ≤ 1`
- `out[v] = Σ a[v,j] ≥ 8`
- `s[v,w] ∈ [0,1]`, `s[v,w] + a[v,w] ≤ 1`
- `s[v,w] ≥ a[v,y] + a[y,w] - 1 - a[v,w]` for each y (`AddBoolOr` を線形化)
- `ex[v] ≥ Σ_w s[v,w] - out[v] + 1`
- 目的: min Σ ex[v]

**弧不等式 family (Big-M)**:
- `o[u,v,w] ∈ [0,1]` McCormick で `y ≤ a_uw, y ≤ a_vw, y ≥ a_uw+a_vw-1`
- 各順序対 (u,v): `Σ_w s[u,w] - out[v] + Σ_w o[u,v,w] + n(1-a[u,v]) ≥ 0`
- `a[u,v]=1` の時のみ弧不等式が forced、`a[u,v]<1` では緩和

### 結果 (n=12..20, GLOP)

| n  | base LP obj | +arc-ineq LP obj | 備考 |
|---:|:-----------:|:---------------:|:-----|
| 12..16 | INFEASIBLE | INFEASIBLE | 総 arc n(n-1)/2 < 8n で min-out=8 が LP でも矛盾 |
| 17 | 0.0 | 0.0 | vars=578→4658, cons=4539→17051 |
| 18 | 0.0 | 0.0 | vars=648→5544, cons=5409→20403 |
| 19 | 0.0 | 0.0 | |
| 20 | 0.0 | 0.0 | |

**LP は arc-ineq family を加えても excess ≥ 1 に届かない**。分数内部で `a=8/(n-1)=0.5` (n=17) 一様代入時、s=0 が feasible で `ex=0`、Big-M 弧不等式 `-8 + 0 + n/2 ≥ 0` は自明成立。整数性ギャップが非常に大きい。

### MIP (SCIP, 120s 予算) — 参考

| n  | status | obj (UB) |
|---:|:------:|:---:|
| 17 | FEASIBLE | 17 (未証明) |
| 18 | FEASIBLE | 17 |
| 19 | FEASIBLE | 25 |
| 20 | FEASIBLE | 19 |

120s では OPTIMAL に至らず、真の integer min-excess は不明。LP-MIP 整数性ギャップ ≥ 17。

### 双対解ダンプについて

LP obj = 0 のため exc≥2 到達なし。双対は非自明ではないので今回はスキップ。

---

## 非目標

証明の主張はしない。以下は測定と観察のみ:

- Part A: n=53 witness 上に **32 頂点の tight-SCC** という組合せ的な等式構造がある。ここで `Σ m + Σ o = 0` が恒等式として成立。
- Part B: 弧不等式の **Big-M LP 埋め込み** はカット強度が不足。今後有望と思われるのは (a) LP の tournament 制約 (a+a=1 for pairs)、(b) clique/odd-cycle cuts、(c) 直接 SDP-relax 等。

## 成果物 (manifest)

| ファイル | SHA-1 |
|---|---|
| slack_lib.py | 17c15a532da62f9f371176d8b77d3d816729a43b |
| test_pure_ring.py | 97e50eff76fd2ae202805c3ea3f01347cffc95ec |
| analyze_witness.py | 389baefb5d7292ece4f822b14293ec4fe44e9fe7 |
| lp_excess.py | b1f2f76c8c92ce0263bbe65e6ba30b648cfc2275 |
| mip_excess.py | 1b3eca1c7704e364b40f21f15e3af06fd776a4ce |
| slack_n53_ca40b396.json | baecdf7720447e876667095c8f3ee7db0055c46b |
| slack_n50_17cd7dc8.json | 6eae528cad280b2077821e6cf7519dcb202261ac |
| lp_excess_results.json | 33edc65d3e401739effd0b3a1bea11b6e96cf9de |
| mip_excess_results.json | dd6ef8b0a4841bb1abe8c8d5ee0a42d08c5be1a2 |

### 再現

```
python3 data/beast_trail/test_pure_ring.py           # Part A-4
python3 data/beast_trail/analyze_witness.py <path> <label>   # Part A-1..3
python3 data/beast_trail/lp_excess.py --nmin 17 --nmax 20
python3 data/beast_trail/mip_excess.py --nmin 17 --nmax 20 --time-limit 120
```
