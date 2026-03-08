import os
from dotenv import load_dotenv

load_dotenv()

TURBOPUFFER_API_KEY = os.getenv("TURBOPUFFER_API_KEY")
VOYAGE_API_KEY      = os.getenv("VOYAGE_API_KEY")
OPENAI_API_KEY      = os.getenv("OPENAI_API_KEY")
YOUR_EMAIL          = os.getenv("YOUR_EMAIL")

TPUF_REGION            = "aws-us-west-2"
TPUF_NAMESPACE         = "search-test-v4"
VOYAGE_MODEL           = "voyage-3"
OPENAI_MODEL           = "gpt-4o-mini"
RETRIEVAL_TOP_K        = 200
RETRIEVAL_TOP_K_LARGE  = 500
MIN_HARD_PASS          = 10
FINAL_SUBMIT_K         = 10
EVAL_ENDPOINT          = "https://mercor-dev--search-eng-interview.modal.run/evaluate"