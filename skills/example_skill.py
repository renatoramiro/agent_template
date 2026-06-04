"""Exemplo de skill - customize conforme suas necessidades.

Este arquivo demonstra o padrão para criar skills:
1. Importe o decorador `skill` do agent_base
2. Use o decorador @skill() com name e description
3. Implemente a função retornando uma string
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from agent_base.skills import skill

# Caminho do banco de dados (ajuste conforme necessário)
DB_PATH = Path("./data/{{AGENT_NAME}}.db")


def _init_db():
    """Inicializa o banco de dados com tabela de exemplo."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(str(DB_PATH)) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


@skill(
    name="get_status",
    description="Retorna o status geral do sistema. Use quando perguntarem como está tudo ou pedirem um resumo.",
)
def get_status() -> str:
    """Retorna status do sistema."""
    return f"✅ Sistema operando normalmente. Data: {datetime.now().strftime('%Y-%m-%d %H:%M')}"


@skill(
    name="list_items",
    description="Lista todos os itens cadastrados. Use quando pedirem para ver itens ou listar registros.",
)
def list_items() -> str:
    """Lista todos os itens."""
    _init_db()
    with sqlite3.connect(str(DB_PATH)) as conn:
        rows = conn.execute("SELECT name, created_at FROM items ORDER BY created_at DESC").fetchall()

    if not rows:
        return "📭 Nenhum item cadastrado."

    lines = ["📋 ITENS CADASTRADOS:"]
    for name, created_at in rows:
        lines.append(f"  • {name} (criado em: {created_at})")
    lines.append(f"\n📊 Total: {len(rows)} itens")
    return "\n".join(lines)


@skill(
    name="add_item",
    description="Adiciona um novo item ao sistema. Parâmetro: name (nome do item).",
)
def add_item(name: str) -> str:
    """Adiciona um item."""
    _init_db()
    with sqlite3.connect(str(DB_PATH)) as conn:
        conn.execute("INSERT INTO items (name) VALUES (?)", (name,))
        conn.commit()
    return f"✅ Item '{name}' adicionado com sucesso!"


# ==============================================================================
# DADOS DE EXEMPLO/DEMO
# ==============================================================================

def popular_demo():
    """Popula banco com dados de demonstração."""
    _init_db()

    demo_items = [
        "Item de exemplo 1",
        "Item de exemplo 2",
        "Item de exemplo 3",
    ]

    with sqlite3.connect(str(DB_PATH)) as conn:
        for item in demo_items:
            conn.execute("INSERT OR IGNORE INTO items (name) VALUES (?)", (item,))
        conn.commit()
    print(f"✅ {len(demo_items)} itens de demo adicionados!")


if __name__ == "__main__":
    popular_demo()
