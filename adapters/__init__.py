"""Adapters para diferentes plataformas de mensageria."""

from .telegram import TelegramAdapter
from .whatsapp import WhatsAppAdapter, WhatsAppConfig

__all__ = ["TelegramAdapter", "WhatsAppAdapter", "WhatsAppConfig"]
