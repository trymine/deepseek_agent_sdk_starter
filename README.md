# DeepSeek + OpenAI Agents SDK Starter

A small Python starter project demonstrating an OpenAI Agents SDK agent using DeepSeek's OpenAI-compatible **Chat Completions** API. The sample agent calls a local order-status tool; replace the demo data with your real ERP/API only after adding authentication and authorization.

## Requirements

- Python 3.11+
- A DeepSeek API key

The DeepSeek API docs currently list `https://api.deepseek.com` as the OpenAI-compatible base URL and `deepseek-flash` as a model name. Check the current DeepSeek model docs if you want to use another model.

## Setup (Windows PowerShell)

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e .
Copy-Item .env.example .env
```

Open `.env` and set `DEEPSEEK_API_KEY` to your own key. Do not commit `.env` or put keys into source code.

## Setup (macOS/Linux)

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
cp .env.example .env
```

Then edit `.env` and set `DEEPSEEK_API_KEY`.

## Run

```bash
python -m deepseek_agent.main
```

Expected demo output (wording can differ):

```text
订单编号：A100；订单状态：已发货；物流单号：SF123456
```

## What's happening

1. `tools.py` defines a Python function and documents its input.
2. The Agents SDK turns the function into a tool schema.
3. `OpenAIChatCompletionsModel` calls DeepSeek using the OpenAI-compatible Chat Completions endpoint.
4. The model can request `get_order_status` with an `order_id` argument.
5. The SDK executes the Python tool and sends its result back to the model.
6. The model generates the final answer.

## Compatibility notes

- This project uses `OpenAIChatCompletionsModel`; don't rely on the default OpenAI Responses API path for DeepSeek's OpenAI-compatible Chat Completions endpoint.
- This minimal example sets `strict_mode=False` on the tool and uses the standard `https://api.deepseek.com` endpoint.
- DeepSeek documents strict function-schema mode as a beta feature using `https://api.deepseek.com/beta`. If you choose strict mode, test the schema against DeepSeek's current supported JSON Schema subset. Agent handoffs use strict schemas, so routing/handoffs may require the beta endpoint or additional compatibility work.
- OpenAI Agents SDK tracing is disabled in this starter because a DeepSeek API key does not authenticate trace uploads to OpenAI. You can later configure a suitable trace processor.
- A compatible API format doesn't guarantee every SDK feature is supported identically. Test tools, structured outputs, handoffs, streaming, and model-specific parameters individually before production.

## Project layout

```text
deepseek-agents-starter/
├── .env.example
├── .gitignore
├── pyproject.toml
├── README.md
└── src/
    └── deepseek_agent/
        ├── __init__.py
        ├── main.py
        └── tools.py
```
