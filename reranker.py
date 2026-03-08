# =============================================================================
# reranker.py — Multi-signal re-ranking using structured features + GPT-4o
# =============================================================================

import json
import math
from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL

openai_client = OpenAI(api_key=OPENAI_API_KEY)

# How many candidates to send to GPT-4o (top N after vector score sort)
LLM_RERANK_TOP_N = 40


# ---------------------------------------------------------------------------
# Signal 1: Normalize vector distance → similarity score [0, 1]
# ---------------------------------------------------------------------------

def normalize_dist_scores(candidates: list[dict]) -> list[dict]:
    """
    Turbopuffer returns euclidean-like dist (lower = better).
    Convert to a similarity score: sim = 1 / (1 + dist)
    Then normalize to [0, 1] across the candidate set.
    """
    if not candidates:
        return candidates

    sims = [1.0 / (1.0 + c.get("_dist", 1.0)) for c in candidates]
    min_s, max_s = min(sims), max(sims)
    rng = max_s - min_s if max_s > min_s else 1.0

    for c, s in zip(candidates, sims):
        c["_vec_score"] = (s - min_s) / rng
    return candidates


# ---------------------------------------------------------------------------
# Signal 2: Structured feature bonus score
# ---------------------------------------------------------------------------

def structured_score(candidate: dict, query: dict) -> float:
    """
    Rule-based scoring on structured fields.
    Returns a score in [0, 1].
    """
    score = 0.0
    max_score = 0.0
    nl = query["nl_description"].lower()

    # --- Experience years bonus ---
    max_score += 1.0
    exp_bucket_map = {"0": 0.5, "1": 1.5, "3": 3.5, "5": 5.5, "10": 10.5}
    raw_years = candidate.get("exp_years") or []
    if isinstance(raw_years, str):
        raw_years = [raw_years]
    total_exp = sum(float(exp_bucket_map.get(str(b).strip(), 0)) for b in raw_years)
    if total_exp >= 10:
        score += 1.0
    elif total_exp >= 5:
        score += 0.8
    elif total_exp >= 3:
        score += 0.6
    elif total_exp >= 1:
        score += 0.3

    # --- Degree relevance bonus ---
    max_score += 1.0
    degrees = [d.lower() for d in (candidate.get("deg_degrees") or [])]
    if any(d in ["doctorate", "phd", "ph.d"] for d in degrees):
        score += 1.0
    elif any(d in ["md", "jd", "mba", "llm"] for d in degrees):
        score += 0.9
    elif any(d in ["master's", "masters"] for d in degrees):
        score += 0.6
    elif any(d in ["bachelor's", "bachelors"] for d in degrees):
        score += 0.3

    # --- Field of study match ---
    max_score += 1.0
    fos_list = [f.lower() for f in (candidate.get("deg_fos") or [])]
    fos_combined = " ".join(fos_list)
    # Extract relevant keywords from NL description
    fos_keywords = []
    for token in nl.split():
        if len(token) > 5:
            fos_keywords.append(token.strip(".,()"))
    for kw in fos_keywords:
        if kw in fos_combined:
            score += 1.0
            break

    # --- School prestige hint (has a school listed at all) ---
    max_score += 0.5
    schools = candidate.get("deg_schools") or []
    if schools:
        score += 0.3
        # bonus if school name appears in top university list
        school_str = " ".join(s.lower() for s in schools)
        top_keywords = ["harvard", "stanford", "mit", "yale", "princeton",
                        "columbia", "wharton", "booth", "kellogg", "sloan",
                        "oxford", "cambridge", "lse", "chicago", "berkeley"]
        if any(k in school_str for k in top_keywords):
            score += 0.2

    # --- Title relevance ---
    max_score += 1.0
    titles = [t.lower() for t in (candidate.get("exp_titles") or [])]
    titles_combined = " ".join(titles)
    title_keywords = []
    for token in nl.split():
        t = token.strip(".,()").lower()
        if len(t) > 4:
            title_keywords.append(t)
    for kw in title_keywords:
        if kw in titles_combined:
            score += 1.0
            break

    return score / max_score if max_score > 0 else 0.0


# ---------------------------------------------------------------------------
# Signal 3: GPT-4o LLM judge
# ---------------------------------------------------------------------------

