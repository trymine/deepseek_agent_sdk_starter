# DeepSeek + OpenAI Agents SDK Starter

A small Python starter project demonstrating an OpenAI Agents SDK agent using DeepSeek's OpenAI-compatible **Chat Completions** API. The sample agent calls a local order-status tool; replace the demo data with your real ERP/API only after adding authentication and authorization.

## Requirements

- Python 3.11+
- A DeepSeek API key

Choose a model available to your DeepSeek account and set `DEEPSEEK_MODEL` explicitly. The basic assistant and the pattern helpers currently have different fallback model names.

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

## Configuration

Run all commands from the repository root after installing the package. Configuration is loaded from `.env`; existing environment variables take precedence.

| Variable | Purpose | Default |
| --- | --- | --- |
| `DEEPSEEK_API_KEY` | Required DeepSeek API key | None |
| `DEEPSEEK_BASE_URL` | OpenAI-compatible API endpoint | `https://api.deepseek.com` |
| `DEEPSEEK_MODEL` | Model used for requests | `deepseek-flash` in the basic assistant; `deepseek-chat` in patterns |
| `MAX_OPTIMIZATION_ROUNDS` | Maximum evaluation rounds for evaluator-optimizer | `3` |

`MAX_OPTIMIZATION_ROUNDS` must be an integer; environment values below `1` are clamped to `1`. Keep API keys only in your local environment or `.env`. Git ignores `.env` and its variants, except the shareable `.env.example`.

## Run the order assistant

```bash
python -m deepseek_agent.main "帮我查询订单 A100 的状态和物流单号。"
```

The query is a required positional argument. Quote it when it contains spaces. Use `python -m deepseek_agent.main --help` for usage.

Expected demo output (wording can differ):

```text
订单编号：A100；订单状态：已发货；物流单号：SF123456
```

## Run patterns

The pattern modules expose asynchronous Python functions, not standalone command-line interfaces. The following one-line commands work in PowerShell and Bash. They make real API requests and may incur charges.

### Routing

The router hands off to order, refund, or general support according to the request:

```bash
python -c "import asyncio; from deepseek_agent.patterns.routing import run_routing; print(asyncio.run(run_routing('Explain what a tracking number is.')))"
```

This returns the final response text. The routing order specialist currently has no order lookup tool attached; use the basic order assistant for the demo order lookup. Refund support likewise cannot execute refunds.

### Evaluator-optimizer

The writer creates a draft, the evaluator scores it, and the optimizer revises it until the evaluator accepts it or the round limit is reached:

```bash
python -c "import asyncio, json; from deepseek_agent.patterns.evaluator_optimizer import run_evaluator_optimizer; print(json.dumps(asyncio.run(run_evaluator_optimizer('Write a concise customer support reply about a delayed delivery.', max_rounds=3)), ensure_ascii=False, indent=2))"
```

The result contains `answer`, `history`, `rounds`, and `final_evaluation`. Omit `max_rounds` to use `MAX_OPTIMIZATION_ROUNDS`. Pass a positive integer when supplying it explicitly. With a limit of N rounds, the flow makes at most 2N pattern-level `Runner.run` calls; actual model requests can be higher if the SDK retries.

## Evaluate a dataset

The repository does not include a default dataset. Create a UTF-8 JSON file such as `datasets/tasks.json`, containing a list of cases:

```json
[
    {
        "id": "refund-definition",
        "input": "Explain what a refund is. Include the word refund.",
        "expected_contains": ["refund"]
    },
    {
        "id": "tracking-definition",
        "input": "Explain what a tracking number is. Include the word tracking.",
        "expected_contains": ["tracking"]
    }
]
```

Every case needs a unique `id` and an `input`. For routing, also supply a nonempty list of strings in `expected_contains`. All listed strings must appear in the answer, ignoring case. Evaluator-optimizer uses `input` and records its own evaluation; it does not check `expected_contains`.

Run either pattern against the file:

```bash
python -m deepseek_agent.patterns.patterns_evaluator --pattern routing --dataset datasets/tasks.json
python -m deepseek_agent.patterns.patterns_evaluator --pattern evaluator-optimizer --dataset datasets/tasks.json
```

Cases run sequentially. The command prints a report summary and writes detailed JSON to `reports/routing.json` or `reports/evaluator_optimizer.json`, relative to the current directory. Running the same pattern again overwrites its report. Use `--help` to see arguments.

Reports contain prompts and generated answers and may include sensitive business information. Reports and datasets are not currently ignored by Git; review them before committing and never put credentials into them.

### Current evaluation limitations

- Routing checks only answer substrings, not which specialist actually handled the request. Missing or empty `expected_contains` currently marks a case as passed without checking the answer.
- Evaluator-optimizer trusts the model's `passed` flag. The `score >= 4` rule is currently expressed only in instructions, not enforced in code.
- Explicit `max_rounds=0` currently falls back to configuration; negative values skip evaluation and return an unevaluated draft. Use positive integers.
- A final evaluation can still be failed when the round limit is reached. The batch command does not turn failed evaluations into a nonzero exit status or an aggregate pass rate.
- Invalid datasets and API errors stop the batch; there is no per-case error recovery. These reports are smoke checks, not a production correctness gate.

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
- Evaluator-optimizer uses Pydantic structured output (`output_type=Evaluation`). Verify that the selected endpoint and model support the SDK's structured-output request format; local import checks do not establish API compatibility.
- A compatible API format doesn't guarantee every SDK feature is supported identically. Test tools, structured outputs, handoffs, streaming, and model-specific parameters individually before production.

## Project layout

```text
deepseek-agents-starter/
|-- .env.example
|-- .gitignore
|-- pyproject.toml
|-- README.md
`-- src/
    `-- deepseek_agent/
        |-- __init__.py
        |-- client.py
        |-- config.py
        |-- main.py
        |-- tools.py
        `-- patterns/
            |-- routing.py
            |-- evaluator_optimizer.py
            `-- patterns_evaluator.py
```
