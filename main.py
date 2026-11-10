"""Entry point. A terminal chat for now; becomes the FastAPI app later."""
import logging

from config import settings
from loop import run_agent

logging.basicConfig(
    filename=settings.log_dir / "agent.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    encoding="utf-8",
)
# Keep the HTTP library from flooding the log with every request
logging.getLogger("httpx").setLevel(logging.WARNING)


def main() -> None:
    print("Agent ready. Type 'exit' to quit.")
    while True:
        question = input("\nYou: ").strip()
        if not question:
            continue
        if question.lower() in {"exit", "quit"}:
            break
        try:
            print("\nAgent:", run_agent(question))
        except Exception as e:
            logging.exception("Run failed")
            print("\nError:", e)


if __name__ == "__main__":
    main()