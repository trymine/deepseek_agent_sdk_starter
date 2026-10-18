from __future__ import annotations

import argparse
import asyncio
import os

from dotenv import load_dotenv
from agents import (
    Agent,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    Runner,
    set_tracing_disabled,
)

from .tools import get_order_status


def build_agent() -> Agent:
    """Configure the Agents SDK to use DeepSeek's OpenAI-compatible Chat API."""
    load_dotenv()

    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key or api_key == "replace_with_your_deepseek_api_key":
        raise RuntimeError(
            "DEEPSEEK_API_KEY is missing. Copy .env.example to .env and set your key."
        )

    model_name = os.getenv("DEEPSEEK_MODEL", "deepseek-flash")
    base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

    # DeepSeek key cannot authenticate OpenAI-hosted trace uploads.
    # Disable the SDK's OpenAI trace export unless you configure a trace processor.
    set_tracing_disabled(disabled=True)

    deepseek_client = AsyncOpenAI(
        api_key=api_key,
        base_url=base_url,
    )
    model = OpenAIChatCompletionsModel(
        model=model_name,
        openai_client=deepseek_client,
    )

    return Agent(
        name="Order Assistant",
        instructions=(
            "你是企业订单查询助手。使用中文回答。"
            "当用户询问订单状态或物流单号时，调用 get_order_status 工具。"
            "只能依据工具返回的结果回答；如果订单不存在，明确告知用户。"
        ),
        model=model,
        tools=[get_order_status],
    )


async def main() -> None:
    parser = argparse.ArgumentParser(description="DeepSeek order assistant")
    parser.add_argument("query", help="Query to send to the agent")
    args = parser.parse_args()

    agent = build_agent()
    result = await Runner.run(
        agent,
        args.query,
    )
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
