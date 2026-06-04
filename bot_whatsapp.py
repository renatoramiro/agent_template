"""Bot WhatsApp - entry point com FastAPI.

Usage:
    python bot_whatsapp.py
    python bot_whatsapp.py --port 8000
    python bot_whatsapp.py --setup-webhook --webhook-url https://meubot.com/webhook
"""

import argparse
import logging
import os
import sys
from pathlib import Path

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from agent_base import BaseAgent
from adapters.whatsapp import WhatsAppAdapter, WhatsAppConfig

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

CONFIG_PATH = Path(__file__).parent / "agent.yaml"


def create_app(agent: BaseAgent, adapter: WhatsAppAdapter) -> FastAPI:
    """Cria aplicação FastAPI."""
    app = FastAPI(title=f"{agent.config.name} - WhatsApp")

    @app.get("/")
    async def health():
        return {"status": "ok", "agent": agent.config.name}

    @app.get("/status")
    async def status():
        try:
            return {"status": "ok", "whatsapp": adapter.get_status()}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post(adapter.config.webhook_path)
    async def webhook(request: Request):
        try:
            data = await request.json()
            result = adapter.process_update(data)
            return JSONResponse(content=result)
        except Exception as e:
            logger.exception("Erro no webhook")
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/send")
    async def send(request: Request):
        try:
            data = await request.json()
            number = data.get("number")
            text = data.get("text")
            if not number or not text:
                raise HTTPException(status_code=400, detail="number e text obrigatórios")
            result = adapter.send_message(number, text)
            return {"status": "sent", "result": result}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return app


def main():
    parser = argparse.ArgumentParser(description="Bot WhatsApp")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--setup-webhook", action="store_true")
    parser.add_argument("--webhook-url")
    args = parser.parse_args()

    # Verifica configuração Evolution
    base_url = os.getenv("EVOLUTION_BASE_URL")
    instance = os.getenv("EVOLUTION_INSTANCE")
    api_key = os.getenv("EVOLUTION_API_KEY")

    if not all([base_url, instance, api_key]):
        logger.error(
            "Configure EVOLUTION_BASE_URL, EVOLUTION_INSTANCE e EVOLUTION_API_KEY"
        )
        sys.exit(1)

    agent = BaseAgent(CONFIG_PATH)
    config = WhatsAppConfig(
        base_url=base_url,
        instance=instance,
        api_key=api_key,
        webhook_path=os.getenv("EVOLUTION_WEBHOOK_PATH", "/webhook/whatsapp"),
    )
    adapter = WhatsAppAdapter(config, agent)

    # Configura webhook e sai
    if args.setup_webhook:
        if not args.webhook_url:
            logger.error("--webhook-url obrigatório com --setup-webhook")
            sys.exit(1)
        try:
            result = adapter.setup_webhook(args.webhook_url)
            logger.info(f"Webhook configurado: {result}")
            print("✅ Webhook configurado!")
        except Exception as e:
            logger.error(f"Erro: {e}")
            sys.exit(1)
        return

    # Inicia servidor
    app = create_app(agent, adapter)
    logger.info(f"Iniciando {agent.config.name} no WhatsApp...")
    logger.info(f"Servidor: http://{args.host}:{args.port}")
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
