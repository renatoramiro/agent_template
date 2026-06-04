"""Bot Telegram - entry point."""

import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from agent_base import BaseAgent
from adapters.telegram import TelegramAdapter

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

CONFIG_PATH = Path(__file__).parent / "agent.yaml"


def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN não configurado no .env")
        sys.exit(1)

    agent = BaseAgent(CONFIG_PATH)
    adapter = TelegramAdapter(token, agent)
    adapter.run()


if __name__ == "__main__":
    main()
