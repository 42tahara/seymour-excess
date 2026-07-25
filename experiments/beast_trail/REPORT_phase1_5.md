# 獣道 phase 1.5 — 恒等式再検証と系候補の測定

## サマリ

**P0 (差し戻し)**: phase 1 の主張「tight SCC 上で Σ_{v∈SCC} m(v) + Σ_arcs o(u,v) = 0」は **偽**。実測 (n=50) 87, (n=53) 1478。正しい重み付き恒等式

$$
\sum_u d^+_T(u)\,m(u) \;+\; \sum_u d_1(u)\,(d^+_T(u) - d^-_T(u)) \;+\; \sum_{arc\in T} o(u,v) \;=\; 0
$$

は両 witness で **exactly 0** を実測 (T = tight-弧集合)。tight SCC は Eulerian でなく、d±_T の非対称が identity の主要項。

**P1**: 全 witness で T/|E| を測定。exc=5..9 の 5 witness で **T/E = 4.71 〜 8.26** — 系候補 (exc≤1 で T/E ≳ 1) の閾値を大幅に超過。pure-ring (exc=3) で T/E=1.58 と最下限。

**P2**: pure-ring の α ∈ {0, t} 二値性は **全弧で確認**。実 witness の双峰は「骨格 (低α)」vs「射撃 (高α)」の帰属が数値的に見え、**高α帯の終点は tight-SCC / keystone に 1.2〜1.7 倍集中**。特に n=53 では高α弧の src=深赤字が 42%、Δd1 支配。

---

## P0: 恒等式の再検証

### 誤主張と修正

phase 1 で「tight SCC 上で `Σm + Σo = 0`」と書いた。この式は「tight-弧集合が Eulerian かつ SCC を Hamiltonian に走る (∀v: d⁺_T(v)=d⁻_T(v)=1)」時にしか成立しない。実際の tight SCC はこれを **満たさない**。

### 正しい恒等式 (α=0 の telescoping から必然)

任意の弧集合 A の全弧で α=0 なら
$$
0 = \sum_{(u,v)\in A} \alpha(u,v) = \sum_u d^+_A(u)\,m(u) + \sum_u d_1(u)(d^+_A(u) - d^-_A(u)) + \sum_{(u,v)\in A} o(u,v)
$$

### 実測 (`p0_identity_results.json`)

**n=50 (17cd7dc8)** — tight SCC: 21 頂点, 87 tight arcs 内部
| 量 | 値 |
|---|---:|
| 単位 Σ m (SCC) | **−28** |
| 単位 Σ o (SCC arcs) | 115 |
| **単位 identity 値** (should be 0 only if Eulerian+Hamil) | **87** |
| 重み Σ d⁺_T · m | −114 |
| 重み Σ d₁·(d⁺_T−d⁻_T) | −1 |
| 重み Σ o | 115 |
| **重み identity 値** (must be 0) | **0** ✓ |
| d⁺_T 分布 | {3:4, 4:10, 5:7} |
| d⁻_T 分布 | {3:5, 4:8, 5:8} |
| Eulerian? | No |

**n=53 (dc922e89)** — tight SCC: 32 頂点, 335 tight arcs 内部
| 量 | 値 |
|---|---:|
| 単位 Σ m (SCC) | **−163** |
| 単位 Σ o (SCC arcs) | 1641 |
| **単位 identity 値** | **1478** |
| 重み Σ d⁺_T · m | −1611 |
| 重み Σ d₁·(d⁺_T−d⁻_T) | −30 |
| 重み Σ o | 1641 |
| **重み identity 値** | **0** ✓ |
| d⁺_T 分布 | {8:11, 11:13, 13:8} |
| d⁻_T 分布 | {8:13, 11:8, 13:11} |
| Eulerian? | No |

**n=53 の d± 分布に興味深い規則性**: d⁺_T, d⁻_T 共に値集合が **{8, 11, 13}** のみ (3 種類)。全体は 3-block 由来の可能性 (n=53 witness は sizes=[18,18,17] の 3 ブロック構築)。

### 閉路被覆

Tight SCC は「d⁺_T の重み付き Eulerian 経路分解」を持つが (Σ 出 = Σ 入 = |A|)、単純閉路被覆で全弧を分割することはできない (Eulerian 条件が破れているため)。従って**重み付き恒等式が「唯一の」テレスコープ形式**。

---

## P1: 大域和 & T/|E| 表

全弧の α ≥ 0 から
$$
\sum_{arcs} \alpha = \sum_v m(v) d_1(v) + \sum_v d_1(v)(d^+(v) - d^-(v)) + T \;\ge\; 0
$$

`identity_gap` 列は上式が実測で厳密成立するかの sanity check (全ケース 0)。

