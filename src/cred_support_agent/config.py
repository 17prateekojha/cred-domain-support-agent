from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge_base"
LOG_DIR = BASE_DIR / "logs"
EVALUATION_DIR = BASE_DIR / "evaluations"
TRANSCRIPTS_DIR = BASE_DIR / "transcripts"

MOCK_LLM_MODE = True
DEFAULT_MAX_REQUEST_TOKENS = 8000
DEFAULT_MAX_QUERY_CHARS = 2000


def ensure_directories() -> None:
    for path in (DATA_DIR, KNOWLEDGE_BASE_DIR, LOG_DIR, EVALUATION_DIR, TRANSCRIPTS_DIR):
        path.mkdir(parents=True, exist_ok=True)
