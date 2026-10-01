import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).with_name(".env"))

REQUIRED_ENV_VARS = (
    "MT5_LOGIN",
    "MT5_PASSWORD",
    "MT5_SERVER",
    "MT5_PATH",
    "OPENROUTER_API_KEY",
    "OPENROUTER_BASE_URL",
    "OPENROUTER_MODEL",
)


def _require_environment(environment):
    missing = [name for name in REQUIRED_ENV_VARS if not environment.get(name)]
    if missing:
        names = ", ".join(missing)
        raise RuntimeError(
            f"Missing required environment variables: {names}. "
            "Set them in the local .env file using .env.example as a template."
        )
    return {name: environment[name] for name in REQUIRED_ENV_VARS}


_required = _require_environment(os.environ)

MT5_LOGIN = _required["MT5_LOGIN"]
MT5_PASSWORD = _required["MT5_PASSWORD"]
MT5_SERVER = _required["MT5_SERVER"]
MT5_PATH = _required["MT5_PATH"]
OPENROUTER_API_KEY = _required["OPENROUTER_API_KEY"]
OPENROUTER_BASE_URL = _required["OPENROUTER_BASE_URL"]
OPENROUTER_MODEL = _required["OPENROUTER_MODEL"]

ANTHROPIC_BASE_URL = os.getenv("ANTHROPIC_BASE_URL", "")
ANTHROPIC_AUTH_TOKEN = os.getenv("ANTHROPIC_AUTH_TOKEN", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY") or ANTHROPIC_AUTH_TOKEN
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "")
ANTHROPIC_SMALL_FAST_MODEL = os.getenv("ANTHROPIC_SMALL_FAST_MODEL", "")
