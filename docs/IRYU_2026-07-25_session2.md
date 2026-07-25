# 異流審査(iryu)記録 その2 — 2026-07-25(iryu エージェント経由、2ラウンド)

[IRYU_2026-07-25_t8_t9.md](IRYU_2026-07-25_t8_t9.md) とは**別の codex セッション**。
同じ2課題を独立に走らせた2本目にあたる。**正典 §2-5 により出力は仮説であって証拠ではない。**

- codex session id: `019f99a4-4a75-71f2-a532-9eec018178c3`
- model gpt-5.5 / reasoning effort medium / sandbox read-only / リポジトリ外の隔離ディレクトリ
- 相手は Python で全探索・MILP・ランダム探索を実行して回答した
- 初回2投は `codex exec` の stdin 未クローズで停止。`< /dev/null` で解消(正典 `agents/iryu.md` に反映済み)

## この2本目で新たに得られたもの

| 内容 | 位置づけ |
|---|---|
| **族の最小 n = 20** を scipy MILP で算出: m=3,4,5,6 → **24, 24, 20, 20** | **依頼側の ortools CP-SAT と完全一致**(別実装・別ソルバー)。1本目の codex も同値を出した |
| n=20 の商(m=5 回転トーナメント、全クラス4)の **c 全探索 5⁵ = 3,125 通り**: 最小 S = **5**。分布 S=5:1024 / 8:1280 / 11:640 / 14:160 / 17:20 / 20:1(和 3,125) | **n=20 は 3∤n なので、ここに S=3 が出れば主張本体の反例だった。出なかった。** ただし探索であって証明ではない |
| n=21,22,23 の探索最良 S = 6 | 網羅でない。相手も明示的に留保 |
| n=24〜30 のランダム探索 50万試行で反例なし。S=3 が出たのは n=24, 27, 30 のみ(すべて 3∣n) | **反証の失敗。確定の材料にならない** |
| 既知性の帰属先は **Landau の定理**(「トーナメントの最大得点頂点は king」) | 引用 URL は未検証と相手自身が留保。**一次文献の照合が別途必要** |
| n=20 商の S の規則性: **S = 5 + 3·#{a : c_a = 0}**、度数 C(5,z)·4^(5−z) | 閉形式 B 導出の検算素材になり得る(未使用) |

## 相手の主張のうち疑わしい点(iryu エージェント自身の申告)

1. 引用 URL(paperzz / math.stackexchange)は web 検索経由で実在・内容一致が未検証
2. m=6 の最小 n=20 は MILP 出力のみ。m=5 の 20 は手算で追認済み
3. n=21〜23 の最良 S=6、n=24〜30 の探索は網羅的でない
4. round 2 冒頭の「厳密に確認できます」は下界側が MILP 依存なので過大。厳密なのは上界側(n=20 の例の存在)だけ

## 依頼側の扱い

- **n=20 が最小**という結論は、依頼側の ortools CP-SAT・codex の scipy MILP・本セッション1本目の codex の**3経路で一致**し、n=20 の強連結 witness を公開検証器で確認した。README にはこの根拠で書いた
- ただし**論法そのもの**(トーナメント還元と強連結性の落とし、どちらも量化子の向きを使う)の検証は kanshu に依頼済み。**量化子の誤りはこの形で死ぬ**
- 探索由来の値(n=21〜23、n=24〜30)は**公開文に一切入れていない**

---

## Round 1 プロンプト(全文)
```
あなたには2件の独立した課題を検討してもらいます。誤りを探すことが任務です。誤りが無いなら「無い」と述べ、根拠を示してください。

---

## 課題 1 — 命題の反証と、既知性の判定

以下の設定と主張を検討してください。

**設定.** 有限有向グラフ D は、ループを持たず、どの2頂点も両方向の弧で結ばれない（各非順序対が担う弧は最大1本）とします。頂点 v について A(v) を「v から弧1本で到達できる頂点の集合」、B(v) を「v からの最短有向路の長さがちょうど 2 である頂点の集合」とします（定義より B(v) は A(v) ∪ {v} と交わりません）。f(v) = |B(v)| − |A(v)|、S(D) = Σ_v max(0, f(v) + 1) と置きます。

**主張.** k ≥ 1 とする。n = 2k+1 頂点の上記のような D すべてについて、全頂点の出次数が k 以上であれば **S(D) = n**。

**提示された証明.** n·k = C(n,2) であり、各非順序対の弧は最大1本、かつ弧の総数 = Σ_v outdeg(v) ≥ n·k = C(n,2) なので、等号が成立して D は全対が隣接し全出次数がちょうど k（正則トーナメント）。v を任意の頂点、w を v への弧を持つ頂点とする。w ∉ B(v) と仮定すると、A(v) の全ての y について w → y であり（全対隣接性から、w→y でなければ y→w となり w ∈ B(v) になってしまう）、よって A(v) ⊆ A(w)。さらに w → v より v ∈ A(w) であり v ∉ A(v) なので A(v) ∪ {v} ⊆ A(w)、すなわち |A(w)| ≥ k+1 > k で正則性に矛盾。ゆえに v への弧を持つ頂点はすべて B(v) に属し |B(v)| ≥ k。一方 B(v) ⊆ V ∖ (A(v) ∪ {v}) より |B(v)| ≤ n−1−k = k。よって f(v) = 0 が全頂点で成立し S(D) = n。∎

**問い.**
1. この証明に誤り・隙間はありますか。とくに「w ∉ B(v) を仮定すると A(v) の全ての y で w → y」の一歩を精査してください。
2. 主張の反例はありますか。あるなら構成を示してください。
3. **この主張は古典的に既知ですか。** 「正則トーナメントの全頂点で |B(v)| = |A(v)| が成り立つ」という形の事実に標準的な名前・出典はありますか。folklore・既知結果の言い換え・新規、のどれに分類すべきですか。
4. 出次数の下限を k から k−1 に緩めると（n = 2k+1 のまま）主張はどう壊れますか。S(D) の最小値はどうなりますか。

---

## 課題 2 — 文面だけを読んで、何が主張されているかを述べる（読解テスト）

以下は、ある論文に載せる予定の主張の文面です。**あなたはこの文面以外の文脈を持っていません。それが本課題の狙いです。**

> **定義.** H を m 頂点の強連結な有向グラフとし、3 ≤ m ≤ 6、ループも両方向弧も持たないとする。正整数ベクトル (n_1,…,n_m) と整数ベクトル (c_1,…,c_m)（0 ≤ c_a ≤ n_a）に対し、G = H[n; c] を次で定める。頂点集合は互いに素なクラス C_1,…,C_m の和（|C_a| = n_a、C_a の元を u_{a,0},…,u_{a,n_a−1} と書く）。弧は次の2種類のみ: **(R)** H に a→b があるとき、全ての j に対し u_{a,j} → C_b の全頂点。**(T)** l < min(j, c_a) なる全ての (j,l) に対し u_{a,j} → u_{a,l}。n = Σ_a n_a と置く。
>
> 頂点 v について A(v)、B(v)、f(v)、S(G) は課題1と同じ定義とする。
>
> **主張.** 上記の (H, n, c) のうち **G の最小出次数が 8 以上**であるもの全てについて、**S(G) ≥ 3** である。さらに S(G) = 3 ならば **3 ∣ n**。なおこの族は **n < 24 では空**であり（最小出次数の条件による）、主張の内容は n ≥ 24 にある。
>
> **これは、n 頂点・最小出次数 ≥ 8 の有向グラフ全体にわたる S の最小値の下界ではない。** 上記のような blow-up でない有向グラフが大多数であるため、本主張は当該クラスの外について何も述べない。

**問い.**
1. **この文面は何を主張していますか。何を主張していませんか。** あなた自身の言葉で、できるだけ厳密に述べてください。
2. 定義に穴はありますか。G が「ループも両方向弧も持たない」ことは (R)(T) から従いますか。強連結性は？ min(j, c_a) の書き方に曖昧さはありますか。
3. 「最小出次数 8 以上ならこの族は n < 24 で空」は正しいですか。検算してください。
4. **この文面を読んで、「最小出次数 ≥ 8 の有向グラフには S ≥ 3 が成り立つ」と誤読する危険はどれくらいありますか。** 最終段落は誤読を防ぐのに十分ですか。不十分なら、どう書き換えるべきですか。
5. m ≤ 6 という制限、および (T) が「切り詰めた推移トーナメント」に限られている点は、主張の射程をどれだけ狭めていますか。

---

返答は両課題について、指摘を具体的に。数値の検算は実際に行ってください。
```

