#!/usr/bin/env python3
"""Script para inicializar um novo agente a partir do template.

Usage:
    python setup.py --name meu_agente --display "Meu Agente" --role "assistente"
"""

import argparse
import re
import sys
from pathlib import Path


TEMPLATE_VARS = {
    "AGENT_NAME": "my-agent",
    "AGENT_NAME_DISPLAY": "MyAgent",
    "AGENT_DESCRIPTION": "Agente genérico baseado em agent-base",
    "AGENT_ROLE": "assistente inteligente",
    "CAPABILITIES": "• Consultar informações\n• Executar tarefas",
    "SKILL_DESCRIPTIONS": "- get_status(): status do sistema\n- list_items(): lista itens\n- add_item(name): adiciona item",
    "RESPONSE_RULES": "- Para STATUS: use get_status()\n- Para LISTAR: use list_items()",
    "SKILLS_LIST": '["get_status", "list_items", "add_item"]',
    "SERVICE_NAME": "my-agent-bot",
}


def to_snake(name: str) -> str:
    """Converte para snake_case."""
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower().replace(" ", "_").replace("-", "_")


def to_kebab(name: str) -> str:
    """Converte para kebab-case."""
    return to_snake(name).replace("_", "-")


def to_display(name: str) -> str:
    """Converte para nome display (title case)."""
    return name.replace("_", " ").replace("-", " ").title()


def replace_in_file(filepath: Path, replacements: dict) -> None:
    """Substitui variáveis no arquivo."""
    content = filepath.read_text(encoding="utf-8")
    for old, new in replacements.items():
        content = content.replace(f"{{{{{old}}}}}", new)
    filepath.write_text(content, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Inicializa agente a partir do template")
    parser.add_argument("--name", required=True, help="Nome técnico do agente (snake_case)")
    parser.add_argument("--display", help="Nome amigável (opcional, default: title case)")
    parser.add_argument("--role", default="assistente inteligente", help="Papel do agente")
    args = parser.parse_args()

    agent_name = to_kebab(args.name)
    agent_name_snake = to_snake(args.name)
    agent_display = args.display or to_display(args.name)
    agent_role = args.role

    replacements = {
        "AGENT_NAME": agent_name,
        "AGENT_NAME_DISPLAY": agent_display,
        "AGENT_DESCRIPTION": f"Agente {agent_display} - {agent_role}",
        "AGENT_ROLE": agent_role,
        "CAPABILITIES": "• Consultar informações\n• Executar tarefas",
        "SKILL_DESCRIPTIONS": "- get_status(): status do sistema\n- list_items(): lista itens\n- add_item(name): adiciona item",
        "RESPONSE_RULES": "- Para STATUS: use get_status()\n- Para LISTAR: use list_items()",
        "SKILLS_LIST": '["get_status", "list_items", "add_item"]',
        "SERVICE_NAME": f"{agent_name_snake}-bot",
    }

    # Aplicar substituições
    template_dir = Path(__file__).parent
    files_to_process = [
        template_dir / "agent.yaml",
        template_dir / "bot_telegram.py",
        template_dir / "bot_whatsapp.py",
        template_dir / "docker-compose.yml",
        template_dir / "skills" / "__init__.py",
        template_dir / "skills" / "example_skill.py",
        template_dir / "README.md",
    ]

    for filepath in files_to_process:
        if filepath.exists():
            replace_in_file(filepath, replacements)
            print(f"✓ {filepath.name}")

    print(f"\n🎉 Agente '{agent_display}' inicializado!")
    print("\nPróximos passos:")
    print("1. cp .env.example .env")
    print("2. Edite .env com suas chaves (Telegram ou WhatsApp)")
    print("3. Customize as skills em skills/")
    print("4. Execute:")
    print("   Telegram:  python bot_telegram.py")
    print("   WhatsApp:  python bot_whatsapp.py --port 8000")


if __name__ == "__main__":
    main()
