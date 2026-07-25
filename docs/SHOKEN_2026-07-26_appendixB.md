# 所見: Appendix B 全面書き直し(release/v0.2.0、HEAD eab421a)

日付: 2026-07-26 / 監修: kanshu(新規クリーン文脈、起草側の会話ログ不参照)
対象: `note/measuring-the-moat.tex` Appendix B(B.1〜B.7)と Theorem 4.1 の
computer-assisted 明示、および同時変更5点(記法 E_{≥d}、正の下界への言い換え、
Prop 3.1 非空性、§5.2 見出し、表紙脚注)。
根拠物: `blowup/`、`data/blowup/`(e4 同梱後)、`make verify-t9` 再実行、
内部リポジトリ(読み取りのみ)。

---

## 1. 要旨

**Appendix B 本体: 受理(文言条件4件、いずれも局所)。数学は B.1〜B.7 の全補題を
再導出して隙間なし、数値は全て監修の独立再計算・独立実装で一致した。**
**同時変更: 5点中「note に実際に反映されたのは記法と Appendix B のみ」。
残り3点+下界の言い換えは README にだけ入り、tex/PDF は旧文のまま**(コミット
37008bb のメッセージは「改めた」と記すが、成果物に無い — 乖離ゲート違反そのもの)。
公開可否: **Appendix B は公開品質。note 全体はこのままではタグ付け不可**、
ただし残件は全て散文の局所修正である。

## 2. 主張別所見表

