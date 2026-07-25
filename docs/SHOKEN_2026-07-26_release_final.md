# 所見: v0.2.0 公開前最終審査(release/v0.2.0、note v2.0 を含む全体)

日付: 2026-07-26 / 監修: kanshu(新規クリーン文脈、起草側の会話ログ不参照)
対象: 公開リポジトリ `/Users/srm/dev/seymour-excess` ブランチ `release/v0.2.0`
(HEAD 7464c07)。note v2.0(`note/measuring-the-moat.tex` /
`measuring-the-moat-v2.0.pdf`)、README、Makefile、RELEASING.md、CHANGELOG.md、
verify/・blowup/・constructions/・data/ の実体。
内部リポジトリは読み取りのみで参照した。

---

## 1. 要旨

**全体判定: 条件付き受理。数学と検証装置は全て監修の独立再計算で成立。
現状のままのタグ付けは不可 — ただし残る差し戻し3件はいずれも散文の局所修正
(各10分以内)であり、反映後は公開可。**
最重要の指摘: (D1) provenance 節のフィールド数が実データと不一致
(excess3 は13[記載12]、gkz は6/7混在[一様7と記載])、(D2) note §1
「Every witness is stored in the accompanying repository」が §5.2 の
101..150 帯の主張(witness 未同梱)と矛盾、(D3) README の「floor 11回」が
grep 再現で12。三つとも「検証可能」を売りにする文の中の検証可能な誤りである。

## 2. 主張別所見表

