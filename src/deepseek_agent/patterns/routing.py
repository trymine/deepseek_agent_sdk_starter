from agents import Agent, Runner
from ..client import make_model

def build_routing_agents():
    model = make_model()

    order_agent = Agent(
        name="OrderSupport",
        instructions=(
            "Handle order status, delivery, and tracking questions. "
            "If required order information is missing, ask for it. "
            "Never invent order status or tracking numbers."
        ),
        model=model,
    )
    refund_agent = Agent(
        name="RefundSupport",
        instructions=(
            "Handle refund and return policy questions. "
            "Do not claim a refund has been processed unless a real "
            "authorized tool confirms it."
        ),
        model=model,
    )
    general_agent = Agent(
        name="GeneralSupport",
        instructions=(
            "Handle general customer support questions. "
            "Be concise and ask clarifying questions when necessary."
        ),
        model=model,
    )

    router = Agent(
        name="SupportRouter",
        instructions=(
            "Route the user's request to the most appropriate specialist. "
            "Order tracking/status/delivery -> OrderSupport. "
            "Refund/return/cancellation policy -> RefundSupport. "
            "Everything else -> GeneralSupport. "
            "If intent is ambiguous, ask a clarifying question rather than "
            "making an unsupported assumption."
        ),
        model=model,
        handoffs=[order_agent, refund_agent, general_agent],
    )
    return router

async def run_routing(user_input: str) -> str:
    router = build_routing_agents()
    result = await Runner.run(router, user_input)
    return result.final_output