## Round 1 codex 出力(全文、生ログ)
```
Reading additional input from stdin...
2026-07-25T14:18:27.294372Z ERROR codex_models_manager::cache: failed to load models cache: missing field `supports_reasoning_summaries` at line 88 column 5
OpenAI Codex v0.142.5
--------
workdir: /private/tmp/claude-501/-Users-srm-dev-conway99-funsearch/ead2d61b-ebf6-4654-abeb-2f2226dceb95/scratchpad/iryu_1784988482
model: gpt-5.5
provider: openai
approval: never
sandbox: read-only
reasoning effort: medium
reasoning summaries: none
session id: 019f99a4-4a75-71f2-a532-9eec018178c3
--------
user
あなたには2件の独立した課題を検討してもらいます。誤りを探すことが任務です。誤りが無いなら「無い」と述べ、根拠を示してください。

---

## 課題 1 — 命題の反証と、既知性の判定

以下の設定と主張を検討してください。

**設定.** 有限有向グラフ D は、ループを持たず、どの2頂点も両方向の弧で結ばれない（各非順序対が担う弧は最大1本）とします。頂点 v について A(v) を「v から弧1本で到達できる頂点の集合」、B(v) を「v からの最短有向路の長さがちょうど 2 である頂点の集合」とします（定義より B(v) は A(v) ∪ {v} と交わりません）。f(v) = |B(v)| − |A(v)|、S(D) = Σ_v max(0, f(v) + 1) と置きます。

**主張.** k ≥ 1 とする。n = 2k+1 頂点の上記のような D すべてについて、全頂点の出次数が k 以上であれば **S(D) = n**。

**提示された証明.** n·k = C(n,2) であり、各非順序対の弧は最大1本、かつ弧の総数 = Σ_v outdeg(v) ≥ n·k = C(n,2) なので、等号が成立して D は全対が隣接し全出次数がちょうど k（正則トーナメント）。v を任意の頂点、w を v への弧を持つ頂点とする。w ∉ B(v) と仮定すると、A(v) の全ての y について w → y であり（全対隣接性から、w→y でなければ y→w となり w ∈ B(v) になってしまう）、よって A(v) ⊆ A(w)。さらに w → v より v ∈ A(w) であり v ∉ A(v) なので A(v) ∪ {v} ⊆ A(w)、すなわち |A(w)| ≥ k+1 > k で正則性に矛盾。ゆえに v への弧を持つ頂点はすべて B(v) に属し |B(v)| ≥ k。一方 B(v) ⊆ V ∖ (A(v) ∪ {v}) より |B(v)| ≤ n−1−k = k。よって f(v) = 0 が全頂点で成立し S(D) = n。∎

**問い.**
1. この証明に誤り・隙間はありますか。とくに「w ∉ B(v) を仮定すると A(v) の全ての y で w → y」の一歩を精査してください。
2. 主張の反例はありますか。あるなら構成を示してください。
3. **この主張は古典的に既知ですか。** 「正則トーナメントの全頂点で |B(v)| = |A(v)| が成り立つ」という形の事実に標準的な名前・出典はありますか。folklore・既知結果の言い換え・新規、のどれに分類すべきですか。
4. 出次数の下限を k から k−1 に緩めると（n = 2k+1 のまま）主張はどう壊れますか。S(D) の最小値はどうなりますか。

---

## 課題 2 — 文面だけを読んで、何が主張されているかを述べる（読解テスト）

以下は、ある論文に載せる予定の主張の文面です。**あなたはこの文面以外の文脈を持っていません。それが本課題の狙いです。**

> **定義.** H を m 頂点の強連結な有向グラフとし、3 ≤ m ≤ 6、ループも両方向弧も持たないとする。正整数ベクトル (n_1,…,n_m) と整数ベクトル (c_1,…,c_m)（0 ≤ c_a ≤ n_a）に対し、G = H[n; c] を次で定める。頂点集合は互いに素なクラス C_1,…,C_m の和（|C_a| = n_a、C_a の元を u_{a,0},…,u_{a,n_a−1} と書く）。弧は次の2種類のみ: **(R)** H に a→b があるとき、全ての j に対し u_{a,j} → C_b の全頂点。**(T)** l < min(j, c_a) なる全ての (j,l) に対し u_{a,j} → u_{a,l}。n = Σ_a n_a と置く。
>
> 頂点 v について A(v)、B(v)、f(v)、S(G) は課題1と同じ定義とする。
>
> **主張.** 上記の (H, n, c) のうち **G の最小出次数が 8 以上**であるもの全てについて、**S(G) ≥ 3** である。さらに S(G) = 3 ならば **3 ∣ n**。なおこの族は **n < 24 では空**であり（最小出次数の条件による）、主張の内容は n ≥ 24 にある。
>
> **これは、n 頂点・最小出次数 ≥ 8 の有向グラフ全体にわたる S の最小値の下界ではない。** 上記のような blow-up でない有向グラフが大多数であるため、本主張は当該クラスの外について何も述べない。

**問い.**
1. **この文面は何を主張していますか。何を主張していませんか。** あなた自身の言葉で、できるだけ厳密に述べてください。
2. 定義に穴はありますか。G が「ループも両方向弧も持たない」ことは (R)(T) から従いますか。強連結性は？ min(j, c_a) の書き方に曖昧さはありますか。
3. 「最小出次数 8 以上ならこの族は n < 24 で空」は正しいですか。検算してください。
4. **この文面を読んで、「最小出次数 ≥ 8 の有向グラフには S ≥ 3 が成り立つ」と誤読する危険はどれくらいありますか。** 最終段落は誤読を防ぐのに十分ですか。不十分なら、どう書き換えるべきですか。
5. m ≤ 6 という制限、および (T) が「切り詰めた推移トーナメント」に限られている点は、主張の射程をどれだけ狭めていますか。

---

返答は両課題について、指摘を具体的に。数値の検算は実際に行ってください。
codex
課題 1 の「既知性」は現在の文献・用語確認が必要なので、そこだけ外部確認しつつ、数値部分は小さいケースの全探索と構成で検算します。
web search: 
web search: regular tournament every vertex distance 2 in-neighbor out-neighborhood theorem
web search: 
web search: tournament theory king vertex maximum outdegree theorem Landau Moon
codex
証明の主要部は、通常のトーナメントの “king” の議論そのものに見えます。下限を `k-1` に落とす部分は、反例の形だけでなく最小値まで聞かれているので、まず小さい `k` を全探索して式を推定します。
exec
/bin/zsh -lc 'python3 -c $'"'from itertools import product\\n\\ndef calc(n,dirs):\\n A=[set() for _ in range(n)]; idx=0\\n for i in range(n):\\n  for j in range(i+1,n):\\n   d=dirs[idx]; idx+=1\\n   if d==0: A[i].add(j)\\n   elif d==1: A[j].add(i)\\n B=[]\\n for v in range(n):\\n  r=set()\\n  for y in A[v]: r |= A[y]\\n  r.discard(v); r -= A[v]; B.append(r)\\n return sum(max(0,len(B[v])-len(A[v])+1) for v in range(n)), [len(x) for x in A], [len(x) for x in B], A, B\\nfor k in range(1,4):\\n n=2*k+1; N=n*(n-1)//2; best=999; ex=None; count=0\\n for dirs in product([-1,0,1], repeat=N):\\n  val,outs,bs,A,B=calc(n,dirs)\\n  if min(outs)>=k-1:\\n   count+=1\\n   if val<best: best=val; ex=(outs,bs,A,B)\\n print(\"k\",k,\"n\",n,\"count\",count,\"best\",best,\"outs\",ex[0],\"bs\",ex[1])\\n print(\"A\",[sorted(s) for s in ex[2]],\"B\",[sorted(s) for s in ex[3]])\\n'" in /private/tmp/claude-501/-Users-srm-dev-conway99-funsearch/ead2d61b-ebf6-4654-abeb-2f2226dceb95/scratchpad/iryu_1784988482
2026-07-25T14:19:42.345653Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 88 column 5
2026-07-25T14:19:44.718659Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 88 column 5
 exited 130 in 32490ms:
Traceback (most recent call last):
  File "<string>", line 19, in <module>
  File "<string>", line 9, in calc
KeyboardInterrupt
k 1 n 3 count 27 best 1 outs [1, 1, 0] bs [0, 0, 0]
A [[2], [2], []] B [[], [], []]
k 2 n 5 count 16168 best 3 outs [2, 2, 1, 1, 1] bs [1, 1, 1, 1, 1]
A [[3, 4], [3, 4], [3], [4], [2]] B [[2], [2], [4], [2], [3]]

codex
小さい全探索では `n=3` の最小が 1、`n=5` の最小が 3 でした。`n=7` 以降は全探索が爆発するので、ここからは一般構成と不等式で詰めます。
exec
/bin/zsh -lc 'python3 -c $'"'import random\\n\\ndef evalG(n,A):\\n B=[]; S=0\\n for v in range(n):\\n  r=set()\\n  for y in A[v]: r |= A[y]\\n  r.discard(v); r -= A[v]\\n  b=len(r); d=len(A[v]); S+=max(0,b-d+1); B.append(b)\\n return S,[len(x) for x in A],B\\n\\ndef randG(n,k):\\n while True:\\n  A=[set() for _ in range(n)]\\n  for i in range(n):\\n   for j in range(i+1,n):\\n    r=random.randrange(3)\\n    if r==0: A[i].add(j)\\n    elif r==1: A[j].add(i)\\n  if min(map(len,A))>=k-1: return A\\n\\nfor k in [3,4,5]:\\n n=2*k+1; best=10**9; bestdata=None\\n for t in range(20000):\\n  A=randG(n,k)\\n  S,outs,B=evalG(n,A)\\n  temp=1.0\\n  for it in range(500):\\n   # pick pair change among 3 states, accept if min ok\\n   i,j=random.sample(range(n),2); i,j=min(i,j),max(i,j)\\n   old = 0 if j in A[i] else (1 if i in A[j] else -1)\\n   choices=[-1,0,1]; choices.remove(old); new=random.choice(choices)\\n   A2=[set(s) for s in A]\\n   A2[i].discard(j); A2[j].discard(i)\\n   if new==0: A2[i].add(j)\\n   elif new==1: A2[j].add(i)\\n   if min(map(len,A2))>=k-1:\\n    S2,outs2,B2=evalG(n,A2)\\n    if S2<=S or random.random()<0.01:\\n     A,S,outs,B=A2,S2,outs2,B2\\n   if S<best:\\n    best=S; bestdata=(outs,B,[sorted(s) for s in A])\\n print(\"k\",k,\"best\",best,\"outs\",bestdata[0],\"B\",bestdata[1],\"A\",bestdata[2])\\n'" in /private/tmp/claude-501/-Users-srm-dev-conway99-funsearch/ead2d61b-ebf6-4654-abeb-2f2226dceb95/scratchpad/iryu_1784988482
2026-07-25T14:20:48.337730Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 88 column 5
codex
探索はまだ走っています。現時点で課題 2 の検算は式で処理できますが、課題 1 の緩和版は「最小値」を断定するには下界証明が必要なので、探索結果は構成の確認に使います。
2026-07-25T14:21:21.773773Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 88 column 5
codex
ランダム探索が長くなっているため打ち切ります。全探索済みの小ケースと、明示構成・一般下界で答えを組み立てます。
2026-07-25T14:21:26.969757Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 88 column 5
 exited 130 in 68854ms:
Traceback (most recent call last):
  File "<string>", line 25, in <module>
  File "<string>", line 17, in randG
  File "/Users/srm/.local/share/mise/installs/python/3.12.12/lib/python3.12/random.py", line 308, in randrange
    return self._randbelow(istart)
           ^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/srm/.local/share/mise/installs/python/3.12.12/lib/python3.12/random.py", line 246, in _randbelow_with_getrandbits
    k = n.bit_length()
        ^^^^^^^^^^^^^^
k 3 best 3 outs [2, 3, 3, 3, 2, 3, 2] B [2, 2, 2, 2, 2, 2, 2] A [[1, 4], [4, 5, 6], [4, 5, 6], [0, 1, 4], [5, 6], [0, 3, 6], [0, 3]]
KeyboardInterrupt

codex
緩和版について、`n=7` では `S=3` の例が出ました。これは単発の偶然ではなく、正則トーナメントから有向三角形の3弧だけを消す一般構成で同じ現象が出るかを確認しています。
exec
/bin/zsh -lc 'python3 -c $'"'def cyclic(n):\\n k=(n-1)//2; A=[set() for _ in range(n)]\\n for i in range(n):\\n  for d in range(1,k+1): A[i].add((i+d)%n)\\n return A\\ndef val(A):\\n n=len(A); S=0; bs=[]; outs=[]\\n for v in range(n):\\n  r=set()\\n  for y in A[v]: r |= A[y]\\n  r.discard(v); r-=A[v]; bs.append(len(r)); outs.append(len(A[v])); S+=max(0,len(r)-len(A[v])+1)\\n return S,outs,bs\\nfor k in range(2,10):\\n n=2*k+1; A=cyclic(n)\\n # triangle 0->1, 1->k+1, k+1->0 in cyclic? check\\n tri=[(0,1),(1,k+1),(k+1,0)]\\n ok=all(b in A[a] for a,b in tri)\\n B=[set(s) for s in A]\\n for a,b in tri: B[a].remove(b)\\n print(k,ok,val(B))\\n'" in /private/tmp/claude-501/-Users-srm-dev-conway99-funsearch/ead2d61b-ebf6-4654-abeb-2f2226dceb95/scratchpad/iryu_1784988482
 succeeded in 0ms:
2 True (7, [1, 1, 2, 1, 2], [2, 2, 2, 2, 1])
3 True (9, [2, 2, 3, 3, 2, 3, 3], [3, 3, 3, 3, 3, 2, 3])
4 True (11, [3, 3, 4, 4, 4, 3, 4, 4, 4], [4, 4, 4, 4, 4, 4, 3, 4, 4])
5 True (13, [4, 4, 5, 5, 5, 5, 4, 5, 5, 5, 5], [5, 5, 5, 5, 5, 5, 5, 4, 5, 5, 5])
6 True (15, [5, 5, 6, 6, 6, 6, 6, 5, 6, 6, 6, 6, 6], [6, 6, 6, 6, 6, 6, 6, 6, 5, 6, 6, 6, 6])
7 True (17, [6, 6, 7, 7, 7, 7, 7, 7, 6, 7, 7, 7, 7, 7, 7], [7, 7, 7, 7, 7, 7, 7, 7, 7, 6, 7, 7, 7, 7, 7])
8 True (19, [7, 7, 8, 8, 8, 8, 8, 8, 8, 7, 8, 8, 8, 8, 8, 8, 8], [8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 7, 8, 8, 8, 8, 8, 8])
9 True (21, [8, 8, 9, 9, 9, 9, 9, 9, 9, 9, 8, 9, 9, 9, 9, 9, 9, 9, 9], [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 8, 9, 9, 9, 9, 9, 9, 9])

exec
/bin/zsh -lc 'python3 -c $'"'A=[{1,4},{4,5,6},{4,5,6},{0,1,4},{5,6},{0,3,6},{0,3}]\\nn=7\\nmiss=[]\\nfor i in range(n):\\n for j in range(i+1,n):\\n  if j not in A[i] and i not in A[j]: miss.append((i,j))\\nprint(miss)\\n# deleted arcs from what orientation? missing pairs were likely outgoing from low degree vertices: 0-6 had 6->0 in A yes no, miss etc\\n'" in /private/tmp/claude-501/-Users-srm-dev-conway99-funsearch/ead2d61b-ebf6-4654-abeb-2f2226dceb95/scratchpad/iryu_1784988482
 succeeded in 0ms:
[(0, 2), (1, 2), (2, 3)]

codex
課題 2 の「n<24 で空」は怪しいです。各クラスの `j=0` 頂点の出次数は外部クラスへの合計だけなので、全ての強連結な基礎グラフ `H` を小さく全探索して、最小総頂点数を整数計画として検算します。
exec
/bin/zsh -lc 'python3 -c $'"'from itertools import product\\nfrom collections import deque\\n\\ndef strong(m,adj):\\n for s in range(m):\\n  seen={s}; q=deque([s])\\n  while q:\\n   u=q.popleft()\\n   for v in adj[u]:\\n    if v not in seen: seen.add(v); q.append(v)\\n  if len(seen)<m: return False\\n return True\\n\\ndef feasible(m,adj,N):\\n # positive n_i sum N, check all ext out sums >=8\\n xs=[1]*m\\n def rec(i,rem,arr):\\n  if i==m-1:\\n   arr=arr+[rem]\\n   return all(sum(arr[b] for b in adj[a])>=8 for a in range(m))\\n  for v in range(1, rem-(m-i-1)+1):\\n   if rec(i+1, rem-v, arr+[v]): return True\\n  return False\\n\\nfor m in range(3,7):\\n pairs=[(i,j) for i in range(m) for j in range(i+1,m)]\\n best=999; bestdata=None; cnt=0\\n for dirs in product([0,1], repeat=len(pairs)): # tournament H, strong only; adding missing arcs cannot help, so tournament likely min but okay?\\n  adj=[set() for _ in range(m)]\\n  for (i,j),d in zip(pairs,dirs):\\n   if d==0: adj[i].add(j)\\n   else: adj[j].add(i)\\n  if not strong(m,adj): continue\\n  cnt+=1\\n  for N in range(m,50):\\n   if feasible(m,adj,N):\\n    if N<best: best=N; bestdata=[sorted(s) for s in adj]\\n    break\\n print(\"m\",m,\"strong tournaments\",cnt,\"best\",best,\"adj\",bestdata)\\n'" in /private/tmp/claude-501/-Users-srm-dev-conway99-funsearch/ead2d61b-ebf6-4654-abeb-2f2226dceb95/scratchpad/iryu_1784988482
2026-07-25T14:22:44.892358Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 88 column 5
 succeeded in 646ms:
m 3 strong tournaments 2 best 999 adj None
m 4 strong tournaments 24 best 999 adj None
m 5 strong tournaments 544 best 999 adj None
m 6 strong tournaments 22320 best 999 adj None

codex
最初の検算スクリプトに候補生成の制約が強すぎる兆候がありました。検算を簡単な既知候補（6頂点の正則トーナメント）で再確認してから、主張の当否を判断します。
exec
/bin/zsh -lc 'python3 -c $'"'m=6\\nadj=[set() for _ in range(m)]\\n# impossible regular tournament on even 6; try cyclic out 1,2,3 gives antipodal 2-cycles? not tournament.\\n# use complete bipartite? print max min weighted maybe via all oriented incl missing exhaustive with DP fixed\\nfrom itertools import product\\nfrom collections import deque\\ndef strong(adj):\\n m=len(adj)\\n for s in range(m):\\n  seen={s}; q=deque([s])\\n  while q:\\n   u=q.popleft()\\n   for v in adj[u]:\\n    if v not in seen: seen.add(v); q.append(v)\\n  if len(seen)<m: return False\\n return True\\ndef comp(m,N):\\n arr=[]\\n def rec(i,rem,p):\\n  if i==m-1:\\n   if rem>=1: arr.append(p+[rem])\\n  else:\\n   for v in range(1, rem-(m-i-1)+1): rec(i+1, rem-v,p+[v])\\n rec(0,N,[])\\n return arr\\nfor m in range(3,7):\\n pairs=[(i,j) for i in range(m) for j in range(i+1,m)]\\n best=999; data=None\\n for dirs in product([-1,0,1], repeat=len(pairs)):\\n  adj=[set() for _ in range(m)]\\n  for (i,j),d in zip(pairs,dirs):\\n   if d==0: adj[i].add(j)\\n   elif d==1: adj[j].add(i)\\n  if not strong(adj): continue\\n  for N in range(m,40):\\n   found=None\\n   for weights in comp(m,N):\\n    if all(sum(weights[b] for b in adj[a])>=8 for a in range(m)):\\n     found=weights; break\\n   if found:\\n    if N<best: best=N; data=([sorted(s) for s in adj],found)\\n    break\\n print(m,best,data)\\n'" in /private/tmp/claude-501/-Users-srm-dev-conway99-funsearch/ead2d61b-ebf6-4654-abeb-2f2226dceb95/scratchpad/iryu_1784988482
2026-07-25T14:23:28.811197Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 88 column 5
2026-07-25T14:24:00.901316Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 88 column 5
codex
検算の結論は明確です。5頂点の正則トーナメントを基礎 `H` にし、全クラスサイズを 4 にすると総頂点数は 20 で、各 `j=0` 頂点の外部出次数が `4+4=8` になるため、`n<24` 空という文は成り立ちません。
2026-07-25T14:24:11.246163Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 88 column 5
 exited 130 in 72521ms:
Traceback (most recent call last):
  File "<string>", line 38, in <module>
  File "<string>", line 38, in <genexpr>
  File "<string>", line 38, in <genexpr>
KeyboardInterrupt
3 24 ([[1], [2], [0]], [8, 8, 8])
4 24 ([[2], [2], [3], [0, 1]], [1, 7, 8, 8])

web search: 
web search: oriented graph minimum outdegree (n-3)/2 second neighborhood at least three vertices
codex
## 課題 1

1. 証明のその一歩に誤りはありません。

`D` は最初の個数計算でトーナメント、しかも全出次数 `k` の正則トーナメントになります。  
`w -> v` かつ `w ∉ B(v)` と仮定する。任意の `y ∈ A(v)` について、トーナメントなので `w -> y` か `y -> w` のどちらか一方です。もし `y -> w` なら `v -> y -> w` という長さ 2 の有向路があり、かつ `w ∉ A(v) ∪ {v}` なので `w ∈ B(v)` です。これは仮定に反する。したがって全ての `y ∈ A(v)` で `w -> y`。この推論は正しいです。

よって提示証明は成立しています。主張の反例はありません。

2. 既知性については、新規主張というより古典的事実の言い換えです。

使っている核心は「トーナメントで最大出次数の頂点は king、すなわち全頂点へ長さ 2 以下で到達できる」という Landau の定理です。正則トーナメントでは全頂点が最大出次数なので全頂点が king です。すると各頂点 `v` について、`A(v)` 以外の全頂点、つまり入近傍がすべて距離 2 に入り、`|B(v)| = indeg(v) = outdeg(v)` になります。

標準名としては「正則トーナメントの第二近傍等式」という固有名はあまり見ません。分類するなら、Landau の king 定理の即時系、または folklore 的な既知事実です。  
参照例: Landau の定理として「maximum score vertex is a king」が紹介されています。Singapore Mathematical Society の解説にも同内容があります: https://paperzz.com/doc/7183445/kings-in-tournaments--2----singapore-mathematical-society 。また Math StackExchange でも提示証明と同型の議論が載っています: https://math.stackexchange.com/q/2235350 。

3. 出次数下限を `k-1` に緩めると、少なくとも `S(D)=n` は直ちに壊れます。

実検算した最小例:

- `k=1, n=3, δ⁺≥0`: 最小 `S=1`。例: `0 -> 2`, `1 -> 2` の2弧だけ。
- `k=2, n=5, δ⁺≥1`: 全探索で最小 `S=3`。例:
  - `A(0)={3,4}`
  - `A(1)={3,4}`
  - `A(2)={3}`
  - `A(3)={4}`
  - `A(4)={2}`  
  このとき出次数は `(2,2,1,1,1)`、各 `|B(v)|=1`、したがって `S=3 < 5`。

`k=3, n=7` でも探索で `S=3` の例が見つかりました。したがって緩和版では元の結論 `S=n` は保てません。一般の厳密最小値をこの場で古典定理として断定するのは危険です。これは Seymour second neighborhood 型の量、つまり `|B(v)| >= |A(v)|` を持つ頂点の存在問題に近く、一般有向グラフでは未解決問題として扱われる文脈があります。Seymour の第二近傍予想については、例えば “Seymour’s Second Neighborhood Conjecture asserts...” と説明されている近年の論文があります: https://www.sciencedirect.com/science/article/pii/S0166218X23001841 。

## 課題 2

1. 文面が主張していることは限定的です。

対象は、`3 ≤ m ≤ 6` の強連結なループなし・両方向弧なしの基礎有向グラフ `H` と、指定された blow-up 構成 `H[n;c]` で作られる `G` だけです。そのうち `δ⁺(G) ≥ 8` を満たすものについて、

- `S(G) ≥ 3`
- もし `S(G)=3` なら `3 | n`

を主張しています。

主張していないことは、一般の `n` 頂点有向グラフで `δ⁺≥8` なら `S≥3`、という命題です。また、任意の blow-up、任意の `m`、任意の内部構造についても述べていません。

2. 定義の穴について。

`G` がループを持たないことは従います。`(R)` は `H` にループがないので同じクラスには弧を作らず、`(T)` は `l < min(j,c_a)` なので `l<j`、従って自己ループは作りません。

両方向弧を持たないことも従います。異なるクラス間では `H` に両方向弧がないため一方向だけです。同一クラス内では大きい添字から小さい添字への弧だけなので、逆向きは出ません。

強連結性も、`H` が強連結で全クラスが非空なので `G` に継承されます。同じクラス内の別頂点へも、いったん `H` の有向閉路に沿って外へ出て戻れば到達できます。

`min(j,c_a)` は通常の整数の最小値として読めば曖昧ではありません。意味は `0 ≤ l < j` かつ `l < c_a` です。

3. 「この族は `n < 24` では空」は誤りです。

反例があります。`m=5` とし、`H` を5頂点正則トーナメント、例えば頂点を `Z/5Z` として  
`a -> a+1`, `a -> a+2`  
で定めます。各クラスサイズをすべて `n_a=4` にすると、総頂点数は

`n = 5 * 4 = 20 < 24`

です。各クラスの `j=0` 頂点の出次数は、外部の2クラス分なので

`4 + 4 = 8`

です。`j>0` では内部弧が増えるだけなので、最小出次数は少なくとも 8。したがって `n<24` で空ではありません。

4. 誤読リスクはあります。最終段落はかなり明示的ですが、主張文の見出しや本文だけを拾われると「最小出次数 ≥8 の有向グラフ一般」と読まれる余地があります。

より安全には、主張の冒頭をこうするべきです。

> **主張（限定された blow-up 族についてのみ）.** 以下の特殊な族 `F` に属するグラフ `G=H[n;c]` のうち、`δ⁺(G)≥8` を満たすものすべてについて `S(G)≥3` である。これは `δ⁺≥8` の有向グラフ全体に対する命題ではない。

さらに `n<24` の文は削除または修正が必要です。少なくとも `n=20` の例があるため、そのままでは false です。

5. 射程はかなり狭いです。

`m≤6` は基礎グラフの頂点数を最大6に固定しており、一般の blow-up からは大きく外れます。また `(T)` は各クラス内を「添字の大きいものから小さいものへ、しかも下位 `c_a` 個まで」という非常に特殊な切り詰め推移構造に限定しています。したがって、この主張は一般の有向グラフはもちろん、一般の強連結 blow-up や一般のクラス内トーナメントにも拡張して読んではいけません。
tokens used
55,802
## 課題 1

1. 証明のその一歩に誤りはありません。

`D` は最初の個数計算でトーナメント、しかも全出次数 `k` の正則トーナメントになります。  
`w -> v` かつ `w ∉ B(v)` と仮定する。任意の `y ∈ A(v)` について、トーナメントなので `w -> y` か `y -> w` のどちらか一方です。もし `y -> w` なら `v -> y -> w` という長さ 2 の有向路があり、かつ `w ∉ A(v) ∪ {v}` なので `w ∈ B(v)` です。これは仮定に反する。したがって全ての `y ∈ A(v)` で `w -> y`。この推論は正しいです。

よって提示証明は成立しています。主張の反例はありません。

2. 既知性については、新規主張というより古典的事実の言い換えです。

使っている核心は「トーナメントで最大出次数の頂点は king、すなわち全頂点へ長さ 2 以下で到達できる」という Landau の定理です。正則トーナメントでは全頂点が最大出次数なので全頂点が king です。すると各頂点 `v` について、`A(v)` 以外の全頂点、つまり入近傍がすべて距離 2 に入り、`|B(v)| = indeg(v) = outdeg(v)` になります。

標準名としては「正則トーナメントの第二近傍等式」という固有名はあまり見ません。分類するなら、Landau の king 定理の即時系、または folklore 的な既知事実です。  
参照例: Landau の定理として「maximum score vertex is a king」が紹介されています。Singapore Mathematical Society の解説にも同内容があります: https://paperzz.com/doc/7183445/kings-in-tournaments--2----singapore-mathematical-society 。また Math StackExchange でも提示証明と同型の議論が載っています: https://math.stackexchange.com/q/2235350 。

3. 出次数下限を `k-1` に緩めると、少なくとも `S(D)=n` は直ちに壊れます。

実検算した最小例:

- `k=1, n=3, δ⁺≥0`: 最小 `S=1`。例: `0 -> 2`, `1 -> 2` の2弧だけ。
- `k=2, n=5, δ⁺≥1`: 全探索で最小 `S=3`。例:
  - `A(0)={3,4}`
  - `A(1)={3,4}`
  - `A(2)={3}`
  - `A(3)={4}`
  - `A(4)={2}`  
  このとき出次数は `(2,2,1,1,1)`、各 `|B(v)|=1`、したがって `S=3 < 5`。

`k=3, n=7` でも探索で `S=3` の例が見つかりました。したがって緩和版では元の結論 `S=n` は保てません。一般の厳密最小値をこの場で古典定理として断定するのは危険です。これは Seymour second neighborhood 型の量、つまり `|B(v)| >= |A(v)|` を持つ頂点の存在問題に近く、一般有向グラフでは未解決問題として扱われる文脈があります。Seymour の第二近傍予想については、例えば “Seymour’s Second Neighborhood Conjecture asserts...” と説明されている近年の論文があります: https://www.sciencedirect.com/science/article/pii/S0166218X23001841 。

## 課題 2

1. 文面が主張していることは限定的です。

対象は、`3 ≤ m ≤ 6` の強連結なループなし・両方向弧なしの基礎有向グラフ `H` と、指定された blow-up 構成 `H[n;c]` で作られる `G` だけです。そのうち `δ⁺(G) ≥ 8` を満たすものについて、

- `S(G) ≥ 3`
- もし `S(G)=3` なら `3 | n`

を主張しています。

主張していないことは、一般の `n` 頂点有向グラフで `δ⁺≥8` なら `S≥3`、という命題です。また、任意の blow-up、任意の `m`、任意の内部構造についても述べていません。

2. 定義の穴について。

`G` がループを持たないことは従います。`(R)` は `H` にループがないので同じクラスには弧を作らず、`(T)` は `l < min(j,c_a)` なので `l<j`、従って自己ループは作りません。

両方向弧を持たないことも従います。異なるクラス間では `H` に両方向弧がないため一方向だけです。同一クラス内では大きい添字から小さい添字への弧だけなので、逆向きは出ません。

強連結性も、`H` が強連結で全クラスが非空なので `G` に継承されます。同じクラス内の別頂点へも、いったん `H` の有向閉路に沿って外へ出て戻れば到達できます。

`min(j,c_a)` は通常の整数の最小値として読めば曖昧ではありません。意味は `0 ≤ l < j` かつ `l < c_a` です。

3. 「この族は `n < 24` では空」は誤りです。

反例があります。`m=5` とし、`H` を5頂点正則トーナメント、例えば頂点を `Z/5Z` として  
`a -> a+1`, `a -> a+2`  
で定めます。各クラスサイズをすべて `n_a=4` にすると、総頂点数は

`n = 5 * 4 = 20 < 24`

です。各クラスの `j=0` 頂点の出次数は、外部の2クラス分なので

`4 + 4 = 8`

です。`j>0` では内部弧が増えるだけなので、最小出次数は少なくとも 8。したがって `n<24` で空ではありません。

4. 誤読リスクはあります。最終段落はかなり明示的ですが、主張文の見出しや本文だけを拾われると「最小出次数 ≥8 の有向グラフ一般」と読まれる余地があります。

より安全には、主張の冒頭をこうするべきです。

> **主張（限定された blow-up 族についてのみ）.** 以下の特殊な族 `F` に属するグラフ `G=H[n;c]` のうち、`δ⁺(G)≥8` を満たすものすべてについて `S(G)≥3` である。これは `δ⁺≥8` の有向グラフ全体に対する命題ではない。

さらに `n<24` の文は削除または修正が必要です。少なくとも `n=20` の例があるため、そのままでは false です。

5. 射程はかなり狭いです。

`m≤6` は基礎グラフの頂点数を最大6に固定しており、一般の blow-up からは大きく外れます。また `(T)` は各クラス内を「添字の大きいものから小さいものへ、しかも下位 `c_a` 個まで」という非常に特殊な切り詰め推移構造に限定しています。したがって、この主張は一般の有向グラフはもちろん、一般の強連結 blow-up や一般のクラス内トーナメントにも拡張して読んではいけません。
```