| # | 主張 / 審査点 | 判定 | 根拠(1行) |
|---|---|---|---|
| T7(Thm 2.6、Lemma 2.1–2.5 の連鎖) | **受理** | 証明を全行再導出(§4-1)。note 仕様のみから G_n を監修の独立実装で再構成し41値(24..60, 99, 100, 149, 150)全一致(§3.1)。fresh clone で verify-t7 / t7-spec green |
| T7 の系(E ≤ E^sc ≤ 3+[3∤n]) | 受理 | witness が強連結なので両方を抑える。min の単調性、向き正しい |
| T8(Prop 3.1、E_{δ≥k}(2k+1)=2k+1) | **受理**(磨き1件、非ブロッカー) | 弧数ピンチ+2-king 論法を再導出。circulant 496・walk 2000 再実行 green。「Hence」にクラス非空(circulant が witness)の明示が無い — 一行追加を推奨(§6-3) |
| Prop 3.1 末文(N⁺⁺(v)=N⁻(v) → 強連結 → 両最小一致) | 受理 | 挟み込み等号から N⁺⁺=N⁻、全頂点間距離 ≤2。再導出済み。定義ゲート通過 |
| T9(Thm 4.1 / App B、README は逐語引用) | **受理** | fresh clone で4検査再現: 73/73・2,321,385(違反0)・357(全て ≡0 mod 3)・146(全不能)。README 引用は note と逐語一致 |
| T9 の 4,313 = 1+4+76+4,232 | **受理**(前回の条件解消) | nauty+自前 SCC フィルタで 1, 4, 76, **4232** を再列挙。m=3,4,5 は nauty 非依存の純 Python 全走査でも一致(§3.3)。前回未再計算だった m=6 が今回埋まった |
| T9 の最小メンバー n=20、min n = 24,24,20,20 | 受理 | membership 条件(δ⁺ = min_a Σ_{b∈N⁺_H(a)} n_b)を自前導出し、全商×全組成で再計算、4値一致(§3.4) |
| T6(Prop 3.3、7 ≤ n ≤ 30) | 受理 | 公開 jsonl: 7..30 全 INFEASIBLE(n=29 は UNKNOWN 14,400s と INFEASIBLE 29,505.8s の両行保存)、hypcheck 24値全 hypothesis_ok。散文の「両行とも保存」「最薄ログ」の開示は正確 |
| T2(§3.3 の格下げ記録) | 受理 | 公開ログ実査: n17 cap2 = UNKNOWN 900s / INFEASIBLE 218.9s / INFEASIBLE 357.0s(hash+ortools 付き)、cap3 1,356.4s、cap4 3,083.0s、19–20 UNKNOWN 1,800s、18–22 cap2 UNKNOWN 3,600s、tournament 12行 UNKNOWN — 全て note・README と一致 |
| T5(Pisa Conj 5.1 反証) | 受理 | fresh clone で verify-t5 green。Rmk 6.2 の参照先は PDF 実物に存在 |
| M1(77値) | 受理 | fresh clone で 77/77 再採点 green。「measurement, not a claim」「no lower-bound content」の囲い込み適切。check_m1.py の docstring も caveat を明記 |
| **provenance 節(note §3.4 / README)のフィールド数** | **差し戻し(D1)** | excess3_probe は**13**フィールド(記載 twelve/12)。gkz は n=7,8,9 の3行が **6**(hypothesis_only 欠落)で残り22行が7 — 「一様7」と読める記載と乖離。「Measured field by field」を掲げる節での値の誤り |
| **note §1 検証プロトコル文 vs §5.2 の 101..150(40/10)** | **差し戻し(D2)** | manifest の最大 n は 100。101..150 の「best stored witness」50本は公開側に無く、「Every witness is stored in the accompanying repository」と矛盾。数値40/10自体は内部記録と整合(監修が内部 REPORT_SONAR §4.8 で確認)だが公開物からは再現不能 |
| **README「floor は11回」** | **差し戻し(D3)** | grep 再現は**12**トークン(本文10+タイトル2)。「うち3回が the measured floor」は正(行跨ぎ1を含む)が、「残りは 'the floor' applied to a measured value」も厳密には2件(引用句 "floor = minimal legal skeleton size"、被引用ノート題名)が該当しない。数え方の規則を書くか数を直す |
| 乖離ゲート: claim table 全10行の参照先 | 受理 | tectonic 再ビルド(EXIT=0、未定義参照0、`??` 0)→ pdftotext で Thm 2.6 / Prop 3.1 / Prop 3.3 / Thm 4.1 / App B / Rmk 6.1 / Rmk 6.2 / §2.3 / §3.3 / §5.1 Table 2 の実在を確認。shipped PDF と再ビルドはテキスト完全一致 |
| Table 1 / Table 2 の番号 | 受理 | 両方 table_generated.tex 内に実在。README「Table 2」・note 本文「Table 1」はどちらも正。make_table.py 再生成で diff なし |
| E_δ / E_δ^sc の分離(審査点2) | 受理 | 定義・主張ごとの効き方(sc witness は両方 / 無連結制約の不能性は大→小)とも論理に穴なし。App A の「省略は緩和」の向きも正しい |
| 新規性ラベル(T8=folklore、T7/T9=new candidate) | 受理 | v1.1 tex 449行の GKZ Lem 2.2 引用を実物確認。folklore ラベルの論拠(note 自身の引用で足りる)は前回所見の裁定どおり |
| RELEASING.md の実行可能性(審査点5) | **条件付き受理** | 8項目中6項目は監修が実際に実行して通した。**不能2件**: `make verify-d2core-t2` は Makefile に存在しない(C2)、`git grep -I "sk-ant"` はチェックリスト自身が自己マッチし字義通りには永遠に非空(C2) |
| LICENSE のディレクトリ列挙 | 条件付き受理(C1) | v0.2.0 で追加された blowup/・lib/・docs/ が dual-license の列挙に無い |
| v1.1 凍結・authority 移行の記述 | 受理 | note_draft_v1.tex は v1.1 化以降未編集(git log 実査)。note/README.md の経緯説明は正確 |
| DOI 群 | 受理(1件要オーナー確認、C4) | concept DOI 2件は内部照合記録と一致。ただし version DOI 21497889 の帰属が tex コメント(v1.1)と note/CHANGELOG.md(v1.0)で矛盾 — Zenodo 実物での確認はオーナーのみ可能 |
| README 未解決問題4(340行/12/36) | 条件付き受理(C5) | 数値は前回所見で内部記録と照合済みだが、公開側 experiments/delta8/ はツール3本のみで結果ログ無し。note の未解決問題リストにも無い。「internal measurement, logs not shipped」の一言か、ログ同梱を |

## 3. 再計算ログ(抜粋、すべて監修自身が実行)

