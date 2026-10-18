from agents import AsyncOpenAI, OpenAIChatCompletionsModel, set_tracing_disabled
from .config import get_settings

def make_model():
    set_tracing_disabled(disabled=True)
    settings = get_settings()
    client = AsyncOpenAI(
        api_key=settings.api_key,
        base_url=settings.base_url,
    )
    model = OpenAIChatCompletionsModel(
        model=settings.model,
        openai_client=client,
    )
    return model