## Round 2 プロンプト(全文)
```
課題2の続きです。あなたが示した n=20 の例(m=5、H = Z/5Z 上の回転トーナメント a→a+1, a→a+2、全クラスサイズ n_a=4)は「n<24 で空」を反証しました。これを踏まえて、次を実際に計算・探索してください。

1. **その n=20 の例について S(G) を実際に計算してください**(c ベクトルは 0 ≤ c_a ≤ 4 の全候補、あるいは代表的なもの)。もし S(G) = 3 となる c があれば、20 は 3 で割り切れないので「S(G)=3 ならば 3∣n」という主張本体の反例になります。もし S(G) ≤ 2 となる c があれば「S(G) ≥ 3」の反例になります。数値を明示してください。

2. **族のうち n < 24 の全メンバー**(3 ≤ m ≤ 6、H は強連結、min outdeg(G) ≥ 8、n = Σ n_a < 24)について、S(G) の最小値を可能な範囲で探索してください。m=6 まで含めて、族が非空になる最小の n はいくつですか。

3. n ≥ 24 の範囲で、主張「S(G) ≥ 3、かつ S(G)=3 ⇒ 3∣n」に反する (H, n, c) を探索で見つけられますか。小さい n(24〜30 程度)で構いません。

計算は実行して、結果の数値を明示してください。
```

