"""Adapter WhatsApp via Evolution API."""

import logging
from dataclasses import dataclass
from typing import Any

import httpx

logger = logging.getLogger(__name__)


@dataclass
class WhatsAppConfig:
    """Configuração para Evolution API."""

    base_url: str
    instance: str
    api_key: str
    webhook_path: str = "/webhook/whatsapp"


class WhatsAppClient:
    """Cliente HTTP para Evolution API."""

    def __init__(self, config: WhatsAppConfig):
        self.config = config
        self._client = httpx.Client(timeout=30.0)

    def _headers(self) -> dict[str, str]:
        return {
            "Content-Type": "application/json",
            "apikey": self.config.api_key,
        }

    def send_text(
        self,
        number: str,
        text: str,
        delay: int = 0,
        link_preview: bool = True,
    ) -> dict[str, Any]:
        """Envia mensagem de texto."""
        url = f"{self.config.base_url}/message/sendText/{self.config.instance}"

        payload = {
            "number": number,
            "text": text,
            "delay": delay,
            "linkPreview": link_preview,
        }

        try:
            response = self._client.post(url, headers=self._headers(), json=payload)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error: {e}")
            raise

    def set_webhook(
        self, webhook_url: str, events: list[str] | None = None
    ) -> dict[str, Any]:
        """Configura webhook."""
        url = f"{self.config.base_url}/webhook/set/{self.config.instance}"

        if events is None:
            events = ["MESSAGES_UPSERT", "CONNECTION_UPDATE"]

        payload = {
            "url": webhook_url,
            "webhook_by_events": False,
            "webhook_base64": False,
            "events": events,
        }

        try:
            response = self._client.post(url, headers=self._headers(), json=payload)
            response.raise_for_status()
            logger.info(f"Webhook configurado: {webhook_url}")
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error: {e}")
            raise

    def get_status(self) -> dict[str, Any]:
        """Status da instância."""
        url = f"{self.config.base_url}/instance/connectionState/{self.config.instance}"
        response = self._client.get(url, headers=self._headers())
        response.raise_for_status()
        return response.json()

    def close(self) -> None:
        self._client.close()


class WhatsAppAdapter:
    """Adapter WhatsApp com integração ao BaseAgent."""

    def __init__(self, config: WhatsAppConfig, agent):
        self.config = config
        self.client = WhatsAppClient(config)
        self.agent = agent
        self._session_prefix = f"whatsapp_{config.instance}"

    def process_update(self, data: dict[str, Any]) -> dict[str, Any]:
        """Processa webhook da Evolution API."""
        event = data.get("event")
        payload = data.get("data", {})

        if event == "MESSAGES_UPSERT":
            return self._handle_message(payload)
        elif event == "CONNECTION_UPDATE":
            return self._handle_connection(payload)
        return {"status": "ignored", "event": event}

    def _handle_message(self, data: dict[str, Any]) -> dict[str, Any]:
        """Processa mensagem recebida."""
        key = data.get("key", {})

        # Ignora mensagens enviadas pelo bot
        if key.get("fromMe"):
            return {"status": "ignored", "reason": "from_me"}

        remote_jid = key.get("remoteJid", "")
        sender = remote_jid.split("@")[0] if "@" in remote_jid else ""

        message = data.get("message", {})
        text = message.get("conversation", "") or message.get("extendedTextMessage", {}).get("text", "")

        if not text:
            return {"status": "ignored", "reason": "no_text"}

        logger.info(f"Mensagem de {sender}: {text[:50]}...")

        # Processa com agente
        session_id = f"{self._session_prefix}_{sender}"
        try:
            response = self.agent.process(text, session_id)
            self.send_message(sender, response)
            return {"status": "processed", "sender": sender}
        except Exception as e:
            logger.exception("Erro processando mensagem")
            return {"status": "error", "error": str(e)}

    def _handle_connection(self, data: dict[str, Any]) -> dict[str, Any]:
        """Processa atualização de conexão."""
        state = data.get("state")
        logger.info(f"Conexão WhatsApp: {state}")
        return {"status": "connection", "state": state}

    def send_message(self, number: str, text: str) -> dict[str, Any]:
        """Envia mensagem."""
        clean_number = "".join(c for c in number if c.isdigit())
        return self.client.send_text(clean_number, text)

    def setup_webhook(self, base_url: str) -> dict[str, Any]:
        """Configura webhook."""
        webhook_url = f"{base_url.rstrip('/')}{self.config.webhook_path}"
        return self.client.set_webhook(webhook_url)

    def get_status(self) -> dict[str, Any]:
        """Status da conexão."""
        return self.client.get_status()

    def close(self) -> None:
        self.client.close()
