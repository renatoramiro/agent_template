"""Base adapter interface."""

from abc import ABC, abstractmethod
from typing import Any


class BaseAdapter(ABC):
    """Interface base para adapters de mensageria."""

    @abstractmethod
    def send_message(self, recipient: str, text: str) -> dict[str, Any]:
        """Envia mensagem para um destinatário."""
        pass

    @abstractmethod
    def process_update(self, data: dict[str, Any]) -> dict[str, Any]:
        """Processa update recebido da plataforma."""
        pass