### 3.1 T7: note 仕様のみからの独立再構成(第3実装)

リポジトリのコードを一切共有しない監修自前の builder + BFS scorer で:

```
$ python3 scratchpad/gn_indep.py
orders tested: 41            # 24..60 全部 + 99, 100, 149, 150
failures: none
sample n=25:  (4, 8, True, 1)    # exc 4, δ+=8, strong, margin+1 が1個
sample n=150: (3, 50, True, 0)
```

### 3.2 fresh clone での全ターゲット

```
$ git clone --branch release/v0.2.0 … sx-fresh && make verify-all   → EXIT=0
  PASS hashes: 95 graphs match manifest / PASS t1 t1p o1 t5 t2 t6
  254 graphs scored, margins closed form exact on 254/254
  witnesses scored: 77, failures: 0
$ make verify-t1 verify-t1p verify-o1 verify-t5 verify-t2 verify-t6 verify-hashes
  → すべて EXIT=0
$ make verify-t9   → EXIT=0
  [A] 73/73 agree  [B] 2,321,385 evaluations / 4313 quotients, 違反0
  [C] 357 cone elements, 1ᵀh ≢ 0 mod 3 は 0件  [D] 146 models, feasible 0
$ tectonic -X compile note/measuring-the-moat.tex → EXIT=0、undefined 0、?? 0
$ diff <(shipped PDF text) <(rebuilt PDF text) → 一致
$ python3 note/make_table.py → EXIT=0、tracked ファイルに diff なし
```

### 3.3 商数 4,313 の独立再列挙(前回所見の宿題 m=6 を含む)

```
# nauty + 監修自前の強連結フィルタ:
m=3: orientations 5,     strongly connected 1
m=4: orientations 34,    strongly connected 4
m=5: orientations 535,   strongly connected 76
m=6: orientations 20848, strongly connected 4232      # 合計 4,313 ✓
# nauty 非依存(純 Python、3^C(m,2) 全走査 + 正準形): m=3:1, m=4:4, m=5:76 ✓
```

### 3.4 blow-up 族の最小メンバー(membership 条件を自前導出)

```
# δ⁺(H[n;c]) = min_a Σ_{b∈N⁺_H(a)} n_b(u_{a,0} の (T) 弧は空)を導出し、
# 全商(§3.3 の列挙)× n_a ∈ 1..8(最小解は n_a ≤ 8 で足りる)で最小化:
m=3 min n = 24   m=4 min n = 24   m=5 min n = 20   m=6 min n = 20   # 記載と一致
```

### 3.5 ソルバーログの実査(D1 の根拠)

```
excess3_probe_results.jsonl の行キー数: 13
  [cap, delta, model_hash, n, ortools_version, status, symmetry,
   time_limit, tool, tournament, wall, wall_time_seconds, workers]
  → note「records twelve fields」/ README 表「12」と乖離
gkz82_results.jsonl のキー数分布: {7: 22行, 6: 3行}   # 6 は n=7,8,9
  (hypothesis_only 欠落)→「conjecture, k, n, two model flags, status,
  wall time」の一様な列挙と乖離
excess2_results.jsonl: [4,4,4,4,4,4,4,7]、n=17 は 4,4,7 → 記載どおり ✓
gkz 7..30 全 INFEASIBLE(29 は UNKNOWN 14,400.4s + INFEASIBLE 29,505.8s)✓
hypcheck 24行(7..30)全 hypothesis_ok ✓
```

### 3.6 floor の再計数(D3 の根拠)

```
$ git show v0.1.0:README.md | grep -o floor | wc -l   → 12
内訳: タイトル行1・引用題名(152行)1・本文10。
"the measured floor" は3回(52行、106–107行の行跨ぎ、114行)→ この部分は正 ✓
本文の非該当2件: 73行の引用句 "floor = minimal legal skeleton size"、
152行の被引用ノート題名 — 「the rest as 'the floor' applied to a measured
value」に収まらない
```

### 3.7 101..150 帯(D2 の根拠)

