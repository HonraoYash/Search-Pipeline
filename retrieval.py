# =============================================================================
# retrieval.py — Embed query with Voyage-3 and fetch candidates from Turbopuffer
# =============================================================================

import turbopuffer
import voyageai
from config import (
    TURBOPUFFER_API_KEY, VOYAGE_API_KEY,
    TPUF_REGION, TPUF_NAMESPACE,
    VOYAGE_MODEL, RETRIEVAL_TOP_K, RETRIEVAL_TOP_K_LARGE
)

# Initialize clients once
tpuf_client = turbopuffer.Turbopuffer(api_key=TURBOPUFFER_API_KEY, region=TPUF_REGION)
voyage_client = voyageai.Client(api_key=VOYAGE_API_KEY)
ns = tpuf_client.namespace(TPUF_NAMESPACE)


def embed_query(text: str) -> list[float]:
    """Embed a query string using Voyage-3 (same model as the index)."""
    response = voyage_client.embed(text, model=VOYAGE_MODEL)
    return response.embeddings[0]


def fetch_candidates(query_text: str, top_k: int = RETRIEVAL_TOP_K) -> list[dict]:
    """
    Embed the query and retrieve top_k candidates from Turbopuffer.
    Returns a list of dicts with all profile attributes + dist score.
    """
    print(f"  [retrieval] Embedding query...")
    vector = embed_query(query_text)

    print(f"  [retrieval] Querying Turbopuffer (top_k={top_k})...")
    result = ns.query(
        rank_by=("vector", "ANN", vector),
        top_k=top_k,
        include_attributes=True,
    )

    candidates = []
    rows = result.rows or []
    for row in rows:
        # Newer turbopuffer SDK returns row attributes as top-level fields on Row
        # (plus "$dist"), while older code expected row.attributes.
        row_data = row.to_dict(exclude_none=True) if hasattr(row, "to_dict") else dict(row)
        row_id = row_data.pop("id", getattr(row, "id", None))
        dist = (
            row_data.pop("$dist", None)
            or row_data.pop("dist", None)
            or getattr(row, "$dist", None)
            or getattr(row, "dist", None)
            or getattr(row, "score", None)
            or 0.0
        )

        doc = {"_id": row_id, "_dist": dist}

        # Backward compatibility if an SDK version returns a nested attributes map.
        maybe_attrs = row_data.pop("attributes", None)
        if isinstance(maybe_attrs, dict):
            doc.update(maybe_attrs)

        # Remove non-attribute fields when present.
        row_data.pop("vector", None)

        # In current SDK, the rest of row_data are profile attributes.
        doc.update(row_data)
        candidates.append(doc)

    print(f"  [retrieval] Retrieved {len(candidates)} candidates.")
    return candidates