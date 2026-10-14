#!/usr/bin/env python
import json
import sys

from crewai_agent_hr.crew import CrewaiAgentHr

SAMPLE = {"forecast": json.dumps({"deals": 60, "sales_headcount_needed": 7, "sales_headcount_planned": 7,
                                  "quota_per_rep": 9}, ensure_ascii=False)}


def run():
    result = CrewaiAgentHr().crew().kickoff(inputs=SAMPLE)
    print(result.raw)


def run_with_trigger():
    if len(sys.argv) < 2:
        raise Exception("No trigger payload provided. Please provide JSON payload as argument.")
    payload = json.loads(sys.argv[1])
    forecast = payload.get("forecast", payload)
    inputs = {"forecast": forecast if isinstance(forecast, str) else json.dumps(forecast, ensure_ascii=False)}
    return CrewaiAgentHr().crew().kickoff(inputs=inputs)


def train():
    CrewaiAgentHr().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=SAMPLE)


def replay():
    CrewaiAgentHr().crew().replay(task_id=sys.argv[1])


def test():
    CrewaiAgentHr().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=SAMPLE)


if __name__ == "__main__":
    run()