```
data/manifest.json: 95 entries、ファイル名中の最大 n = 100
data/sonar_best/: 77本(24..100)のみ。n>100 の witness・掃引ログは公開側に無い
(数値 40/10 自体は内部 REPORT_SONAR_2026-07-25.md §4.8 と整合:
 修復帯25値中10値が5〜6 → 50値中40一致・10超過。読み替えの誤りは無い)
```

## 4. 反駁の試みと結果

1. **Thm 2.6 への反駁(失敗)**: 共有バグの可能性を消すため、note の散文仕様
   だけから監修自前実装で G_n を再構成し、リポジトリと無関係な scorer で
   41値を採点 → 全一致(§3.1)。端(24, 150)と両剰余類も含む。
   Lemma 2.4 が暗黙に使う Δ_a ∈ {−1,0,1} の範囲外(Δ ≤ −2)が生じる n が
   無いかも確認 — profile lemma により構成上生じ得ない。**反駁失敗**
2. **T9 の数値への反駁(失敗)**: 4,313・73・2,321,385・357・146 のいずれかが
   再現しなければ App B は崩れる → fresh clone の4検査 + 監修の二重列挙
   (nauty 系と純 Python 系)で全て再現。**反駁失敗**
3. **provenance 節への反駁(成功 → D1)**: 「Measured field by field」を
   文字通り検算 → excess3 の 12→13、gkz の一様7→6/7 混在の2件が乖離。
   excess2 の「4, and 7 on one row」は正確だった
4. **「Every witness is stored」への反駁(成功 → D2)**: §5.2 が値を引く
   101..150 の witness 50本を manifest・data/ に探索 → 不在。
   note の検証プロトコル文と自己矛盾
5. **floor 計数への反駁(成功 → D3)**: 「checkable against the archived
   v0.1.0」を文字通り実行 → 11 ではなく 12(§3.6)
6. **Prop 3.3 の範囲への反駁(失敗)**: 走査に穴(INFEASIBLE でない n、
   空虚な hypothesis)がないか全行照合 → 7..30 完全被覆、hypcheck 全通過
7. **shipped PDF への反駁(失敗)**: tex から再ビルドしテキスト比較 → 一致。
   「PDF だけ古い/手で直した」の可能性は消えた

## 5. 差し戻し事項(公開前必須 — いずれも散文の局所修正)

- **D1(note §3.4 と README provenance 表)**: excess3 を「thirteen fields」
  (または数え方の規則を明記)に、gkz を「seven fields on 22 rows and six on
  the three fastest (n = 7–9, which lack `hypothesis_only`)」に修正。
  修正文例(note): "The reachability probe … records thirteen fields
  including model hash, solver version and worker count." /
  "the GKZ scan records conjecture, k, n, one or two model flags, status and
  wall time — the three fastest rows lack `hypothesis_only` — and no model
  hash, solver version, seed or worker count."
- **D2(note §1 と §5.2、README 該当節)**: 選択肢は2つ。
  (a) 101..150 の best witness(または各 n の best excess を記録した小さな
  jsonl)を data/ に同梱して manifest に載せる、または
  (b) §1 を "Every witness behind a claim in the tables is stored …" に
  絞り、§5.2 と README の当該文に "(the 50 witnesses above the surveyed band
  are recorded in the project archive and are not shipped with this release)"
  を追記。(b) が安い。どちらでも T7 の定理値が上界を与えるので数学は不変
- **D3(README 用語節)**: 「the word appears 11 times there」を
  「12 times (including the title and the citation)」にするか、数え方の規則
  (例: 見出しを除く本文、と書くなら 10)を一行で固定する。あわせて
  「the rest as 'the floor' applied to a measured value」を「the rest applied
  to measured values, one of them inside the quoted hypothesis
  'floor = minimal legal skeleton size'」程度に緩める

## 6. 条件(公開はブロックしない。タグ前に安く済むなら D 群と同時に)

- **C1**: LICENSE のディレクトリ列挙に `blowup/`・`lib/`(MIT)と `docs/`
  (CC-BY か MIT、方針に合わせて)を追加
- **C2**: RELEASING.md の `make verify-d2core-t2` は存在しないターゲット —
  「`python3 -m pytest lib/dist2core/tests/test_n17_infeasible.py`」等の実在
  コマンドに差し替え。`git grep -I "sk-ant"` はチェックリスト自身が自己マッチ
  するため字義通りには常に非空 — パターンを `sk-ant-` にする等の回避を明記