| label | N | \|E\| | exc | T | **T/\|E\|** | Σm | Σm·d₁ | Σd₁(d⁺−d⁻) | Σα | gap |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| pure_ring (k=3, t=8) | 24 | 213 | 3 | 336 | **1.577** | −21 | −189 | 21 | 168 | 0 |
| n47 (ad1a1ee5) | 47 | 862 | 9 | 4799 | 5.567 | −50 | −983 | 472 | 4288 | 0 |
| n49 (ead3c3c3) | 49 | 758 | 6 | 4349 | 5.737 | −73 | −1222 | 452 | 3579 | 0 |
| n50 (17cd7dc8) | 50 | 639 | 5 | 3317 | 5.191 | −77 | −1036 | 354 | 2635 | 0 |
| n53 (dc922e89) | 53 | 1201 | 5 | 9916 | **8.256** | −224 | −6020 | 1661 | 5557 | 0 |
| n59 (c44e402b) | 59 | 738 | 7 | 3476 | 4.710 | −92 | −1231 | 345 | 2590 | 0 |

**観察**:
- 全 exc≥3 witness で T/E > 1.5、系候補閾値を大きく超過
- pure-ring は最下限 (1.58) — 構造が疎で α=t の高α弧が少数
- n=53 は最大 T/E (8.26) — 密 (E/N=22.7) で推移三角形が多い
- **exc≤1 で本当に T/E ≳ 1 が forced か** は今回のデータでは分からない (全 exc ≥ 3)。exc=1 相当の "薄いテスト" は Part B (LP) や、より小 n の pure-ring 派生で見るのが筋

---

## P2: 双峰帰属と pure-ring α∈{0,t} 単体テスト

### pure-ring 二値性テスト — PASS

```
pure_ring(k=3, t=8): alpha in {0, 8} with counts {0: 192, 8: 21}
```

全 213 弧について α ∈ {0, 8} を確認 (cross-layer→0, intra-layer impure→pure→8)。

### 実 witness の双峰帰属

n=50 の gap = (6, 10)、n=53 の gap = (4, 17) で分類:

#### n=50 (17cd7dc8)
| band | arcs | src∈SCC | src=keystone (m≥0) | term∈SCC | term=keystone |
|---|---:|---:|---:|---:|---:|
| 低 α ≤ 6 | 462 | 45.5% | 10.8% | **42.0%** | 10.2% |
| 高 α ≥ 10 | 177 | 15.8% | 0% | **70.6%** | 23.7% |

高α帯は src が SCC 外 (84%) から term = SCC 内 (71%) に集中。**「SCC 外の疎な頂点から SCC 内へ射撃」**。

#### n=53 (dc922e89)
| band | arcs | src∈SCC | src=keystone | src=深赤字 | term∈SCC | term=keystone | term=深赤字 |
|---|---:|---:|---:|---:|---:|---:|---:|
| 低 α ≤ 4 | 936 | 60.7% | 7.4% | 17.3% | **60.4%** | 7.7% | 16.9% |
| 高 α ≥ 17 | 265 | 60.4% | 0.8% | **41.9%** | **73.6%** | 20.4% | 3.0% |

- 高α帯は src が **深赤字** 42% (低α帯 17% の 2.5 倍)、term=深赤字が 3% (低α帯 17% の 1/6)
- **高α = 深赤字 (d1 大) から d1 の小さい tight-SCC / keystone への「射撃」**
- α = m(u) + d1(u) − d1(v) + o(u,v) で m(u) は負なので、d1(u)−d1(v) の項が大きい時に α が大きい

### 骨格/射撃解釈のまとめ

- **骨格** (低α, tight-SCC の内部+隣接): 重み付き恒等式に寄与、証明の主要な組合せ構造
- **射撃** (高α, SCC/keystone を的にした余剰弧): 各 witness の "スラック" — カット/緩和で除去できる可能性

---

## 非目標 (再掲)

証明主張はしない。以下は測定と観察:

1. tight-SCC 上の正しい恒等式は **重み付き** (d⁺_T, d⁻_T 荷重)。単位重み版は成立しない。
2. T/|E| は phase 1 witness 群で 1.58 〜 8.26 の範囲。系候補は satisfied で余裕あり。
3. 双峰α は「射撃 = 深赤字→SCC」構造に帰属可能。pure-ring の α ∈ {0, t} 二値性が最も清潔。

## 成果物 & SHA-1

| ファイル | SHA-1 |
|---|---|
| p0_identity.py | b48d75422b0abb07f4bb682431563d12d0e011e6 |
| p0_identity_results.json | 4f227164d1e13878aa9ac1b7a885d62f1360e6df |
| p1_global_sums.py | a17a67e353b5cb74ef646b942b690a3615fb7ad5 |
| p1_global_sums.json | 2d382d1a6a0cb8a4e4cc696b832d5aceaed88d14 |
| p2_bimodal.py | c0d6f7b35ae76e92b6a57910aab032002143dd89 |
| p2_bimodal.json | e3c95cbf1661f4c0961ce7bdac6016084823b851 |

### 再現

```
python3 data/beast_trail/p0_identity.py    # 恒等式検証
python3 data/beast_trail/p1_global_sums.py # T/|E| 表
python3 data/beast_trail/p2_bimodal.py     # 双峰帰属 + pure-ring 二値テスト
```