## Round 2 codex 出力(全文、生ログ)
```
2026-07-25T14:27:16.926176Z ERROR codex_models_manager::cache: failed to load models cache: missing field `supports_reasoning_summaries` at line 88 column 5
OpenAI Codex v0.142.5
--------
workdir: /private/tmp/claude-501/-Users-srm-dev-conway99-funsearch/ead2d61b-ebf6-4654-abeb-2f2226dceb95/scratchpad/iryu_1784988482
model: gpt-5.5
provider: openai
approval: never
sandbox: read-only
reasoning effort: medium
reasoning summaries: none
session id: 019f99a4-4a75-71f2-a532-9eec018178c3
--------
user
課題2の続きです。あなたが示した n=20 の例(m=5、H = Z/5Z 上の回転トーナメント a→a+1, a→a+2、全クラスサイズ n_a=4)は「n<24 で空」を反証しました。これを踏まえて、次を実際に計算・探索してください。

1. **その n=20 の例について S(G) を実際に計算してください**(c ベクトルは 0 ≤ c_a ≤ 4 の全候補、あるいは代表的なもの)。もし S(G) = 3 となる c があれば、20 は 3 で割り切れないので「S(G)=3 ならば 3∣n」という主張本体の反例になります。もし S(G) ≤ 2 となる c があれば「S(G) ≥ 3」の反例になります。数値を明示してください。

2. **族のうち n < 24 の全メンバー**(3 ≤ m ≤ 6、H は強連結、min outdeg(G) ≥ 8、n = Σ n_a < 24)について、S(G) の最小値を可能な範囲で探索してください。m=6 まで含めて、族が非空になる最小の n はいくつですか。

3. n ≥ 24 の範囲で、主張「S(G) ≥ 3、かつ S(G)=3 ⇒ 3∣n」に反する (H, n, c) を探索で見つけられますか。小さい n(24〜30 程度)で構いません。

計算は実行して、結果の数値を明示してください。
codex
続きは計算主導で進めます。まず `n=20` の具体例を `c` 全3125通りで厳密に計算し、その後 `n<24` の候補は `δ⁺≥8` が `c` に依存しない点を使って絞り込みます。
exec
/bin/zsh -lc 'python3 -c $'"'
from itertools import product

def build(m,s,c,adj):
    offsets=[0]
    for x in s: offsets.append(offsets[-1]+x)
    n=offsets[-1]
    A=[set() for _ in range(n)]
    for a in range(m):
        # R
        for b in adj[a]:
            targets=range(offsets[b], offsets[b+1])
            for j in range(s[a]):
                A[offsets[a]+j].update(targets)
        # T
        for j in range(s[a]):
            lim=min(j,c[a])
            for l in range(lim):
                A[offsets[a]+j].add(offsets[a]+l)
    return A

def S_of(A):
    n=len(A); total=0; vals=[]
    for v in range(n):
        R=set()
        for y in A[v]: R |= A[y]
        R.discard(v); R -= A[v]
        d=len(A[v]); b=len(R); term=max(0,b-d+1)
        total+=term; vals.append((d,b,term))
    return total, vals

m=5
s=[4]*5
adj=[set() for _ in range(m)]
for a in range(m):
    adj[a].add((a+1)%m); adj[a].add((a+2)%m)

best=10**9; bestcs=[]; hist={}
for c in product(range(5), repeat=5):
    A=build(m,s,c,adj)
    S,vals=S_of(A)
    hist[S]=hist.get(S,0)+1
    if S<best:
        best=S; bestcs=[c]
    elif S==best and len(bestcs)<10:
        bestcs.append(c)
print(\"best\",best,\"examples\",bestcs)
print(\"hist\",sorted(hist.items())[:20],\"... total distinct\",len(hist))
for c in [(0,0,0,0,0),(1,1,1,1,1),(2,2,2,2,2),(3,3,3,3,3),(4,4,4,4,4),bestcs[0]]:
    A=build(m,s,c,adj); S,vals=S_of(A)
    from collections import Counter
    print(\"c\",c,\"S\",S,\"terms\",Counter(t for d,b,t in vals),\"db\",Counter((d,b) for d,b,t in vals))
'" in /private/tmp/claude-501/-Users-srm-dev-conway99-funsearch/ead2d61b-ebf6-4654-abeb-2f2226dceb95/scratchpad/iryu_1784988482
 succeeded in 137ms:
best 5 examples [(1, 1, 1, 1, 1), (1, 1, 1, 1, 2), (1, 1, 1, 1, 3), (1, 1, 1, 1, 4), (1, 1, 1, 2, 1), (1, 1, 1, 2, 2), (1, 1, 1, 2, 3), (1, 1, 1, 2, 4), (1, 1, 1, 3, 1), (1, 1, 1, 3, 2)]
hist [(5, 1024), (8, 1280), (11, 640), (14, 160), (17, 20), (20, 1)] ... total distinct 6
c (0, 0, 0, 0, 0) S 20 terms Counter({1: 20}) db Counter({(8, 8): 20})
c (1, 1, 1, 1, 1) S 5 terms Counter({0: 15, 1: 5}) db Counter({(9, 8): 15, (8, 8): 5})
c (2, 2, 2, 2, 2) S 5 terms Counter({0: 15, 1: 5}) db Counter({(10, 8): 10, (8, 8): 5, (9, 8): 5})
c (3, 3, 3, 3, 3) S 5 terms Counter({0: 15, 1: 5}) db Counter({(8, 8): 5, (9, 8): 5, (10, 8): 5, (11, 8): 5})
c (4, 4, 4, 4, 4) S 5 terms Counter({0: 15, 1: 5}) db Counter({(8, 8): 5, (9, 8): 5, (10, 8): 5, (11, 8): 5})
c (1, 1, 1, 1, 1) S 5 terms Counter({0: 15, 1: 5}) db Counter({(9, 8): 15, (8, 8): 5})

codex
`n=20` の例は最小 `S=5` でした。したがってこの例自体は主張本体の反例ではありません。次に、まず強連結トーナメント基礎 `H` に絞った全探索で `n<24` と `24〜30` の小さい範囲を調べます。
exec
/bin/zsh -lc 'python3 -c $'"'
from itertools import product
from collections import deque, Counter

def strong(adj):
    m=len(adj)
    for s in range(m):
        seen={s}; q=deque([s])
        while q:
            u=q.popleft()
            for v in adj[u]:
                if v not in seen: seen.add(v); q.append(v)
        if len(seen)<m: return False
    return True

def comps(m,N):
    def rec(i,rem,p):
        if i==m-1:
            if rem>=1: yield p+[rem]
            return
        for v in range(1, rem-(m-i-1)+1):
            yield from rec(i+1,rem-v,p+[v])
    yield from rec(0,N,[])

def build_masks(m,s,c,adj):
    off=[0]
    for x in s: off.append(off[-1]+x)
    n=off[-1]; A=[0]*n
    classmask=[((1<<off[a+1])-(1<<off[a])) for a in range(m)]
    for a in range(m):
        ext=0
        for b in adj[a]: ext |= classmask[b]
        for j in range(s[a]):
            mask=ext
            lim=min(j,c[a])
            if lim: mask |= ((1<<(off[a]+lim))-(1<<off[a]))
            A[off[a]+j]=mask
    return A

def S_masks(A):
    n=len(A); total=0
    for v,mask in enumerate(A):
        R=0; mm=mask
        while mm:
            lsb=mm & -mm; y=lsb.bit_length()-1; R |= A[y]; mm-=lsb
        R &= ~mask; R &= ~(1<<v)
        b=R.bit_count(); d=mask.bit_count(); total += max(0,b-d+1)
        if total>=999999: pass
    return total

def search_tournaments(Nmin,Nmax):
    global_best=(10**9,None)
    minN=None; cand=0; checked_c=0; hist=Counter()
    for m in range(3,7):
        pairs=[(i,j) for i in range(m) for j in range(i+1,m)]
        for dirs in product([0,1], repeat=len(pairs)):
            adj=[set() for _ in range(m)]
            for (i,j),d in zip(pairs,dirs):
                (adj[i] if d==0 else adj[j]).add(j if d==0 else i)
            if not strong(adj): continue
            for N in range(Nmin,Nmax+1):
                for s in comps(m,N):
                    if not all(sum(s[b] for b in adj[a])>=8 for a in range(m)): continue
                    cand+=1
                    if minN is None or N<minN: minN=N
                    # enumerate c
                    ranges=[range(x+1) for x in s]
                    for c in product(*ranges):
                        checked_c+=1
                        S=S_masks(build_masks(m,s,c,adj))
                        hist[S]+=1
                        if S<global_best[0]:
                            global_best=(S,(m,[sorted(x) for x in adj],tuple(s),tuple(c),N))
    return minN,cand,checked_c,global_best,hist

for lo,hi in [(3,23),(24,30)]:
    res=search_tournaments(lo,hi)
    print(\"range\",lo,hi,\"minN\",res[0],\"weighted candidates\",res[1],\"c checked\",res[2])
    print(\"best\",res[3])
    print(\"small hist\",sorted(res[4].items())[:20])
'" in /private/tmp/claude-501/-Users-srm-dev-conway99-funsearch/ead2d61b-ebf6-4654-abeb-2f2226dceb95/scratchpad/iryu_1784988482
2026-07-25T14:28:40.049211Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 88 column 5
codex
探索は継続中です。トーナメント基礎だけでも候補は多いですが、`δ⁺≥8` の判定を重み条件で先に済ませ、`S` はビットマスクで計算しています。
2026-07-25T14:29:13.434351Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 88 column 5
codex
全範囲を一気に回すと時間が伸びています。いったん止めて、`n<24` の最小 `n` と低い `S` を見つける探索に分け、必要な範囲から順に確定させます。
2026-07-25T14:29:17.243993Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 88 column 5
 exited 130 in 67293ms:
Traceback (most recent call last):
  File "<string>", line 77, in <module>
  File "<string>", line 70, in search_tournaments
  File "<string>", line 48, in S_masks
KeyboardInterrupt

codex
目的に合わせて探索方針を切り替えます。完全な列挙は重いので、まず反例発見用のランダム探索と、非空最小 `n` の厳密寄りチェックを分けます。
exec
/bin/zsh -lc 'python3 -c $'"'
import random, itertools, time
from collections import deque

def strong(adj):
 m=len(adj)
 for s in range(m):
  seen={s}; q=deque([s])
  while q:
   u=q.popleft()
   for v in adj[u]:
    if v not in seen: seen.add(v); q.append(v)
  if len(seen)<m: return False
 return True

def S(m,s,c,adj):
 off=[0]
 for x in s: off.append(off[-1]+x)
 n=off[-1]; cm=[((1<<off[a+1])-(1<<off[a])) for a in range(m)]; A=[0]*n
 for a in range(m):
  ext=0
  for b in adj[a]: ext|=cm[b]
  base=off[a]
  for j in range(s[a]):
   lim=min(j,c[a]); A[base+j]=ext | (((1<<(base+lim))-(1<<base)) if lim else 0)
 tot=0
 for v,mask in enumerate(A):
  R=0; mm=mask
  while mm:
   l=mm&-mm; y=l.bit_length()-1; R|=A[y]; mm-=l
  R &= ~mask; R &= ~(1<<v)
  tot += max(0, R.bit_count()-mask.bit_count()+1)
 return tot

def rand_adj(m,missing=False):
 while True:
  adj=[set() for _ in range(m)]
  for i in range(m):
   for j in range(i+1,m):
    d=random.randrange(3 if missing else 2)
    if d==0: adj[i].add(j)
    elif d==1: adj[j].add(i)
  if strong(adj): return adj

def rand_comp(m,N):
 cuts=sorted(random.sample(range(1,N),m-1)); arr=[]; last=0
 for x in cuts+[N]: arr.append(x-last); last=x
 return arr
for rng in [(3,23),(24,30)]:
 best=(10**9,None); minN=999; feasible=0; start=time.time()
 for it in range(200000):
  m=random.randint(3,6); N=random.randint(rng[0],rng[1]); adj=rand_adj(m,missing=True); s=rand_comp(m,N)
  if not all(sum(s[b] for b in adj[a])>=8 for a in range(m)): continue
  feasible+=1; minN=min(minN,N)
  # try random c plus all-zero/all-max/all-one
  cs=[tuple(0 for _ in s), tuple(x for x in s), tuple(min(1,x) for x in s)]
  for _ in range(10): cs.append(tuple(random.randint(0,x) for x in s))
  for c in cs:
   val=S(m,s,c,adj)
   if val<best[0]: best=(val,(m,[sorted(x) for x in adj],tuple(s),c,N,it))
 print(\"range\",rng,\"feasible samples\",feasible,\"minN seen\",minN,\"best\",best,\"time\",time.time()-start)
'" in /private/tmp/claude-501/-Users-srm-dev-conway99-funsearch/ead2d61b-ebf6-4654-abeb-2f2226dceb95/scratchpad/iryu_1784988482
 exited 1 in 0ms:
Traceback (most recent call last):
  File "<string>", line 52, in <module>
  File "<string>", line 46, in rand_comp
  File "/Users/srm/.local/share/mise/installs/python/3.12.12/lib/python3.12/random.py", line 430, in sample
    raise ValueError("Sample larger than population or is negative")
ValueError: Sample larger than population or is negative

2026-07-25T14:29:35.793877Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 88 column 5
exec
/bin/zsh -lc 'python3 -c $'"'
import random, time
from collections import deque

def strong(adj):
 m=len(adj)
 for s in range(m):
  seen={s}; q=deque([s])
  while q:
   u=q.popleft()
   for v in adj[u]:
    if v not in seen: seen.add(v); q.append(v)
  if len(seen)<m: return False
 return True

def S(m,s,c,adj):
 off=[0]
 for x in s: off.append(off[-1]+x)
 n=off[-1]; cm=[((1<<off[a+1])-(1<<off[a])) for a in range(m)]; A=[0]*n
 for a in range(m):
  ext=0
  for b in adj[a]: ext|=cm[b]
  base=off[a]
  for j in range(s[a]):
   lim=min(j,c[a]); A[base+j]=ext | (((1<<(base+lim))-(1<<base)) if lim else 0)
 tot=0
 for v,mask in enumerate(A):
  R=0; mm=mask
  while mm:
   l=mm&-mm; y=l.bit_length()-1; R|=A[y]; mm-=l
  R &= ~mask; R &= ~(1<<v)
  tot += max(0, R.bit_count()-mask.bit_count()+1)
 return tot

def rand_adj(m):
 while True:
  adj=[set() for _ in range(m)]
  for i in range(m):
   for j in range(i+1,m):
    d=random.randrange(3)
    if d==0: adj[i].add(j)
    elif d==1: adj[j].add(i)
  if strong(adj): return adj

def rand_comp(m,N):
 cuts=sorted(random.sample(range(1,N),m-1)); arr=[]; last=0
 for x in cuts+[N]: arr.append(x-last); last=x
 return arr
for rng in [(3,23),(24,30)]:
 best=(10**9,None); minN=999; feasible=0; start=time.time()
 for it in range(200000):
  m=random.randint(3,6); N=random.randint(max(rng[0],m),rng[1]); adj=rand_adj(m); s=rand_comp(m,N)
  if not all(sum(s[b] for b in adj[a])>=8 for a in range(m)): continue
  feasible+=1; minN=min(minN,N)
  cs=[tuple(0 for _ in s), tuple(x for x in s), tuple(min(1,x) for x in s)]
  for _ in range(10): cs.append(tuple(random.randint(0,x) for x in s))
  for c in cs:
   val=S(m,s,c,adj)
   if val<best[0]: best=(val,(m,[sorted(x) for x in adj],tuple(s),c,N,it))
 print(\"range\",rng,\"feasible samples\",feasible,\"minN seen\",minN,\"best\",best,\"time\",round(time.time()-start,2))
'" in /private/tmp/claude-501/-Users-srm-dev-conway99-funsearch/ead2d61b-ebf6-4654-abeb-2f2226dceb95/scratchpad/iryu_1784988482
2026-07-25T14:30:05.718670Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 88 column 5
 succeeded in 14032ms:
range (3, 23) feasible samples 0 minN seen 999 best (1000000000, None) time 6.17
range (24, 30) feasible samples 3309 minN seen 24 best (3, (4, [[1, 2], [3], [1], [0, 2]], (4, 8, 4, 8), (4, 8, 4, 8), 24, 1378)) time 7.83

exec
/bin/zsh -lc 'python3 -c $'"'
from itertools import product
from collections import deque

def strong(adj):
 m=len(adj)
 for s in range(m):
  seen={s}; q=deque([s])
  while q:
   u=q.popleft()
   for v in adj[u]:
    if v not in seen: seen.add(v); q.append(v)
  if len(seen)<m: return False
 return True

def comps(m,N):
 def rec(i,rem,p):
  if i==m-1:
   if rem>=1: yield p+[rem]
  else:
   for v in range(1, rem-(m-i-1)+1): yield from rec(i+1,rem-v,p+[v])
 yield from rec(0,N,[])
for m in range(3,7):
 pairs=[(i,j) for i in range(m) for j in range(i+1,m)]
 best=None; data=None; cnt=0
 for dirs in product([0,1], repeat=len(pairs)):
  adj=[set() for _ in range(m)]
  for (i,j),d in zip(pairs,dirs):
   if d==0: adj[i].add(j)
   else: adj[j].add(i)
  if not strong(adj): continue
  cnt+=1
  for N in range(m,24):
   for s in comps(m,N):
    if all(sum(s[b] for b in adj[a])>=8 for a in range(m)):
     if best is None or N<best: best=N; data=([sorted(x) for x in adj],s)
     break
   if best==N: break
 print(\"m\",m,\"strong_tourn\",cnt,\"bestN<24\",best,\"data\",data)
'" in /private/tmp/claude-501/-Users-srm-dev-conway99-funsearch/ead2d61b-ebf6-4654-abeb-2f2226dceb95/scratchpad/iryu_1784988482
codex
ランダム探索は `n=20` の既知例のような細い候補を拾いにくいので、非空性だけは `H` をトーナメントに絞った厳密列挙で確認しています。欠弧を入れても出次数条件は有利にならないため、最小 `n` の探索ではトーナメントをまず見るのが自然です。
codex
列挙が遅いので、整数計画ソルバが使えるか確認して、使えるなら `min Σ n_a` subject to `n_a≥1` and outgoing-weight sums `≥8` で非空最小を直接出します。
exec
/bin/zsh -lc "python3 -c \"import scipy, scipy.optimize as opt; print('scipy', scipy.__version__, hasattr(opt,'milp'))\"" in /private/tmp/claude-501/-Users-srm-dev-conway99-funsearch/ead2d61b-ebf6-4654-abeb-2f2226dceb95/scratchpad/iryu_1784988482
 succeeded in 866ms:
scipy 1.16.3 True

codex
`scipy.optimize.milp` が使えます。これで各 `H` の最小総サイズを厳密に解き、`n<24` の非空最小を確認します。
 exited 130 in 49404ms:
Traceback (most recent call last):
  File "<string>", line 35, in <module>
  File "<string>", line 35, in <genexpr>
KeyboardInterrupt
m 3 strong_tourn 2 bestN<24 None data None
m 4 strong_tourn 24 bestN<24 None data None
m 5 strong_tourn 544 bestN<24 20 data ([[1, 2], [2, 3], [3, 4], [0, 4], [0, 1]], [4, 4, 4, 4, 4])

exec
/bin/zsh -lc 'python3 -c $'"'
from itertools import product
from collections import deque
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds

def strong(adj):
 m=len(adj)
 for s in range(m):
  seen={s}; q=deque([s])
  while q:
   u=q.popleft()
   for v in adj[u]:
    if v not in seen: seen.add(v); q.append(v)
  if len(seen)<m: return False
 return True
for m in range(3,7):
 pairs=[(i,j) for i in range(m) for j in range(i+1,m)]
 best=999; data=None; cnt=0
 for dirs in product([0,1], repeat=len(pairs)):
  adj=[set() for _ in range(m)]
  for (i,j),d in zip(pairs,dirs):
   if d==0: adj[i].add(j)
   else: adj[j].add(i)
  if not strong(adj): continue
  cnt+=1
  A=np.zeros((m,m))
  for a in range(m):
   for b in adj[a]: A[a,b]=1
  lc=LinearConstraint(A, np.full(m,8), np.full(m,np.inf))
  res=milp(c=np.ones(m), integrality=np.ones(m), bounds=Bounds(np.ones(m), np.full(m,np.inf)), constraints=lc, options={\"time_limit\":1})
  if res.success:
   N=round(res.fun)
   if N<best:
    best=N; data=([sorted(x) for x in adj], [round(v) for v in res.x])
 print(\"m\",m,\"strong_tourn\",cnt,\"best\",best,\"data\",data)
'" in /private/tmp/claude-501/-Users-srm-dev-conway99-funsearch/ead2d61b-ebf6-4654-abeb-2f2226dceb95/scratchpad/iryu_1784988482
2026-07-25T14:31:34.629842Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 88 column 5
 succeeded in 13864ms:
m 3 strong_tourn 2 best 24 data ([[1], [2], [0]], [8, 8, 8])
m 4 strong_tourn 24 best 24 data ([[1, 2], [2, 3], [3], [0]], [8, 7, 1, 8])
m 5 strong_tourn 544 best 20 data ([[1, 2], [2, 3], [3, 4], [0, 4], [0, 1]], [4, 4, 4, 4, 4])
m 6 strong_tourn 22320 best 20 data ([[1, 2, 3], [2, 3, 4], [3, 4, 5], [4, 5], [0, 5], [0, 1]], [4, 4, 3, 1, 4, 4])

codex
非空最小は `n=20` でした。これは欠弧ありの `H` まで含めても、欠弧をトーナメントまで足せば出次数条件は弱くならないため、最小 `n` の下界確認として十分です。次は `n=20..23` の `S` 最小を探します。
exec
/bin/zsh -lc 'python3 -c $'"'
from itertools import product
from collections import deque,Counter

def strong(adj):
 m=len(adj)
 for s in range(m):
  seen={s}; q=deque([s])
  while q:
   u=q.popleft()
   for v in adj[u]:
    if v not in seen: seen.add(v); q.append(v)
  if len(seen)<m: return False
 return True

def comps(m,N):
 def rec(i,rem,p):
  if i==m-1:
   if rem>=1: yield p+[rem]
  else:
   for v in range(1, rem-(m-i-1)+1): yield from rec(i+1,rem-v,p+[v])
 yield from rec(0,N,[])
for m in [5,6]:
 pairs=[(i,j) for i in range(m) for j in range(i+1,m)]
 counts=Counter(); examples={}
 for dirs in product([0,1], repeat=len(pairs)):
  adj=[set() for _ in range(m)]
  for (i,j),d in zip(pairs,dirs):
   if d==0: adj[i].add(j)
   else: adj[j].add(i)
  if not strong(adj): continue
  for N in range(20,24):
   for s in comps(m,N):
    if all(sum(s[b] for b in adj[a])>=8 for a in range(m)):
     counts[N]+=1; examples.setdefault(N,([sorted(x) for x in adj],s))
 print(\"m\",m,\"counts\",counts,\"examples\",examples)
'" in /private/tmp/claude-501/-Users-srm-dev-conway99-funsearch/ead2d61b-ebf6-4654-abeb-2f2226dceb95/scratchpad/iryu_1784988482
2026-07-25T14:32:20.210411Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 88 column 5
codex
候補数カウントも `m=6` で重くなっています。ここからは全候補列挙ではなく、主張本体の反例発見に焦点を置いた探索に切り替え、見つかったものは個別に厳密計算します。
2026-07-25T14:32:25.579575Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 88 column 5
 exited 130 in 35468ms:
Traceback (most recent call last):
  File "<string>", line 33, in <module>
  File "<string>", line 22, in comps
  File "<string>", line 21, in rec
  File "<string>", line 21, in rec
  File "<string>", line 21, in rec
  [Previous line repeated 2 more times]
KeyboardInterrupt
m 5 counts Counter({23: 6680, 22: 1960, 21: 360, 20: 24}) examples {22: ([[1, 2, 3], [2, 4], [3, 4], [1, 4], [0]], [8, 2, 2, 4, 6]), 23: ([[1, 2, 3], [2, 4], [3, 4], [1, 4], [0]], [8, 1, 1, 6, 7]), 20: ([[1, 2], [2, 3], [3, 4], [0, 4], [0, 1]], [4, 4, 4, 4, 4]), 21: ([[1, 2], [2, 3], [3, 4], [0, 4], [0, 1]], [3, 5, 3, 5, 5])}

codex
`m=5` の `n=20..23` 候補数は出ました。これらについては `c` も含めて全探索できる規模なので、まず `m=5` で `S` の最小を厳密に出します。
exec
/bin/zsh -lc 'python3 -c $'"'
from itertools import product
from collections import deque,Counter

def strong(adj):
 m=len(adj)
 for s in range(m):
  seen={s}; q=deque([s])
  while q:
   u=q.popleft()
   for v in adj[u]:
    if v not in seen: seen.add(v); q.append(v)
  if len(seen)<m: return False
 return True

def comps(m,N):
 def rec(i,rem,p):
  if i==m-1:
   if rem>=1: yield p+[rem]
  else:
   for v in range(1, rem-(m-i-1)+1): yield from rec(i+1,rem-v,p+[v])
 yield from rec(0,N,[])
def Sm(m,s,c,adj):
 off=[0]
 for x in s: off.append(off[-1]+x)
 n=off[-1]; cm=[((1<<off[a+1])-(1<<off[a])) for a in range(m)]; A=[0]*n
 for a in range(m):
  ext=0
  for b in adj[a]: ext|=cm[b]
  base=off[a]
  for j in range(s[a]):
   lim=min(j,c[a]); A[base+j]=ext | (((1<<(base+lim))-(1<<base)) if lim else 0)
 tot=0
 for v,mask in enumerate(A):
  R=0; mm=mask
  while mm:
   l=mm&-mm; y=l.bit_length()-1; R|=A[y]; mm-=l
  R &= ~mask; R &= ~(1<<v)
  tot += max(0,R.bit_count()-mask.bit_count()+1)
  if tot>=best_global[0]:
   # cannot beat, but caller still ok
   pass
 return tot
best_by_N={N:(10**9,None) for N in range(20,24)}; checked=0; cand=0
pairs=[(i,j) for i in range(5) for j in range(i+1,5)]
for dirs in product([0,1], repeat=len(pairs)):
 adj=[set() for _ in range(5)]
 for (i,j),d in zip(pairs,dirs):
  if d==0: adj[i].add(j)
  else: adj[j].add(i)
 if not strong(adj): continue
 for N in range(20,24):
  for s in comps(5,N):
   if not all(sum(s[b] for b in adj[a])>=8 for a in range(5)): continue
   cand+=1
   ranges=[range(x+1) for x in s]
   for c in product(*ranges):
    checked+=1; best_global=best_by_N[N]
    val=Sm(5,s,c,adj)
    if val<best_by_N[N][0]: best_by_N[N]=(val,([sorted(x) for x in adj],tuple(s),tuple(c)))
print(\"cand\",cand,\"c_checked\",checked)
for N in range(20,24): print(N,best_by_N[N])
'" in /private/tmp/claude-501/-Users-srm-dev-conway99-funsearch/ead2d61b-ebf6-4654-abeb-2f2226dceb95/scratchpad/iryu_1784988482
codex
`m=5` の厳密探索も `c` の直積が効いて長引いています。ここで止めて、反例発見に必要な低い `S` を優先する局所探索にします。既に `n=20` の全 `c` は完了済みです。
 exited 130 in 66737ms:
Traceback (most recent call last):
  File "<string>", line 59, in <module>
  File "<string>", line 37, in Sm
KeyboardInterrupt

codex
これまでの探索では `n=24` に `S=3` の例が出ていますが、これは `3|24` なので反例ではありません。`24..30` では、非3倍の `n` に `S=3`、または任意の `n` に `S≤2` があるかを重点的に探します。
exec
/bin/zsh -lc 'python3 -c $'"'
import random, time
from collections import deque

def strong(adj):
 m=len(adj)
 for s in range(m):
  seen={s}; q=deque([s])
  while q:
   u=q.popleft()
   for v in adj[u]:
    if v not in seen: seen.add(v); q.append(v)
  if len(seen)<m: return False
 return True

def S(m,s,c,adj):
 off=[0]
 for x in s: off.append(off[-1]+x)
 n=off[-1]; cm=[((1<<off[a+1])-(1<<off[a])) for a in range(m)]; A=[0]*n
 for a in range(m):
  ext=0
  for b in adj[a]: ext|=cm[b]
  base=off[a]
  for j in range(s[a]):
   lim=min(j,c[a]); A[base+j]=ext | (((1<<(base+lim))-(1<<base)) if lim else 0)
 tot=0
 for v,mask in enumerate(A):
  R=0; mm=mask
  while mm:
   l=mm&-mm; y=l.bit_length()-1; R|=A[y]; mm-=l
  R &= ~mask; R &= ~(1<<v)
  tot += max(0,R.bit_count()-mask.bit_count()+1)
 return tot

def rand_adj(m):
 while True:
  adj=[set() for _ in range(m)]
  # bias tournaments mostly
  for i in range(m):
   for j in range(i+1,m):
    d=random.randrange(2)
    if d==0: adj[i].add(j)
    else: adj[j].add(i)
  if strong(adj): return adj

def rand_comp(m,N):
 cuts=sorted(random.sample(range(1,N),m-1)); arr=[]; last=0
 for x in cuts+[N]: arr.append(x-last); last=x
 return arr
best_by_N={N:(999,None) for N in range(24,31)}; hits=[]; feasible=0
start=time.time()
for it in range(500000):
 m=random.randint(3,6); N=random.randint(max(24,m),30); adj=rand_adj(m); s=rand_comp(m,N)
 if not all(sum(s[b] for b in adj[a])>=8 for a in range(m)): continue
 feasible+=1
 cs=[tuple(x for x in s), tuple(max(0,x-1) for x in s), tuple(1 for _ in s), tuple(0 for _ in s)]
 for _ in range(8): cs.append(tuple(random.randint(0,x) for x in s))
 for c in cs:
  val=S(m,s,c,adj)
  if val<best_by_N[N][0]:
   best_by_N[N]=(val,(m,[sorted(a) for a in adj],tuple(s),tuple(c),it))
   print(\"new\",N,best_by_N[N], flush=True)
  if val<=2 or (val==3 and N%3):
   print(\"COUNTER\",N,val,m,[sorted(a) for a in adj],s,c); raise SystemExit
print(\"done feasible\",feasible,\"best_by_N\",best_by_N,\"time\",time.time()-start)
'" in /private/tmp/claude-501/-Users-srm-dev-conway99-funsearch/ead2d61b-ebf6-4654-abeb-2f2226dceb95/scratchpad/iryu_1784988482
 succeeded in 14912ms:
new 27 (3, (3, [[1], [2], [0]], (9, 9, 9), (9, 9, 9), 3230))
new 30 (3, (4, [[1], [3], [0, 1], [0, 2]], (1, 10, 9, 10), (1, 10, 9, 10), 3618))
done feasible 16660 best_by_N {24: (3, (4, [[2], [0, 3], [1, 3], [0]], (8, 6, 8, 2), (8, 6, 8, 2), 404)), 25: (4, (3, [[2], [0], [1]], (8, 9, 8), (8, 9, 8), 534)), 26: (4, (5, [[4], [0, 3], [0, 1, 3], [0], [1, 2, 3]], (9, 3, 1, 5, 8), (9, 3, 1, 5, 8), 1579)), 27: (3, (3, [[1], [2], [0]], (9, 9, 9), (9, 9, 9), 3230)), 28: (4, (3, [[2], [0], [1]], (10, 9, 9), (10, 9, 9), 974)), 29: (4, (3, [[2], [0], [1]], (10, 9, 10), (10, 9, 10), 1330)), 30: (3, (4, [[1], [3], [0, 1], [0, 2]], (1, 10, 9, 10), (1, 10, 9, 10), 3618))} time 14.876914978027344

codex
`24..30` のランダム探索では反例は見つからず、最良値は `n=24,27,30` で `S=3`、非3倍の `n=25,26,28,29` では最良 `S=4` でした。次に `n=20..23` を同じ方針で重点探索します。
exec
/bin/zsh -lc 'python3 -c $'"'
import random, time
from collections import deque
# reuse funcs compact
def strong(adj):
 m=len(adj)
 for s in range(m):
  seen={s}; q=deque([s])
  while q:
   u=q.popleft()
   for v in adj[u]:
    if v not in seen: seen.add(v); q.append(v)
  if len(seen)<m: return False
 return True
def S(m,s,c,adj):
 off=[0]
 for x in s: off.append(off[-1]+x)
 n=off[-1]; cm=[((1<<off[a+1])-(1<<off[a])) for a in range(m)]; A=[0]*n
 for a in range(m):
  ext=0
  for b in adj[a]: ext|=cm[b]
  base=off[a]
  for j in range(s[a]):
   lim=min(j,c[a]); A[base+j]=ext | (((1<<(base+lim))-(1<<base)) if lim else 0)
 tot=0
 for v,mask in enumerate(A):
  R=0; mm=mask
  while mm:
   l=mm&-mm; y=l.bit_length()-1; R|=A[y]; mm-=l
  R &= ~mask; R &= ~(1<<v)
  tot += max(0,R.bit_count()-mask.bit_count()+1)
 return tot
def rand_tourn(m):
 while True:
  adj=[set() for _ in range(m)]
  for i in range(m):
   for j in range(i+1,m):
    if random.randrange(2): adj[i].add(j)
    else: adj[j].add(i)
  if strong(adj): return adj
def rand_comp(m,N):
 cuts=sorted(random.sample(range(1,N),m-1)); arr=[]; last=0
 for x in cuts+[N]: arr.append(x-last); last=x
 return arr
best_by_N={N:(999,None) for N in range(20,24)}; feasible=0
# seed known structures: 5-cycle regular for N 20..23 random comps satisfying
for it in range(300000):
 m=random.choice([5,6,3,4]); N=random.randint(max(20,m),23); adj=rand_tourn(m); s=rand_comp(m,N)
 if not all(sum(s[b] for b in adj[a])>=8 for a in range(m)): continue
 feasible+=1
 cs=[tuple(x for x in s), tuple(max(1,x//2) for x in s), tuple(1 for _ in s), tuple(0 for _ in s)]
 for _ in range(15): cs.append(tuple(random.randint(0,x) for x in s))
 for c in cs:
  val=S(m,s,c,adj)
  if val<best_by_N[N][0]:
   best_by_N[N]=(val,(m,[sorted(a) for a in adj],tuple(s),tuple(c),it)); print(\"new\",N,best_by_N[N],flush=True)
print(\"feasible\",feasible,\"best\",best_by_N)
'" in /private/tmp/claude-501/-Users-srm-dev-conway99-funsearch/ead2d61b-ebf6-4654-abeb-2f2226dceb95/scratchpad/iryu_1784988482
2026-07-25T14:34:51.267670Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 88 column 5
 succeeded in 4237ms:
new 22 (22, (6, [[2, 3, 4], [0, 2], [3, 5], [1, 5], [1, 2, 3], [0, 1, 4]], (5, 4, 3, 3, 2, 5), (5, 4, 3, 3, 2, 5), 20573))
new 22 (13, (6, [[2, 4, 5], [0, 2, 4], [4, 5], [0, 1, 2], [3, 5], [1, 3]], (2, 4, 2, 4, 6, 4), (2, 4, 2, 4, 6, 4), 26993))
new 22 (7, (6, [[2, 4, 5], [0, 3], [1, 3], [0, 4, 5], [1, 2], [1, 2, 4]], (5, 6, 3, 3, 4, 1), (5, 6, 3, 3, 4, 1), 35789))
new 23 (8, (5, [[1, 2], [3, 4], [1, 4], [0, 2], [0, 3]], (5, 4, 5, 3, 6), (5, 4, 5, 3, 6), 75277))
new 23 (7, (5, [[1, 2], [3, 4], [1, 3], [0, 4], [0, 2]], (6, 4, 4, 6, 3), (6, 4, 4, 6, 3), 105076))
new 22 (6, (6, [[3, 4, 5], [0, 3, 4], [0, 1, 4], [2, 5], [3, 5], [1, 2]], (2, 5, 4, 5, 2, 4), (2, 5, 4, 5, 2, 4), 119698))
new 23 (6, (5, [[3, 4], [0, 3], [0, 1], [2, 4], [1, 2]], (5, 5, 4, 4, 5), (5, 5, 4, 4, 5), 230389))
new 21 (6, (6, [[1, 4, 5], [2, 3], [0, 4, 5], [0, 2, 4], [1, 5], [1, 3]], (1, 5, 5, 3, 3, 4), (1, 5, 5, 3, 3, 4), 233930))
feasible 127 best {20: (999, None), 21: (6, (6, [[1, 4, 5], [2, 3], [0, 4, 5], [0, 2, 4], [1, 5], [1, 3]], (1, 5, 5, 3, 3, 4), (1, 5, 5, 3, 3, 4), 233930)), 22: (6, (6, [[3, 4, 5], [0, 3, 4], [0, 1, 4], [2, 5], [3, 5], [1, 2]], (2, 5, 4, 5, 2, 4), (2, 5, 4, 5, 2, 4), 119698)), 23: (6, (5, [[3, 4], [0, 3], [0, 1], [2, 4], [1, 2]], (5, 5, 4, 4, 5), (5, 5, 4, 4, 5), 230389))}

codex
`n=20..23` の探索では、既知の `n=20` 例が `S=5`、ランダム探索で `n=21,22,23` は最良 `S=6` まで見つかりました。これらは全探索ではないため、「見つかった最小」として扱います。最後に、提示する各例の `δ⁺` と `S` を再計算して整合性を確認します。
exec
/bin/zsh -lc 'python3 -c $'"'
from collections import Counter

def calc(m,adj,s,c):
 off=[0]
 for x in s: off.append(off[-1]+x)
 n=off[-1]; cm=[((1<<off[a+1])-(1<<off[a])) for a in range(m)]; A=[0]*n
 for a in range(m):
  ext=0
  for b in adj[a]: ext|=cm[b]
  base=off[a]
  for j in range(s[a]):
   lim=min(j,c[a]); A[base+j]=ext | (((1<<(base+lim))-(1<<base)) if lim else 0)
 S=0; vals=[]
 for v,mask in enumerate(A):
  R=0; mm=mask
  while mm:
   l=mm&-mm; y=l.bit_length()-1; R|=A[y]; mm-=l
  R &= ~mask; R &= ~(1<<v)
  d=mask.bit_count(); b=R.bit_count(); t=max(0,b-d+1)
  vals.append((d,b,t)); S+=t
 return n,min(d for d,b,t in vals),S,Counter(vals),Counter(t for d,b,t in vals)
examples={
\"n20_5cycle\":(5,[[1,2],[2,3],[3,4],[0,4],[0,1]],[4,4,4,4,4],[1,1,1,1,1]),
\"n21_found\":(6,[[1,4,5],[2,3],[0,4,5],[0,2,4],[1,5],[1,3]],[1,5,5,3,3,4],[1,5,5,3,3,4]),
\"n22_found\":(6,[[3,4,5],[0,3,4],[0,1,4],[2,5],[3,5],[1,2]],[2,5,4,5,2,4],[2,5,4,5,2,4]),
\"n23_found\":(5,[[3,4],[0,3],[0,1],[2,4],[1,2]],[5,5,4,4,5],[5,5,4,4,5]),
\"n24_S3\":(4,[[2],[0,3],[1,3],[0]],[8,6,8,2],[8,6,8,2]),
\"n25_S4\":(3,[[2],[0],[1]],[8,9,8],[8,9,8]),
\"n27_S3\":(3,[[1],[2],[0]],[9,9,9],[9,9,9]),
}
for name,args in examples.items():
 print(name, calc(*args)[:3], \"terms\", calc(*args)[4])
'" in /private/tmp/claude-501/-Users-srm-dev-conway99-funsearch/ead2d61b-ebf6-4654-abeb-2f2226dceb95/scratchpad/iryu_1784988482
 succeeded in 0ms:
n20_5cycle (20, 8, 5) terms Counter({0: 15, 1: 5})
n21_found (21, 8, 6) terms Counter({0: 16, 1: 4, 2: 1})
n22_found (22, 8, 6) terms Counter({0: 17, 1: 4, 2: 1})
n23_found (23, 9, 6) terms Counter({0: 18, 1: 4, 2: 1})
n24_S3 (24, 8, 3) terms Counter({0: 21, 1: 3})
n25_S4 (25, 8, 4) terms Counter({0: 22, 1: 2, 2: 1})
n27_S3 (27, 9, 3) terms Counter({0: 24, 1: 3})

2026-07-25T14:35:17.314217Z ERROR codex_models_manager::manager: failed to renew cache TTL: missing field `supports_reasoning_summaries` at line 88 column 5
codex
計算しました。結論から言うと、あなたが指定した `n=20` 例は「`n<24` で空」を反証しますが、主張本体 `S≥3` や `S=3 ⇒ 3|n` の反例にはなりません。

**1. n=20 例**
対象:

- `m=5`
- `H`: `Z/5Z` 上で `a -> a+1, a -> a+2`
- `n_a=4` 全クラス
- `c_a ∈ {0,1,2,3,4}` 全 `5^5=3125` 通り

全探索結果:

```text
最小 S = 5
S の分布:
S=5   : 1024 通り
S=8   : 1280 通り
S=11  : 640 通り
S=14  : 160 通り
S=17  : 20 通り
S=20  : 1 通り
```

代表値:

```text
c=(0,0,0,0,0): S=20
c=(1,1,1,1,1): S=5
c=(2,2,2,2,2): S=5
c=(3,3,3,3,3): S=5
c=(4,4,4,4,4): S=5
```

例えば `c=(1,1,1,1,1)` では:

```text
n=20, min outdeg=8, S=5
term 分布: 0 が15頂点、1 が5頂点
```

したがって、この `n=20` 例には `S=3` も `S≤2` もありません。

**2. n<24 の探索**
まず非空になる最小 `n` は `20` です。これは厳密に確認できます。

理由は、欠弧のある `H` が条件を満たすなら、欠弧を足してトーナメントにしても各外部出次数和は減らないため、非空最小 `n` の探索はトーナメント基礎 `H` に絞ってよいからです。`scipy.optimize.milp` で各強連結トーナメントに対して

```text
minimize Σ n_a
subject to n_a >= 1
         Σ_{a->b} n_b >= 8  for every a
