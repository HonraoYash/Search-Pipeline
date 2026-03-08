# =============================================================================
# pipeline.py — Orchestrator: runs full pipeline for all 10 query configs
# =============================================================================

import json
import os
import time
import argparse

from config import RETRIEVAL_TOP_K, RETRIEVAL_TOP_K_LARGE, MIN_HARD_PASS, FINAL_SUBMIT_K
from queries import QUERIES
from retrieval import fetch_candidates
from hard_filter import filter_candidates
from reranker import rerank
from evaluator import submit, print_summary
from query_rewriter import rewrite_query

# Configs where the original NL description is already better than rewritten
# These were performing well before rewriting — don't mess with them
NO_REWRITE_CONFIGS = {
    "mechanical_engineers.yml",
    "quantitative_finance.yml",
}


def print_eval_details(yml_name: str, result: dict):
    """Print detailed breakdown of eval response including individual scores."""
    print(f"\n  {'─'*52}")
    print(f"  EVAL RESULTS: {yml_name}")
    print(f"  {'─'*52}")
    print(f"  Average Final Score : {result.get('average_final_score', 'N/A')}")

    hard_scores = result.get("average_hard_scores", [])
    if hard_scores:
        print(f"  Hard Criteria:")
        for h in hard_scores:
            rate = h.get("pass_rate", 0)
            filled = int(rate * 10)
            bar = "█" * filled + "░" * (10 - filled)
            print(f"    [{bar}] {rate*100:.0f}%  {h['criteria_name']}")

    soft_scores = result.get("average_soft_scores", [])
    if soft_scores:
        print(f"  Soft Criteria:")
        for s in soft_scores:
            score = s.get("average_score", 0)
            print(f"    {score:.2f}/5  {s['criteria_name']}")

    individual = result.get("individual_results", [])
    if individual:
        print(f"  Individual Candidates:")
        for ind in individual:
            name   = ind.get("candidate_name", "Unknown")
            fscore = ind.get("final_score", 0)
            hard_pass = all(h.get("passes", False) for h in ind.get("hard_scores", []))
            status = "✅" if hard_pass else "❌"
            print(f"    {status} {name:<35} final={fscore}")
    print(f"  {'─'*52}")


