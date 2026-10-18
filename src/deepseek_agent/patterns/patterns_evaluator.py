import asyncio
import json
from pathlib import Path
from .routing import run_routing
from .evaluator_optimizer import run_evaluator_optimizer

async def evaluate_dataset(dataset_path: str, pattern: str) -> dict:
    path = Path(dataset_path)
    cases = json.loads(path.read_text(encoding="utf-8"))
    rows = []

    for case in cases:
        if pattern == "routing":
            output = await run_routing(case["input"])
            expected = case.get("expected_contains", [])
            passed = all(
                phrase.lower() in output.lower() for phrase in expected
            )
            rows.append({
                "id": case["id"],
                "passed": passed,
                "output": output,
                "expected_contains": expected,
            })
        elif pattern == "evaluator-optimizer":
            result = await run_evaluator_optimizer(case["input"])
            rows.append({
                "id": case["id"],
                "rounds": result["rounds"],
                "final_evaluation": result["final_evaluation"],
                "answer": result["answer"],
            })
        else:
            raise ValueError(f"Unknown pattern: {pattern}")

    report = {
        "pattern": pattern,
        "total": len(rows),
        "results": rows,
    }
    Path("reports").mkdir(exist_ok=True)
    out = Path("reports") / f"{pattern.replace('-', '_')}.json"
    out.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return report

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="datasets/tasks.json")
    parser.add_argument(
        "--pattern",
        choices=["routing", "evaluator-optimizer"],
        required=True,
    )
    args = parser.parse_args()
    report = asyncio.run(evaluate_dataset(args.dataset, args.pattern))
    print(json.dumps({
        "pattern": report["pattern"],
        "total": report["total"],
        "report": f"reports/{args.pattern.replace('-', '_')}.json",
    }, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()