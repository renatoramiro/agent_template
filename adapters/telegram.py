"""Adapter Telegram - código original do bot.py refatorado."""

import logging
from typing import Any

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

logger = logging.getLogger(__name__)


class TelegramAdapter:
    """Adapter para Telegram usando python-telegram-bot."""

    def __init__(self, token: str, agent):
        """Inicializa adapter.

        Args:
            token: Telegram Bot Token
            agent: Instância de BaseAgent
        """
        self.token = token
        self.agent = agent
        self._sessions: dict[int, str] = {}
        self.app: Application | None = None

    def _get_session_id(self, user_id: int) -> str:
        """Gera session_id único por usuário."""
        if user_id not in self._sessions:
            self._sessions[user_id] = f"telegram_{user_id}"
        return self._sessions[user_id]

    async def _handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handler para comando /start."""
        user = update.effective_user
        name = self.agent.config.name.replace("-", " ").replace("_", " ").title()

        await update.message.reply_text(
            f"Olá, {user.first_name}! 👋\n"
            f"Sou o **{name}**, {self.agent.config.description}.\n\n"
            "Como posso ajudar?",
            parse_mode="Markdown",
        )

    async def _handle_clear(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handler para comando /clear."""
        user_id = update.effective_user.id
        if user_id in self._sessions:
            del self._sessions[user_id]
        await update.message.reply_text("🗑️ Histórico da conversa limpo!")

    async def _handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handler para mensagens de texto."""
        user_id = update.effective_user.id
        user_text = update.message.text
        session_id = self._get_session_id(user_id)

        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id, action="typing"
        )

        try:
            response = self.agent.process(user_text, session_id)
            await update.message.reply_text(response, parse_mode="Markdown")
        except Exception as e:
            logger.exception("Erro ao processar mensagem")
            await update.message.reply_text(
                f"❌ Ocorreu um erro: {e}\nTente novamente."
            )

    def setup(self) -> Application:
        """Configura aplicação Telegram."""
        self.app = Application.builder().token(self.token).build()

        self.app.add_handler(CommandHandler("start", self._handle_start))
        self.app.add_handler(CommandHandler("clear", self._handle_clear))
        self.app.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_message)
        )

        return self.app

    def run(self) -> None:
        """Inicia polling."""
        if not self.app:
            self.setup()

        logger.info(f"{self.agent.config.name} iniciado via Telegram...")
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)

    def process_update(self, data: dict[str, Any]) -> dict[str, Any]:
        """Processa update (para compatibilidade com interface base)."""
        # Telegram usa polling, não webhooks diretos assim
        raise NotImplementedError("Telegram usa polling, não webhooks HTTP")

    def send_message(self, recipient: str, text: str) -> dict[str, Any]:
        """Envia mensagem para um chat_id."""
        # Implementação síncrona para compatibilidade
        import asyncio

        async def _send():
            if not self.app:
                self.setup()
            await self.app.bot.send_message(
                chat_id=recipient, text=text, parse_mode="Markdown"
            )
            return {"status": "sent"}

        try:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(_send())
        except RuntimeError:
            # Sem event loop rodando
            return asyncio.run(_send())