```

を解いた結果:

```text
m=3: 最小 n = 24
m=4: 最小 n = 24
m=5: 最小 n = 20
m=6: 最小 n = 20
```

よって族は `n=20` から非空です。

`n<24` の `S` については、完全全探索は `m=6` と `c` の直積で重く、今回は可能範囲の探索です。見つかった最良値は:

```text
n=20: S=5  （上の m=5 正則トーナメント例、c=(1,1,1,1,1)）
n=21: S=6  （探索で発見）
n=22: S=6  （探索で発見）
n=23: S=6  （探索で発見）
```

確認済みの例:

```text
n=21, min outdeg=8, S=6
term 分布: 0 が16頂点、1 が4頂点、2 が1頂点

n=22, min outdeg=8, S=6
term 分布: 0 が17頂点、1 が4頂点、2 が1頂点

n=23, min outdeg=9, S=6
term 分布: 0 が18頂点、1 が4頂点、2 が1頂点
```

少なくとも探索範囲では `n<24` に `S≤3` は見つかっていません。

**3. n=24〜30 の反例探索**
ランダム探索 50万試行、各候補につき複数の `c` を試しました。反例、つまり

- `S≤2`
- または `S=3` かつ `3∤n`

は見つかりませんでした。

見つかった最良値:

```text
n=24: S=3
n=25: S=4
n=26: S=4
n=27: S=3
n=28: S=4
n=29: S=4
n=30: S=3
```

`S=3` が出たのは、今回の探索では `n=24,27,30` のみで、いずれも `3|n` です。

例:

```text
n=24, m=4
H adjacency:
0 -> {2}
1 -> {0,3}
2 -> {1,3}
3 -> {0}
n = (8,6,8,2)
c = (8,6,8,2)
min outdeg=8
S=3
```

```text
n=27, m=3
H: directed 3-cycle
n = (9,9,9)
c = (9,9,9)
min outdeg=9
S=3
```

まとめると、「`n<24` で空」は明確に false です。ただし、今回の計算範囲では主張本体 `S(G)≥3` および `S(G)=3 ⇒ 3|n` の反例は見つかっていません。
tokens used
107,600
計算しました。結論から言うと、あなたが指定した `n=20` 例は「`n<24` で空」を反証しますが、主張本体 `S≥3` や `S=3 ⇒ 3|n` の反例にはなりません。

**1. n=20 例**
対象:

- `m=5`
- `H`: `Z/5Z` 上で `a -> a+1, a -> a+2`
- `n_a=4` 全クラス
- `c_a ∈ {0,1,2,3,4}` 全 `5^5=3125` 通り

全探索結果:

```text
最小 S = 5
S の分布:
S=5   : 1024 通り
S=8   : 1280 通り
S=11  : 640 通り
S=14  : 160 通り
S=17  : 20 通り
S=20  : 1 通り
```

代表値:

```text
c=(0,0,0,0,0): S=20
c=(1,1,1,1,1): S=5
c=(2,2,2,2,2): S=5
c=(3,3,3,3,3): S=5
c=(4,4,4,4,4): S=5
```

例えば `c=(1,1,1,1,1)` では:

```text
n=20, min outdeg=8, S=5
term 分布: 0 が15頂点、1 が5頂点
```

したがって、この `n=20` 例には `S=3` も `S≤2` もありません。

**2. n<24 の探索**
まず非空になる最小 `n` は `20` です。これは厳密に確認できます。

理由は、欠弧のある `H` が条件を満たすなら、欠弧を足してトーナメントにしても各外部出次数和は減らないため、非空最小 `n` の探索はトーナメント基礎 `H` に絞ってよいからです。`scipy.optimize.milp` で各強連結トーナメントに対して

```text
minimize Σ n_a
subject to n_a >= 1
         Σ_{a->b} n_b >= 8  for every a