| # | 主張 / 審査点 | 判定 | 根拠(1行) |
|---|---|---|---|
| B-1 | Lemma B.1(well-formedness、deg⁺ = S₁(a)+min(j,c_a)、δ⁺ = min_a S₁(a)) | **受理** | 全行再導出。loop/digon/連結性の3論点とも閉じる。(T) が指数を下げるので逆弧不能、(R)+(R) 逆対は H の digon に還元 ✓ |
| B-2 | Lemma B.2(N⁺⁺ = ∪_{c∈C(a)} C_c、margin = Δ_a − min(j,c_a)) | **受理** | a ∉ B(a) の一歩は正しい(a∈B(a) ⇔ H に digon)。削除集合(⊂ C_a ∪ ∪_{b∈A(a)}C_b)と残存集合(⊂ ∪_{c∈C(a)}C_c)の非交差は C(a)=B\A と a∉B(a) から従う。被覆側は n_b ≥ 1(クラス非空、定義で保証)を使う — 明示されていないが定義に含まれる。ランダム300例のファジングで margin 公式に反例なし(§3-2) |
| B-3 | Lemma B.3(cap 最適性、g の閉形式) | **条件付き受理** | 閉形式・鞍着点・最小化子はすべて正しい(全 cap 総当たりとの照合300例一致)。ただし証明の一文「Increasing c_a by one **replaces one contribution**」は不正確: c→c+1 で変わるのは位置 j ≥ c+1 の **n_a−c−1 個**の寄与(各々弱減少)。結論は各位置単調性で立つ。一文の修正を条件とする(C1) |
| B-4 | Lemma B.4(有限 regime、E=3 の表) | **受理** | g(Δ,ν) ≥ Δ+1 と ν-飽和の両単調性を再導出。E=3 の表 NEG/D0M/D1S1/D1M/D2S1 = 0/1/2/3/3 は g の直接評価で網羅・正確(g(2,2)=5, g(3,·)≥4 の脱落も正しい)。**列挙単位 (Δ_a, min(n_a,Δ_a+1)) の主張は正当** — g はちょうどこの対の関数。budget 4 では D1S1 を含む可行 hit が実在する(166件、§3-6)ので ν 分割は飾りではない。なお本文の例 [8,1,7,8] の size-1 クラスは NEG であり ν 分割 regime の実例ではない — 誤読を招く(C2) |
| B-5 | Lemma B.5(bound 導出、s′ の3性質と B) | **受理** | 3性質すべて成立。q ∈ conv(V) が頂点でない場合も 1ᵀq ≤ max_V 1ᵀv(線形汎関数の凸結合上の最大)で閉じる。暗黙の前提「1ᵀr_i ≥ 0」は P ⊂ 非負象限 ⇒ 後退錐 ⊂ 非負象限から従う — 一句の明示を推奨(C3)。コードは top を floor しており散文の B 以下(両方 valid、実測 max B=222/224 はコード側の値) |
| B-6 | Lemma B.6(soundness、有界探索→全 n) | **条件付き受理** | 論理は閉じる: exc ≤ E ⇒ Σg ≤ E ⇒ 実現 regime 割当(コスト = Σg ≤ E)は列挙済み ⇒ s ∈ P ⇒ B.5 で同剰余の整数点が B 以下に存在。**向き**: 有界 ILP の INFEASIBLE(健全側)+ B.5 の完全性で「全 n で不能」— 向きの誤りなし。FEASIBLE 側は 73/73 の外部再採点で担保。ただし補題の文「decides … whether a member of F with excess at most E … exists」はインスタンス単体に対しては過大(単体の INFEASIBLE が排除するのは**その regime 割当を実現する** member のみ。網羅性は割当全列挙との合接で出る)。「a member realising that regime assignment」への語修正を条件とする(C4) |
| B-7 | Prop B.7(conserving quotient の手計算) | **受理** | 両不等式を再導出: Σ_{a∈S}Δ_a = −Σ_{a∉S}Δ_a ≥ m−|S|(S 外は Δ ≤ −1)✓、exc ≥ Σ_{a∈S}(Δ_a+1) = |S|+Σ_{a∈S}Δ_a ≥ m(B.4(i)、S 外の寄与 ≥ 0)✓。列和の恒等式(column c of N sums to |{a:c∈C(a)}|−deg⁻(c))も再導出。**「4,313 中 7 個(1,1,2,3)」は監修自前の C 実装(商リスト不使用、全 orientation 列挙+定義からの conserving 判定)で完全一致**(§3-3) |
| B-8 | B.6 の数値(385,695 / 385,622 / 73 / max B 222 / 1,052,936 / 1,051,964 / 972 / 899 / 224 / 2,321,385 / 357 / 146) | **受理** | 全数値一致: (i) instances 2値は regime 表×自前商数から**算術的に導出一致**(§3-1)、(ii) summary 行・hit 行の再集計一致、公開 e4 は内部一次記録とバイト同一(§3-4)、(iii) verify-t9 再実行で 73/73・2,321,385・357・146 全再現(§3-5)。文言条件2件: 「all 357 irreducible elements of the recession cones」は検査自身が明記する箱 [0,10] の限定が note 側に無い(C5)、新設の「every figure quoted in this subsection is a field of the summary row」は cross-check 段落の 2,321,385/357/146 に当てはまらない(C6) |
| B-9 | Theorem 4.1 の computer-assisted 表示の強度 | **受理** | 適切。手証明部(B.1〜B.5、B.7)が有限決定問題への還元を完結させ、ソルバーの寄与は「明示的に有界なインスタンスの判定」に限定。「the only thing taken on trust is the solver」は正確(LP-empty 385,622 は厳密整数演算の double description であり、実はソルバー信頼すら不要 — 主張より強い)。外部レビューの5論点(N の実体、2変数依存、有限 regime、剰余条件、被覆)はすべて本文だけで検査可能になった |
| S-1 | 記法 E_{≥d} への全面変更 | **差し戻し(D1)** | 旧記法の残存はゼロ(grep 確認)。しかし**添字 d と束縛変数 δ が不一致のまま**: abstract(l.52–53)「Let $E_{\ge d}(n)$ be … out-degree at least $\delta$」、定義部(l.111–112)「$E_{\ge d}(n) = \min\{… \delta^+(G) \ge \delta\}$」。d はどこにも束縛されない。最頻出記号の定義部での取りこぼし |
| S-2 | 「正の下界がない」への言い換え | **差し戻し(D2)** | README のみ反映。note は abstract「No lower bound is known at any n ≥ 18」(l.62)、§3.2「Nothing, at any n ≥ 18」(l.457)、Open problems(l.679)が旧文のまま — 自明な ≥0 がある以上、文字どおりには偽で、外部レビューの指摘が未解消 |
| S-3 | Prop 3.1 の非空性の一文 | **差し戻し(D3)** | tex に無い(circulant/cyclic/rotational を grep、PDF も確認)。README にも無い。クラスが空なら min は 2k+1 にならないので、これは磨きではなく**min 主張の実際の隙間**(前回所見 §6-3 で指摘済み、37008bb で「追加した」と記されたが未実施) |
| S-4 | §5.2 見出し改名(non-attainment / false pattern inference) | **差し戻し(D4)** | README のみ。note は \emph{Too high.}/\emph{Too low.} のまま(l.599, 611)。しかも同節の新しい導入文「The two failures below **differ in kind, not in direction**」と、直後の方向名ラベルが**同一文書内で直接矛盾**。Contributions 第4項「wrong in both directions」(l.156–157)も abstract の新文「overstated … in every discrepancy」と矛盾。改名自体の妥当性は認める: 両事例とも到達値は上界の上side(48/50: 13,20 vs 3,5; 59/61: 7 vs 4)で、種類(未到達 vs 偽パターン推論)の区別が正しい軸 |
| S-5 | 表紙脚注の変更 | **差し戻し(D5)** | note は旧文「no claim of that version became false.」(l.42–43)のまま。README(l.5)だけ新文。新文言自体は過小でも過大でもなく適切(数値的不等式は全て存続、撤回されたのは記号・語法・解釈 — v1.1 の「floor 7 at n=59」級の読みは撤回対象なので旧文は防御しにくい)。現状は**note と README が別のことを言っている**状態で、どちらか一方より悪い |

