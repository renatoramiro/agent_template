# 🤖 {{AGENT_NAME_DISPLAY}} - Template de Agente

Template genérico para criar agentes com `agent-base` + **Telegram** ou **WhatsApp**.

## 📁 Estrutura

```
.
├── agent.yaml              # Configuração principal do agente
├── bot_telegram.py         # Bot Telegram (polling)
├── bot_whatsapp.py         # Bot WhatsApp (webhook server)
├── adapters/               # Adapters de plataforma
│   ├── telegram.py
│   └── whatsapp.py
├── requirements.txt        # Dependências Python
├── .env.example            # Template de variáveis de ambiente
├── Dockerfile              # Container Docker
├── docker-compose.yml      # Orquestração Docker
├── skills/
│   ├── __init__.py
│   └── example_skill.py    # Exemplo de skill (modele aqui)
└── README.md               # Este arquivo
```

## 🚀 Como usar este template

### 1. Copie o template

```bash
cp -r agent_template meu_agente
cd meu_agente
```

### 2. Substitua as variáveis de template

Edite os arquivos marcados com `{{...}}`:

| Variável | Descrição | Arquivos |
|----------|-----------|----------|
| `{{AGENT_NAME}}` | Nome técnico (snake_case) | `agent.yaml`, `bot.py`, `docker-compose.yml` |
| `{{AGENT_NAME_DISPLAY}}` | Nome amigável | `agent.yaml`, `bot.py` |
| `{{AGENT_DESCRIPTION}}` | Descrição do agente | `agent.yaml` |
| `{{AGENT_ROLE}}` | Papel do agente | `agent.yaml`, `bot.py` |
| `{{CAPABILITIES}}` | Lista de capacidades | `bot.py` |
| `{{SKILL_DESCRIPTIONS}}` | Descrição das skills | `agent.yaml` |
| `{{RESPONSE_RULES}}` | Regras de resposta | `agent.yaml` |
| `{{SKILLS_LIST}}` | Lista de skills habilitadas | `agent.yaml` |
| `{{SERVICE_NAME}}` | Nome do serviço no docker-compose | `docker-compose.yml` |

### 3. Configure o ambiente

```bash
cp .env.example .env
# Edite .env com suas chaves
```

### 4. Crie suas skills

Edite `skills/example_skill.py` ou crie novos arquivos em `skills/`:

```python
from agent_base.skills import skill

@skill(
    name="minha_skill",
    description="O que esta skill faz",
)
def minha_skill(parametro: str) -> str:
    """Implementação da skill."""
    return f"Resultado: {parametro}"
```

### 5. Atualize `agent.yaml`

- Liste suas skills em `skills.enabled`
- Descreva-as no `system_prompt`
- Ajuste `provider.model` se necessário

### 6. Execute

Escolha a plataforma:

#### 🚀 Telegram (mais simples)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python bot_telegram.py
```

#### 📱 WhatsApp (requer Evolution API)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 1. Configure o webhook (apenas uma vez)
python bot_whatsapp.py --setup-webhook --webhook-url https://seubot.com/webhook/whatsapp

# 2. Inicie o servidor
python bot_whatsapp.py --port 8000
```

**Docker:**
```bash
docker-compose up -d
```

## 📝 Exemplo: Criando um agente de suporte

### 1. Copiar template
```bash
cp -r agent_template agent_suporte_ti
cd agent_suporte_ti
```

### 2. Editar `agent.yaml`
```yaml
name: "suporte-ti"
description: "Agente de suporte técnico de TI"

system_prompt: |
  Você é o TechBot, assistente de suporte técnico.
  ...

skills:
  enabled: ["listar_chamados", "abrir_chamado", "consultar_kb"]
```

### 3. Criar skills em `skills/suporte.py`
```python
@skill(name="listar_chamados", description="Lista chamados em aberto")
def listar_chamados() -> str:
    # Implementação...
    pass
```

### 4. Configurar e rodar

**Telegram:**
```bash
cp .env.example .env
# editar .env (TELEGRAM_BOT_TOKEN)
python bot_telegram.py
```

**WhatsApp:**
```bash
cp .env.example .env
# editar .env (EVOLUTION_*)
python bot_whatsapp.py --setup-webhook --webhook-url https://seubot.com/webhook/whatsapp
python bot_whatsapp.py --port 8000
```

## � Comparação: Telegram vs WhatsApp

| Feature | Telegram | WhatsApp |
|---------|----------|----------|
| Setup | Muito simples | Requer Evolution API |
| Hosting | Local/Cloud | Precisa de servidor web |
| Webhook | Não (polling) | Sim |
| Portas | Nenhuma | 8000+ |
| Sessões | por `user_id` | por `número de telefone` |

## �🔧 Personalização avançada

### Mudar o provider LLM

Edite `agent.yaml`:
```yaml
provider:
  type: "ollama"  # ou "groq"
  model: "llama3.2:1b"
```

### Adicionar mais memória

```yaml
memory:
  short_term:
    max_messages: 50  # Aumentar contexto
  long_term:
    enabled: true
    db_path: "./memory.db"
```

### Múltiplas skills

Crie vários arquivos em `skills/`:
```
skills/
├── __init__.py
├── chamados.py      # Skills de chamados
├── inventario.py    # Skills de inventário
└── relatorios.py    # Skills de relatórios
```

## 📚 Referência

- **agent-base**: https://github.com/renatoramiro/agent-base
- **Evolution API**: https://doc.evolution-api.com/
- **python-telegram-bot**: https://docs.python-telegram-bot.org/
- **Groq API**: https://console.groq.com/docs

---

Template criado a partir de `agent_supermarket_inventory`.