- **C3**: tex ヘッダコメントの旧番号(Thm 2.4 → 2.6、Thm 5.1/App C →
  4.1/App B、Section 4.1 → 5.1)。描画されないが source of record 内の乖離
- **C4**: version DOI 21497889 の帰属が tex コメント(v1.1)と
  note/CHANGELOG.md(v1.0)で矛盾。Zenodo 実物で確認できるのはオーナーのみ
  — **要エスカレーション(オーナー確認)**。どちらかの1行を直す
- **C5**: README 未解決問題4の 340行/12/36 に「(internal measurement; logs
  not shipped)」を付すか delta8 の結果 jsonl を同梱。あわせて README と note
  の未解決問題リストの差(README にのみ δ=8 局所可行性・GKZ k≥4、note に
  のみ global counting・transplant lemma)を、「README は note の写像」の
  宣言と整合する一言(例: "problems 4 and 6 are repository-level records not
  restated in the note")で断る
- **C6**: verify-t9 の所要時間表記の統一(README「~2 min」vs Makefile
  「~3.5 min」)
- **C7**(磨き): Prop 3.1 の「Hence」の前にクラス非空の一言(「the rotational
  tournament witnesses non-emptiness for every k」)。Makefile verify-t7 の
  コメント「3 implementations」は3実装照合が14値の抜き取りである旨を併記
  (全数は自前 scorer、`--cross-all` で全数照合可能なら明記)

## 7. 理論所見(提案、拘束力なし)

1. **(自信度: 高)note v2.0 の数学は健全。** Lemma 2.1–2.5 → Thm 2.6 の連鎖に
   隙間はない。Lemma 2.4 の Lemma 2.5 前方参照は非循環(2.5 は直接代入のみで
   閉じ、2.4 に依存しない)であり、「below」と明示されているので妥当。
   Lemma 2.1 は以降の証明に論理的には使われない動機付けだが、その旨は
   「This is the mechanism … in bulk」の一文で示されており誤解の余地は小さい
2. **(自信度: 高)Thm 4.1 / App B の囲い込みは十分。** 定理名に
   「restricted to F」、本文に否定文2連、README は逐語引用+「quote it; do
   not summarise it」。一般下界への誤読経路は残っていない
3. **(自信度: 中)D2 は (a)(データ同梱)を推す。** 「探索が構成に負けた」
   ことは本 note の方法論的主結果であり、その一次証拠(10値の 5〜6)を
   アーカイブ外に置くのは主張の性質上惜しい。50行の jsonl で足りる
4. **(自信度: 高)過大主張は検出されなかった。** "essentially settled" 系の
   語は否定文にのみ出現。測定値を最小値と読ませる箇所は用語節・M1 行・
   §5.2 で三重に封じられている。新規性ラベルの三分類も前回裁定と整合

## 8. 資源配分への意見

1. D1–D3 の修正は合計30分未満の散文作業で、新規計算は不要。修正後の再タグ
   前に `make verify-all`(fresh clone)と tectonic ビルドの2点だけ回し直せば
   よい(本審査でコマンドは全て検証済み)
2. C4(DOI 帰属)だけはオーナーの Zenodo 画面でしか裁定できない。タグ前の
   1分の確認を推奨
3. これ以上の数値検証は不要。本審査で T7 は第3実装まで、T9 は m=6 商数まで
   埋まり、全 claim 行が独立再現された。凍結方針(残件は kanshu-1 の
   ストレステストのみ)と整合する

## 9. 公開可否の明示(依頼への直接回答)

**現状のままのタグ付け・公開: 不可**(D1–D3。いずれも DOI で永久固定される
散文中の、grep で反証可能な記述)。
**D1–D3 反映後: 公開可。** C 群は後続コミットで構わない(ただし C1・C2 は
数分なのでタグ前推奨、C4 はオーナー確認のみ)。主張本体(T7/T8/T9/T6/T2/
T5/M1)と検証装置に、本審査の独立再計算で崩れたものは一つもない。
