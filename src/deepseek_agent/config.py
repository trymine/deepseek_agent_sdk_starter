import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    api_key: str
    base_url: str
    model: str
    max_optimization_rounds: int

def get_settings() -> Settings:
    key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    if not key:
        raise RuntimeError(
            "Missing DEEPSEEK_API_KEY. Copy .env.example to .env "
            "and configure your API key."
        )
    return Settings(
        api_key=key,
        base_url=os.getenv(
            "DEEPSEEK_BASE_URL", "https://api.deepseek.com"
        ),
        model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
        max_optimization_rounds=max(
            1, int(os.getenv("MAX_OPTIMIZATION_ROUNDS", "3"))
        ),
    )