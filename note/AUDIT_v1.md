# note_draft_v1 事実監査レポート

監査者: Claude Code / 2026-07-22 夜。方針: 本文は一切修正せず、台帳
(data/ + manifest + 感度・flip2 出力 + 実行記録)との相違のみ列挙。
修正判断は監修。**[要修正]** = 台帳と食い違う記述、**[注記]** = 補強推奨。

## A. 台帳と食い違う記述

1. **[要修正] §5「ring witness's non-survivors all sit at margin exactly −1」は誤り。**
   28da4a1e (n=50) の実マージン分布は {−5:1, −4:1, −3:4, −2:17, −1:22, 0:5}。
   非生存者45個のうち −1 は22個。−5 までの裾がある。
   「keystone は深い赤字尾(−15)、ring は浅い」という対比自体は成立する
   (−5 vs −15)が、「exactly −1」は成り立たない。

2. **[要修正] §5「killing any survivor promotes a reserve … an equal trade」の
   "any" は過大。** sensitivity_n50 の実測: v8/v16/v23/v47 は best flip
   dE_total +0(等価交換)だが **v36 は +2**。「4 of 5 survivors admit an
   equal trade; one (v36) costs +2」が正確。

3. **[要修正] §3.1 の witness 欄のハッシュ種別が不統一。**
   `ad5efc8b` `ca40b396` は **generator-code lineage id**(ファイル名由来)、
   `28da4a1e` も同様。一方本プロジェクトの公開規約では graph の同一性は
   canonical adjacency sha1 (manifest 記載)で示す。graph hash は
   ad5efc8b→`ead3c3c3…`、ca40b396→`dc922e89…`、28da4a1e→`17cd7dc8…`。
   生成した完全表(§B)は graph hash に統一済み。本文の選抜表も統一を推奨。

4. **[要修正] Abstract「machine-verified measurements for 24 ≤ n ≤ 75」。**
   測定・witness の実在範囲は **25 ≤ n ≤ 75**(n=24 の witness/測定は
   台帳に存在しない。T1 により E(24)≤3 は定理として言えるが「measurement」
   ではない)。「25 ≤ n ≤ 75」への修正、または n=24 witness の追加生成
   (pure_ring.py --n 24、1秒)のどちらかを。

5. **[要修正] §7「simulated annealing over a triangle/arc representation」。**
   本プロジェクトの探索は island-model LLM 進化のみ。焼きなまし・
   triangle/arc 表現はリポジトリに存在しない(別プロジェクトの混入?)。
   削除または「(not used in the results reported here)」の明示を。

6. **[注記] 発注文の照合数値「194」は台帳のどこにも存在しない。**
   sensitivity/flip2 の実数値は 2450 (n=50 flips), 2756 (n=53 flips),
   171,288 (有効2手ペア), 7,712 (中立ペア), 104 (|F1|), 1,700 (|F2|)。
   194 は 104 の記憶違いの可能性。初稿本文には 194 は現れないため実害なし。

## B. プレースホルダの解決(挿入値)

7. **§4.1 [Code: model reference + wall time]:**
   モデル = `experiments/delta8/excess2_search.py`(--n 17 --cap 2,
   random_seed 1, workers 8)。**INFEASIBLE, wall time 218.9 s**
   (record: `data/excess2_results.jsonl`)。同 jsonl には先行する
   900 s 予算・4 workers の UNKNOWN 記録も残っている(異なる設定の
   打ち切り。矛盾ではないが、引用時は 218.9 s の INFEASIBLE を指すこと)。
   **[注記]** この jsonl には delta8_table.jsonl と違い model_hash /
   ortools_version フィールドが無い。公開前に T2 レコードへ両フィールドを
   追記する再実行(4分)を推奨。

8. **§3.1 完全表**: `note/make_table.py` が data/en_sweep + manifest +
   構成上界から機械生成(手書き禁止)。生成結果は note_draft_v1.tex に
   挿入済み。選抜表との相違: 特になし(数値一致)。

## C. Lemma 2.1 の帳簿(発注の注意事項への回答)

9. **p ∈ N₂⁺(v) の場合、margin(v) は −1 でなく −2 変化する。**
   弧 v→p の追加で d₁(v) は +1、かつ p が N₂⁺(v) から N₁⁺(v) へ移動して
   d₂(v) が −1(out-set inclusion により新規の2歩先は生じないため)。
   従って現行の「d₂ 不変・margin ちょうど −1」は p が距離 ≥3 の場合のみ。
   層状構成では p_i への層内距離が常に m ≥ 3 なのでこのケースは生じない
   (初稿の自己注記の通り)。keystone 記述(§2.3)は既存グラフの記述であって
   弧追加操作ではないため影響なし。反例的配置とまでは言えないが、
   補題の主張は場合分けが必須。

## D. 照合済み・一致した数値(抜粋)

- §2.3 翼の一致: N⁺(34) = N⁺(35) = N⁺(18) ∪ {18} を集合として厳密確認。
  記録: `data/cluster_structure_n53.txt`(graph_sha1 dc922e89…)
- §5 感度: 2450 flips (n=50) / 2756 flips (n=53) / 非対角 +1,+1 は
  keystone 行のみ — 出力ファイルと一致
- §5 二手攻撃: 171,288 有効ペア、dE<0 ゼロ、中立 7,712 — flip2 出力と一致
- §5 keystone 赤字尾 −15 — margin histogram と一致
- §3.2 統制値 13 (n=48) / 20 (n=50)、事前登録コミット実在 — 一致
- §3.3 δ≥9/10 で 5、divisor-ring witness の δ⁺=10 — 一致
- §4 n=18..22 各 3600 s UNKNOWN / トーナメント 17..28 12連続 UNKNOWN — 一致
- 表の選抜行 (27, 30, 47, 48, 49, 50, 51, 53, 57, 59) — 全て manifest と一致
- **[注記]** トーナメント n=17 行は T2 (一般 digraph INFEASIBLE) の部分クラスと
  して実は決着済み(README には明記済み)。§4 でも一言触れる余地あり。

## E. 監査対象外(コード台帳の外)

- §1 の文献数値(Huang–Peng の γ = 0.715538…、各文献の年号・帰属)は
  当方の台帳では検証不能。文献照合は監修の管轄。
- 著者表記(Cite as は Daiki Tahara で確定済み。初稿の [Raa full name /
  handle TBD] は要更新)。