def run_query(query: dict, submit_results: bool = True, use_rewriter: bool = True) -> dict:
    """Run the full pipeline for a single query config."""
    yml = query["yml_name"]
    print(f"\n{'='*60}")
    print(f"PROCESSING: {yml}")
    print(f"{'='*60}")

    # --- Stage 1: Query Rewriting ---
    if use_rewriter and yml not in NO_REWRITE_CONFIGS:
        print(f"  [pipeline] Rewriting query for better retrieval...")
        search_query = rewrite_query(query)
    else:
        if yml in NO_REWRITE_CONFIGS:
            print(f"  [pipeline] Using original query (rewriter disabled for {yml})")
        search_query = query["nl_description"]

    # --- Stage 2: Retrieve ---
    candidates = fetch_candidates(search_query, top_k=RETRIEVAL_TOP_K)

    # --- Stage 3: Hard filter ---
    passed = filter_candidates(candidates, query["hard_criteria"])

    # --- Fallback: if too few pass, retrieve more ---
    if len(passed) < MIN_HARD_PASS:
        # Anthropology needs much larger retrieval — relevant PhDs are rare
        large_k = 1000 if "anthropology" in yml else RETRIEVAL_TOP_K_LARGE
        print(f"  [pipeline] Only {len(passed)} candidates passed hard filter; retrying with top_k={large_k}...")
        candidates = fetch_candidates(search_query, top_k=large_k)
        passed = filter_candidates(candidates, query["hard_criteria"])
        print(f"  [pipeline] After larger retrieval: {len(passed)} candidates passed.")

    if not passed:
        print(f"  [pipeline] ⚠️  No candidates passed hard filter for {yml}.")
        print(f"  [pipeline] Submitting top vector matches as fallback.")
        passed = sorted(candidates, key=lambda x: x.get("_dist", 999))[:FINAL_SUBMIT_K * 3]

    # --- Stage 4: Re-rank ---
    ranked = rerank(passed, query)

    # --- Print top 10 for inspection ---
    print(f"\n  [pipeline] Top {min(10, len(ranked))} candidates after re-ranking:")
    for i, c in enumerate(ranked[:10]):
        name   = c.get("name", "Unknown")
        final  = c.get("_final_score", 0)
        vec    = c.get("_vec_score", 0)
        llm    = c.get("_llm_score", 0)
        struct = c.get("_struct_score", 0)
        reason = c.get("_llm_reasoning", "")[:80]
        print(f"    {i+1}. {name:<35} final={final:.3f}  vec={vec:.2f}  struct={struct:.2f}  llm={llm:.2f}")
        if reason:
            print(f"       → {reason}")

    # --- Stage 5: Save results locally ---
    os.makedirs("results", exist_ok=True)
    result_path = f"results/{yml.replace('.yml', '')}_results.json"
    with open(result_path, "w") as f:
        save_data = []
        for c in ranked[:20]:
            save_data.append({
                "_id":            c["_id"],
                "name":           c.get("name", ""),
                "_final_score":   c.get("_final_score", 0),
                "_vec_score":     c.get("_vec_score", 0),
                "_llm_score":     c.get("_llm_score", 0),
                "_struct_score":  c.get("_struct_score", 0),
                "_llm_reasoning": c.get("_llm_reasoning", ""),
            })
        json.dump(save_data, f, indent=2)
    print(f"  [pipeline] Saved results to {result_path}")

    # --- Stage 6: Submit to eval endpoint ---
    if submit_results:
        eval_result = submit(yml, ranked)
        print_eval_details(yml, eval_result)
        return eval_result
    else:
        print(f"  [pipeline] Dry run — skipping submission.")
        return {"skipped": True, "top_ids": [c["_id"] for c in ranked[:10]]}


def main(dry_run: bool = False, only: list[str] = None, no_rewrite: bool = False):
    """
    Run the full pipeline for all 10 configs.

    Args:
        dry_run:    If True, skip submission to eval endpoint
        only:       If set, only run these yml configs
        no_rewrite: If True, skip query rewriting for all configs
    """
    print("Starting search pipeline...")

    all_results = {}
    queries_to_run = QUERIES

    if only:
        queries_to_run = [q for q in QUERIES if q["yml_name"] in only]
        print(f"Running only: {[q['yml_name'] for q in queries_to_run]}")

    for query in queries_to_run:
        try:
            result = run_query(
                query,
                submit_results=not dry_run,
                use_rewriter=not no_rewrite,
            )
            all_results[query["yml_name"]] = result
            time.sleep(1)
        except Exception as e:
            print(f"\n❌ FAILED for {query['yml_name']}: {e}")
            import traceback
            traceback.print_exc()
            all_results[query["yml_name"]] = {"error": str(e)}

    if not dry_run:
        print_summary(all_results)

    os.makedirs("results", exist_ok=True)
    with open("results/all_results.json", "w") as f:
        json.dump(all_results, f, indent=2)
    print("\nAll results saved to results/all_results.json")

    return all_results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mercor Search Pipeline")
    parser.add_argument("--dry-run",    action="store_true", help="Skip eval submission")
    parser.add_argument("--no-rewrite", action="store_true", help="Skip query rewriting for all configs")
    parser.add_argument("--only", nargs="+", metavar="YML",
                        help="Only run specific configs e.g. --only tax_lawyer.yml bankers.yml")
    parser.add_argument("--test-one",   action="store_true", help="Run just tax_lawyer.yml as smoke test")
    args = parser.parse_args()

    if args.test_one:
        result = run_query(QUERIES[0], submit_results=True, use_rewriter=not args.no_rewrite)
        print(json.dumps(result, indent=2, default=str))
    else:
        main(
            dry_run=args.dry_run,
            only=args.only,
            no_rewrite=args.no_rewrite,
        )