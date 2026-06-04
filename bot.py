"""Telegram Bot adapter para o {{AGENT_NAME_DISPLAY}}."""

import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from agent_base import BaseAgent

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

CONFIG_PATH = Path(__file__).parent / "agent.yaml"

agent = BaseAgent(CONFIG_PATH)

# Sessão por usuário (user_id do Telegram)
_sessions: dict[int, str] = {}


def _get_session_id(user_id: int) -> str:
    if user_id not in _sessions:
        _sessions[user_id] = f"telegram_{user_id}"
    return _sessions[user_id]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /start."""
    user = update.effective_user
    await update.message.reply_text(
        f"Olá, {user.first_name}! 👋\n"
        "Sou o **{{AGENT_NAME_DISPLAY}}**, {{AGENT_ROLE}}.\n\n"
        "Posso te ajudar com:\n"
        "{{CAPABILITIES}}\n"
        "Como posso ajudar?",
        parse_mode="Markdown",
    )


async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Comando /clear - limpa histórico da sessão."""
    user_id = update.effective_user.id
    if user_id in _sessions:
        del _sessions[user_id]
    await update.message.reply_text("🗑️ Histórico da conversa limpo!")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Processa mensagens de texto."""
    user_id = update.effective_user.id
    user_text = update.message.text
    session_id = _get_session_id(user_id)

    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action="typing"
    )

    try:
        response = agent.process(user_text, session_id)
        await update.message.reply_text(response, parse_mode="Markdown")
    except Exception as e:
        logger.exception("Erro ao processar mensagem")
        await update.message.reply_text(
            f"❌ Ocorreu um erro: {e}\nTente novamente."
        )


def main() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN não configurado no .env")

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("{{AGENT_NAME_DISPLAY}} iniciado via Telegram...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