## 3. 再計算ログ(監修の独立実行)

### 3-1. instances 2値の算術的導出(regime 表 × 商数のみから)

```
$ python3 <<'EOF'   # dp: コスト multiset {0:1, 1:1, 2:1, 3:2, (4:1)} を m クラスに割当
Q={3:1,4:4,5:76,6:4232}; ...
EOF
budget3 instances: 385695 (note claims 385695)
budget4 instances: 1052936 (note claims 1052936)
```
regime 表が1つでも欠け/過剰ならこの2値は一致しない。表の網羅性の裏取りを兼ねる。

### 3-2. 73 witness のゼロから再採点+公式のファジング(監修自前実装、リポジトリのコード不使用)

```
$ python3 scratchpad/indep_witness.py
[1] hits re-scored from scratch: 73/73 pass (excess==3, delta+>=8, oriented,
    strongly connected, 3|n)
[2] random blow-ups: 300 trials, 0 failures (margin formula + closed-form min
    over caps)
```
[2] はランダム強連結 oriented H(m=3..5)・ランダムサイズ・**全 cap 格子の総当たり**
に対し、Lemma B.2 の margin 公式(ランダム cap で全頂点照合)と Lemma B.3 の
min_c Σ X = Σ g を突き合わせたもの。

### 3-3. 商の列挙と conserving 判定(監修自前 C 実装、商リスト・nauty 不使用)

```
$ cc -O2 -o enum_quotients enum_quotients.c && ./enum_quotients
m=3: strongly connected oriented graphs up to iso = 1,    conserving = 1
m=4: strongly connected oriented graphs up to iso = 4,    conserving = 1
m=5: strongly connected oriented graphs up to iso = 76,   conserving = 2
m=6: strongly connected oriented graphs up to iso = 4232, conserving = 3
```
4,313 = 1+4+76+4,232、conserving 7 = 1+1+2+3。Prop B.7 の数値と一致。

### 3-4. 公開データの再集計と出所照合

```
summary(e3): instances 385695, lp_empty 385622, int_infeasible 0, feasible 73,
             unknown 0, max_B 222   # 385622+0+73 = 385695 ✓
hits(e3): 73件、excess 全て3、profile は D0M×3+NEG のみ、residue 1/2 は全て null
summary(e4): instances 1052936, lp_empty 1051964, feasible 972, unknown 0, max_B 224
hits(e4): 972件、excess {3:73, 4:899}、excess4 は剰余 0/1/2 全部で実現、
          excess3 は剰余 0 のみ、min n = 24
published e4 == 内部一次記録: sha1 一致(バイト同一)
```

### 3-5. `make verify-t9` 再実行(4検査)

