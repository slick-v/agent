from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore"   #ignore unknown keys in .env
    )

    # --- Required (no default = must be in .env) ---
    groq_api_key: SecretStr
    model_name: str
    tavily_api_key: SecretStr

    # --- Agent behavior (optional, defaults here) ---
    max_steps: int = 10
    temperature: float = 0.2
    tool_timeout: int = 20       # seconds

    # --- Paths ---
    data_dir: Path = BASE_DIR / "data"
    log_dir: Path = BASE_DIR / "logs"
    output_dir: Path = BASE_DIR / "outputs"

    @property
    def db_path(self) -> Path:
        return self.data_dir / "agent.db"

    def make_dirs(self) -> None:
        for folder in (self.data_dir, self.log_dir, self.output_dir):
            folder.mkdir(exist_ok=True)


settings = Settings()
settings.make_dirs()