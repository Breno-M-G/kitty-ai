# 🐱 Kitty AI

Assistente pessoal com IA construída do zero em Python, com arquitetura orientada a eventos, suporte a múltiplas plataformas e ferramentas de internet.

## Sobre o projeto

Kitty é uma assistente inteligente com memória persistente entre conversas, capaz de ler e escrever arquivos, executar comandos no terminal, pesquisar e ler páginas da web, e responder tanto no terminal quanto no Discord. Construída com base no projeto [build-your-own-openclaw](https://github.com/czl9707/build-your-own-openclaw).

## Funcionalidades

- 💬 Conversa em português com memória entre sessões (auto-resume)
- 📁 Leitura e escrita de arquivos
- 💻 Execução de comandos no terminal
- 🌐 Pesquisa na web (Tavily) e leitura de páginas (Crawl4AI)
- 🧩 Sistema de skills dinâmicas
- ⚡ Slash commands: `/help`, `/skills`, `/session`, `/compact`, `/context`, `/clear`
- 🗜️ Compactação automática de contexto para conversas longas
- 🔄 Hot reload de configuração (sem precisar reiniciar)
- 🏗️ Arquitetura orientada a eventos (EventBus + Workers)
- 🎮 Integração com Discord (responde quando mencionada)
- 🔌 Compatível com múltiplos provedores de LLM via LiteLLM (Groq, OpenAI, Anthropic, Gemini, etc.)

## Arquitetura

```
CLI / Discord → ChannelWorker → EventBus → AgentWorker → DeliveryWorker → resposta
```

Cada fonte (CLI, Discord) mantém sua própria sessão isolada e persistente. O sistema recupera mensagens pendentes automaticamente em caso de falha.

## Como rodar

1. Clone o repositório:
```bash
git clone https://github.com/Breno-M-G/kitty-ai.git
cd kitty-ai
```

2. Copie o arquivo de configuração:
```bash
cp default_workspace/config.example.yaml default_workspace/config.user.yaml
```

3. Edite o `config.user.yaml` com sua API key e preferências (veja seção Configuração)

4. Rode o bot no terminal:
```bash
uv run my-bot chat
```

5. Ou rode o servidor 24/7 (para usar com Discord):
```bash
uv run my-bot server
```

## Configuração

### LLM (obrigatório)
```yaml
llm:
  provider: openai
  model: groq/llama-3.3-70b-versatile
  api_key: SUA_CHAVE_AQUI
  temperature: 0.7
  max_tokens: 2048
```

### Web Search (opcional)
```yaml
websearch:
  provider: tavily
  api_key: SUA_CHAVE_TAVILY
```

### Web Read (opcional)
```yaml
webread:
  provider: crawl4ai
```

### Discord (opcional)
```yaml
channels:
  enabled: true
  discord:
    enabled: true
    bot_token: SEU_TOKEN_AQUI
    channel_ids: []
    allowed_user_ids: []
```

## Comandos disponíveis no chat

| Comando | Descrição |
|---|---|
| `/help` | Lista todos os comandos disponíveis |
| `/skills` | Lista as skills carregadas |
| `/session` | Mostra detalhes da sessão atual |
| `/compact` | Compacta o histórico manualmente |
| `/context` | Mostra uso de tokens da sessão |
| `/clear` | Limpa a conversa e começa do zero |

## Tecnologias

- Python 3.12
- [uv](https://github.com/astral-sh/uv) — gerenciador de pacotes
- [LiteLLM](https://github.com/BerriAI/litellm) — abstração multi-provider de LLM
- [discord.py](https://github.com/Rapptz/discord.py) — integração com Discord
- [Crawl4AI](https://github.com/unclecode/crawl4ai) — leitura de páginas web
- [Tavily](https://tavily.com) — busca na web
- [Typer](https://typer.tiangolo.com/) + [Rich](https://github.com/Textualize/rich) — CLI
- [Pydantic](https://docs.pydantic.dev/) — validação de configuração
- [Watchdog](https://github.com/gorakhargosh/watchdog) — hot reload de configuração

## Roadmap

Baseado nos próximos steps do tutorial:
- [ ] Multi-agent routing
- [ ] Cron / heartbeat (tarefas agendadas)
- [ ] Multi-layer prompts
- [ ] Memória de longo prazo estruturada
- [ ] HUD desktop/mobile
- [ ] Integração com Obsidian

## Créditos

Baseado no tutorial [build-your-own-openclaw](https://github.com/czl9707/build-your-own-openclaw) por [czl9707](https://github.com/czl9707).