```
[A] witnesses re-scored: 73/73 agree
[B] 2,321,385 excess evaluations over 4313 quotients at N in [25,26,28,29,31,32], 78s
    excess <= 3 with 3 nmid N: 0 found
[C] 73 distinct patterns, 357 irreducible cone elements in [0,10]
    largest coordinate 6 (box 10); elements with 1^T h != 0 mod 3: 0
[D] 73 patterns x residues {1,2} = 146 models, coordinates <= 40
    feasible at residue 1 or 2: 0; UNKNOWN: 0
  A: pass  B: pass  C: pass  D: pass
```
`make verify-all` も再実行し green(77 witness、failures 0)。

### 3-6. hit #2(m=4)の多面体を手で解き直し(Lemma B.5 の実地照合)

H=[[0110],[0011],[0001],[1000]]、profile [D0M,NEG,D0M,D0M]。制約を解くと
s₀=s₃=s₁+s₂、Δ₁=−s₂≤−1、s₁+s₂≥8。頂点 (8,1,7,8) と (8,7,1,8)(各 1ᵀq=24)、
射線 (1,1,0,1) と (1,0,1,1)(各 1ᵀr=3)。B = 24+3·(3+3) = **42** —
記録の B=42, vertices=2, rays=2 と一致。witness [8,1,7,8] は頂点そのもの。
あわせて hit #1(C₃)は暗算で B = 24+3·3 = 33 ✓。
budget-4 hit の profile 語彙: D0M 972 / NEG 969 / D1M 590 / **D1S1 166** —
ν 分割 regime に実在の可行例があることを確認(B-4 の裏取り)。
min Σn_a の4値(m=3..6 で 24,24,20,20)も全商×格子 [1,8]^m で再計算し一致。

## 4. 反駁の試みと結果

1. **「cap が第2近傍を変え、margin 公式が破れる」筋** — ランダム H・サイズ・cap の
   300例で全頂点の margin を BFS 定義から照合(§3-2)。反例なし。B.2 の証明どおり
   (T) の到達先の out-set は観測者の N₁⁺ に包含される。**失敗**。
2. **「E=3 の regime 表に漏れがあり、可行例が列挙外に落ちる」筋** — 表が違えば
   instances の2値(385,695 / 1,052,936)が商数×dp と一致しえないが一致(§3-1)。
   また g の直接評価で cost ≤ 3 の (Δ,t) 対は表の5行で尽きる。**失敗**。
3. **「B の導出が頂点でない q や負の射線和で破れる」筋** — 1ᵀq は conv(V) 上で
   頂点最大値に抑えられ、後退錐は非負象限内なので 1ᵀr ≥ 0。hit #2 で B を手で
   再導出し一致(§3-6)。**失敗**(ただし 1ᵀr ≥ 0 の一句は明示推奨 = C3)。
4. **「有界 INFEASIBLE から全 n を結論するのは向きの誤り」筋** — B.5 が「整数点が
   あれば B 以下・同剰余にもある」を厳密演算の V,R に対して与えるので、
   有界不能 ⇒ 全域不能は完全性つきの健全な向き。独立経路の検査 B(LP なしの
   全数 2,321,385)と D(剰余 1/2 の CP-SAT 146 モデル全不能)も同じ結論。**失敗**。
5. **「商の列挙(4,313)自体が誤り」筋** — 監修自前の C 実装で全 orientation を
   列挙し canonical 判定。1/4/76/4232 で一致(§3-3)。**失敗**。
6. **「n=20..23 に excess ≤ 4 の member が居て『smallest n = 24』が破れる」筋** —
   e4 の全972 hit の剰余別最小 n を再集計、最小 24(§3-4)。B.5 の完全性により
   これは有界打ち切りではない。**失敗**。

## 5. 差し戻し事項(すべて散文の局所修正、合計30分以内)

- **D1**: E_{≥d} の定義部2箇所(abstract l.52–53、定義 l.111–112)で δ を d に
  そろえる(または「write d for the bound δ」を一度置く)。
- **D2**: 「No lower bound is known」(abstract l.62)、「Nothing, at any n ≥ 18」
  (§3.2 l.457)、Open problems(l.679)を README と同じ「no positive lower
  bound / nothing beyond the trivial ≥ 0」系へ。
- **D3**: Prop 3.1 に非空性の一文(Z_{2k+1} 上の巡回トーナメントが witness)を追加。
  これは min 主張の実際の隙間であり、前回所見 §6-3 の再掲。
