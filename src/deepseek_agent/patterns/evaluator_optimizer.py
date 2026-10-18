from pydantic import BaseModel, Field
from agents import Agent, Runner
from ..client import make_model
from ..config import get_settings

class Evaluation(BaseModel):
    score: int = Field(ge=1, le=5)
    passed: bool
    feedback: str
    reasons: list[str] = Field(default_factory=list)

def build_agents():
    model = make_model()

    writer = Agent(
        name="Writer",
        instructions=(
            "Produce a helpful answer to the user's task. "
            "Follow all explicit constraints. Do not fabricate facts. "
            "When information is missing, state assumptions or ask."
        ),
        model=model,
    )

    evaluator = Agent(
        name="Evaluator",
        instructions=(
            "Evaluate the candidate answer against the task. "
            "Score 1-5 for correctness, completeness, relevance, and clarity. "
            "Be strict. passed=true only if score >= 4 and there are no "
            "material correctness or constraint violations. "
            "Give actionable feedback for improvement."
        ),
        model=model,
        output_type=Evaluation,
    )
    optimizer = Agent(
        name="Optimizer",
        instructions=(
            "Improve the candidate answer using the evaluator feedback. "
            "Preserve correct content, fix identified issues, and avoid "
            "unsupported claims. Return only the improved answer."
        ),
        model=model,
    )
    return writer, evaluator, optimizer

async def run_evaluator_optimizer(
    task: str, max_rounds: int | None = None
) -> dict:
    settings = get_settings()
    rounds_limit = max_rounds or settings.max_optimization_rounds
    writer, evaluator, optimizer = build_agents()

    draft_result = await Runner.run(
        writer, f"Task:\n{task}\n\nWrite the best answer you can."
    )
    draft = str(draft_result.final_output)
    history = []

    for round_no in range(1, rounds_limit + 1):
        evaluation_result = await Runner.run(
            evaluator,
            f"Task:\n{task}\n\nCandidate answer:\n{draft}",
        )
        evaluation = evaluation_result.final_output
        history.append({
            "round": round_no,
            "score": evaluation.score,
            "passed": evaluation.passed,
            "feedback": evaluation.feedback,
            "reasons": evaluation.reasons,
        })

        if evaluation.passed:
            break

        if round_no < rounds_limit:
            optimized_result = await Runner.run(
                optimizer,
                f"Task:\n{task}\n\n"
                f"Current answer:\n{draft}\n\n"
                f"Evaluator score: {evaluation.score}/5\n"
                f"Feedback: {evaluation.feedback}\n"
                f"Reasons: {evaluation.reasons}\n\n"
                "Return the improved answer.",
            )
            draft = str(optimized_result.final_output)

    return {
        "answer": draft,
        "history": history,
        "rounds": len(history),
        "final_evaluation": history[-1] if history else None,
    }