# =============================================================================
# query_rewriter.py — Rewrite job descriptions into optimal search queries
# =============================================================================
# Before embedding, we ask GPT-4o to rewrite the job description into the
# most semantically rich, searchable form. This improves vector retrieval
# because the rewritten query better matches how candidates describe themselves
# in their rerankSummary profiles.
# =============================================================================

from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL

openai_client = OpenAI(api_key=OPENAI_API_KEY)


REWRITE_SYSTEM_PROMPT = """You are an expert recruiter and search engineer. 
Your job is to rewrite a job description into an ideal search query that will 
retrieve the best matching candidate profiles from a vector database.

The candidate profiles are LinkedIn-style summaries describing:
- Their education (degrees, schools, fields of study)
- Their work experience (job titles, companies, years)
- Their skills and expertise

Your rewritten query should:
1. Use the same language and terminology that candidates use to describe themselves
2. Include specific degree names, job titles, skills, and domain terms
3. Be dense with relevant keywords — not a sentence, but a rich keyword-heavy paragraph
4. Include synonyms and related terms (e.g. "JD / Juris Doctor / law degree / attorney / lawyer")
5. Mention specific tools, certifications, methodologies relevant to the role
6. Be 100-200 words — comprehensive but focused

Return ONLY the rewritten query text. No explanation, no preamble."""


def rewrite_query(query: dict) -> str:
    """
    Use GPT-4o to rewrite a query into optimal vector search form.
    Returns the rewritten query string.
    """
    nl = query["nl_description"]
    hard = "\n".join(f"- {c['description']}" for c in query["hard_criteria"])
    soft = "\n".join(f"- {s}" for s in query["soft_criteria"])

    user_prompt = f"""Rewrite this job description into an ideal vector search query 
to find the best matching candidate profiles.

ORIGINAL JOB DESCRIPTION:
{nl}

MUST-HAVE REQUIREMENTS:
{hard}

NICE-TO-HAVE REQUIREMENTS:
{soft}

Rewrite this into a rich, keyword-dense search query (100-200 words) using 
terminology that candidates would use in their own LinkedIn profiles and resumes."""

    try:
        response = openai_client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": REWRITE_SYSTEM_PROMPT},
                {"role": "user",   "content": user_prompt},
            ],
            temperature=0.2,
            max_tokens=400,
        )
        rewritten = response.choices[0].message.content.strip()
        print(f"  [query_rewriter] Rewritten query ({len(rewritten.split())} words):")
        print(f"  {rewritten[:200]}...")
        return rewritten
    except Exception as e:
        print(f"  [query_rewriter] Failed to rewrite query: {e}. Using original.")
        return nl