```

を解いた結果:

```text
m=3: 最小 n = 24
m=4: 最小 n = 24
m=5: 最小 n = 20
m=6: 最小 n = 20
```

よって族は `n=20` から非空です。

`n<24` の `S` については、完全全探索は `m=6` と `c` の直積で重く、今回は可能範囲の探索です。見つかった最良値は:

```text
n=20: S=5  （上の m=5 正則トーナメント例、c=(1,1,1,1,1)）
n=21: S=6  （探索で発見）
n=22: S=6  （探索で発見）
n=23: S=6  （探索で発見）
```

確認済みの例:

```text
n=21, min outdeg=8, S=6
term 分布: 0 が16頂点、1 が4頂点、2 が1頂点

n=22, min outdeg=8, S=6
term 分布: 0 が17頂点、1 が4頂点、2 が1頂点

n=23, min outdeg=9, S=6
term 分布: 0 が18頂点、1 が4頂点、2 が1頂点
```

少なくとも探索範囲では `n<24` に `S≤3` は見つかっていません。

**3. n=24〜30 の反例探索**
ランダム探索 50万試行、各候補につき複数の `c` を試しました。反例、つまり

- `S≤2`
- または `S=3` かつ `3∤n`

は見つかりませんでした。

見つかった最良値:

```text
n=24: S=3
n=25: S=4
n=26: S=4
n=27: S=3
n=28: S=4
n=29: S=4
n=30: S=3
```

`S=3` が出たのは、今回の探索では `n=24,27,30` のみで、いずれも `3|n` です。

例:

```text
n=24, m=4
H adjacency:
0 -> {2}
1 -> {0,3}
2 -> {1,3}
3 -> {0}
n = (8,6,8,2)
c = (8,6,8,2)
min outdeg=8
S=3
```

```text
n=27, m=3
H: directed 3-cycle
n = (9,9,9)
c = (9,9,9)
min outdeg=9
S=3
```

まとめると、「`n<24` で空」は明確に false です。ただし、今回の計算範囲では主張本体 `S(G)≥3` および `S(G)=3 ⇒ 3|n` の反例は見つかっていません。
```