def build_llm_prompt(query: dict, candidates: list[dict]) -> str:
    soft_criteria_str = "\n".join(f"  - {s}" for s in query["soft_criteria"])
    nl = query["nl_description"]

    candidate_blocks = []
    for i, c in enumerate(candidates):
        summary = c.get("rerankSummary") or c.get("rerank_summary") or "No summary available."
        # Truncate very long summaries
        if len(summary) > 800:
            summary = summary[:800] + "..."
        candidate_blocks.append(
            f"[{i}] ID={c['_id']}\nSummary: {summary}"
        )

    candidates_str = "\n\n".join(candidate_blocks)

    return f"""You are an expert talent evaluator. Your job is to score candidates for a job role.

ROLE DESCRIPTION:
{nl}

SOFT CRITERIA (nice-to-haves, each scored 1-5):
{soft_criteria_str}

CANDIDATES:
{candidates_str}

TASK:
For each candidate, output a JSON array where each element has:
- "idx": the candidate index (integer, 0-based)
- "total_soft_score": a float from 0.0 to 5.0 representing how well this candidate matches ALL soft criteria combined
- "reasoning": one sentence explaining the score

Return ONLY a valid JSON array. No markdown, no explanation outside the JSON.
Example: [{{"idx": 0, "total_soft_score": 4.2, "reasoning": "Strong match on all three criteria."}}, ...]"""


def llm_rerank(candidates: list[dict], query: dict) -> list[dict]:
    """
    Use GPT-4o to score top candidates on soft criteria.
    Adds _llm_score to each candidate.
    """
    if not candidates:
        return candidates

    # Only send top N to LLM (sorted by vector score first)
    to_score = sorted(candidates, key=lambda x: x.get("_vec_score", 0), reverse=True)
    top_for_llm = to_score[:LLM_RERANK_TOP_N]
    rest = to_score[LLM_RERANK_TOP_N:]

    print(f"  [reranker] Sending {len(top_for_llm)} candidates to GPT-4o for soft scoring...")

    prompt = build_llm_prompt(query, top_for_llm)

    try:
        response = openai_client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
            max_tokens=2000,
        )
        raw = response.choices[0].message.content.strip()

        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        scores = json.loads(raw)
        score_map = {item["idx"]: item["total_soft_score"] for item in scores}

        for i, c in enumerate(top_for_llm):
            c["_llm_score"] = score_map.get(i, 0.0) / 5.0  # normalize to [0,1]
            c["_llm_reasoning"] = next(
                (item.get("reasoning", "") for item in scores if item["idx"] == i), ""
            )

    except Exception as e:
        print(f"  [reranker] LLM scoring failed: {e}. Using 0 for all.")
        for c in top_for_llm:
            c["_llm_score"] = 0.0

    # Assign low score to rest
    for c in rest:
        c["_llm_score"] = 0.0

    return top_for_llm + rest


# ---------------------------------------------------------------------------
# Final ensemble scoring + ranking
# ---------------------------------------------------------------------------

# Weights for the three signals
W_VEC        = 0.20   # Vector similarity (semantic match)
W_STRUCTURED = 0.15   # Structured feature score
W_LLM        = 0.65   # LLM soft scoring (most trusted)


def ensemble_score(candidate: dict) -> float:
    vec = candidate.get("_vec_score", 0.0)
    struct = candidate.get("_struct_score", 0.0)
    llm = candidate.get("_llm_score", 0.0)
    return W_VEC * vec + W_STRUCTURED * struct + W_LLM * llm


def rerank(candidates: list[dict], query: dict) -> list[dict]:
    """
    Full re-ranking pipeline:
    1. Normalize vector distances
    2. Compute structured scores
    3. LLM soft scoring
    4. Ensemble → final ranked list
    """
    if not candidates:
        return candidates

    # Signal 1
    candidates = normalize_dist_scores(candidates)

    # Signal 2
    for c in candidates:
        c["_struct_score"] = structured_score(c, query)

    # Signal 3
    candidates = llm_rerank(candidates, query)

    # Ensemble
    for c in candidates:
        c["_final_score"] = ensemble_score(c)

    # Sort by final score descending
    ranked = sorted(candidates, key=lambda x: x["_final_score"], reverse=True)
    return ranked