- **D4**: §5.2 のラベルを README と同じ Failure by non-attainment / Failure by
  false pattern inference に。あわせて Contributions 第4項の「wrong in both
  directions」を abstract の新文と整合させる。
- **D5**: 表紙脚注を README l.5 の新文言(All proved inequalities … remain valid;
  corrects notation, interpretation and provenance)に差し替え。
- 修正後の再監修はフル審査不要 — 上記5点の diff と PDF 再抽出の確認で足りる。

**文言条件(Appendix B 内、受理の条件)**:
- **C1**(B.3 証明)「replaces one contribution」→ 変わるのは j ≥ c+1 の n_a−c−1 個
  (各々弱減少)である旨に修正。
- **C2**(B.2 末尾)[8,1,7,8] は「size-1 クラスの実例」であって ν 分割 regime の
  実例ではない(その size-1 クラスは NEG)。budget-4 で D1S1 の可行 hit が
  166 件ある事実を挙げる方が主張に合う。
- **C3**(B.5 証明)最後の不等式に「1ᵀr_i ≥ 0(P が非負象限内ゆえ)」の一句を。
- **C4**(B.6 の statement)「whether a member of F … exists」→「whether a member
  **realising that regime assignment** exists」。
- **C5**(B.6)「all 357 irreducible elements of the recession cones」に検査自身が
  明記する箱 [0,10] の限定を付す(検証器の docstring は Hilbert 基底の証明では
  ないと明言している。cross-check なので限定付きで十分)。
- **C6**(B.6 新設文)「every figure quoted in this subsection is a field of the
  summary row」は cross-check 段落の 2,321,385/357/146 には当てはまらない。
  「quoted in this paragraph」等へ縮める。

## 6. 理論所見(提案、拘束力なし)

- **B.5 は Hilbert 基底なしで剰余保存を出す設計が良い**(自信度: 高)。周期 3 の
  剰余だけが要るので 3⌊μ/3⌋ の減算で足り、Normaliz 級の道具を持ち込まずに
  「全 n」へ持ち上がる。この形は ch/ 側の周期的 blow-up 族にもそのまま移植できる。
- **int_infeasible = 0(両 budget)は偶然ではない可能性**(自信度: 低)。
  LP 非空 ⇒ 整数点ありが全インスタンスで成立している。N と M₁ の行が {−1,0,1} で
  構造が強く、系が整数性の良い性質(全単模に近い何か)を持つ疑いがある。証明できれば
  CP-SAT 依存が消えて Theorem 4.1 から computer-assisted の但し書きの一部が外せるが、
  現状の主張には不要(追う価値は低め)。
- **「m=3 は classical hand computation」の一句**(自信度: 中)は exc ≥ 3 のみを
  指すと読める書き方になっているが、C₃ の 3|n 強制も実は手で閉じる(δ≥8 で全クラス
  ≥8 ⇒ Δ≥1 のクラスは g ≥ 3 単独負担、Σ Δ=0 と |S|+Σ_S Δ ≥ 3 の等号解析で
  Δ=(0,0,0) のみ残る)。一文足せば m=3 は完全に計算機フリーになる。

## 7. 資源配分への意見

- 次に使うべきは **D1〜D5 の反映(人手30分)+ 反映後の diff 確認(監修10分)**。
  計算資源は不要。Appendix B 本体に追加計算の必要はない — 数値は3経路
  (算術導出・再集計・verify-t9)で既に閉じている。
- タグ付け前に一度だけ `pdftotext` で「Too high / no claim of that version /
  No lower bound is known」の3文字列が消えたことを機械確認することを推奨
  (今回の乖離は全てこの1コマンドで検出できた)。
- iryu への追加往復は不要。外部レビューの5論点は B.1〜B.7 で全て本文内から
  検査可能になっており、これ以上は費用対効果が立たない。

## 付記(作業環境)

- 監修の作業ファイル(enum_quotients.c、indep_witness.py 等)は全てセッション
  scratchpad(/private/tmp/claude-501/…/scratchpad/)にあり、**本リポジトリにも
  内部リポジトリにも作業ファイル・ビルド生成物は残していない**(git status clean、
  find で確認)。make 実行により gitignore 済みの __pycache__ が再生成された以外の
  副作用なし。
