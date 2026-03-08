# =============================================================================
# evaluator.py — Submit ranked candidates to the Mercor eval endpoint
# =============================================================================

import json
import requests
from config import EVAL_ENDPOINT, YOUR_EMAIL, FINAL_SUBMIT_K


def submit(yml_name: str, ranked_candidates: list[dict]) -> dict:
    """
    Submit top-K candidates for a given config to the eval endpoint.
    Returns the full API response as a dict.
    """
    object_ids = [c["_id"] for c in ranked_candidates[:FINAL_SUBMIT_K]]

    payload = {
        "config_path": yml_name,
        "object_ids": object_ids,
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": YOUR_EMAIL,
    }

    print(f"  [evaluator] Submitting {len(object_ids)} candidates for '{yml_name}'...")
    print(f"  [evaluator] IDs: {object_ids}")

    try:
        resp = requests.post(EVAL_ENDPOINT, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        result = resp.json()
        avg_score = result.get("average_final_score", "N/A")
        print(f"  [evaluator] ✅ Score for '{yml_name}': {avg_score}")
        return result
    except requests.HTTPError as e:
        print(f"  [evaluator] ❌ HTTP error for '{yml_name}': {e} — {resp.text}")
        return {"error": str(e), "config": yml_name}
    except Exception as e:
        print(f"  [evaluator] ❌ Error for '{yml_name}': {e}")
        return {"error": str(e), "config": yml_name}


def print_summary(all_results: dict):
    """Print a clean summary table of all scores."""
    print("\n" + "=" * 60)
    print("FINAL SCORES SUMMARY")
    print("=" * 60)
    total = 0.0
    count = 0
    for yml_name, result in all_results.items():
        score = result.get("average_final_score", 0)
        hard_scores = result.get("average_hard_scores", [])
        hard_pass_rates = [f"{h['criteria_name']}: {h.get('pass_rate', 0):.0%}" for h in hard_scores]
        hard_str = " | ".join(hard_pass_rates) if hard_pass_rates else "N/A"
        print(f"\n{yml_name}")
        print(f"  Final Score : {score}")
        print(f"  Hard Scores : {hard_str}")
        if isinstance(score, (int, float)):
            total += score
            count += 1
    if count:
        print(f"\nAVERAGE ACROSS ALL CONFIGS: {total / count:.4f}")
    print("=" * 60)