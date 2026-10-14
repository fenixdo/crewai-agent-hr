"""Offline tests: staffing math from team.yaml, the code guardrail, and a full crew run with the scripted LLM."""
import json
from types import SimpleNamespace

from crewai_agent_hr.crew import CrewaiAgentHr, StaffingPlan, plan_guardrail
from crewai_agent_hr.tools.staffing import staffing, team


def test_staffing_caps_hires_and_asks_sale():
    t = team()
    s = staffing(t["current_sales_reps"] + t["max_hires_per_quarter"] + 2)
    assert s["hires"] == t["max_hires_per_quarter"]
    assert s["open_questions"] and s["open_questions"][0]["max_headcount"] == t["current_sales_reps"] + s["hires"]
    assert s["cost"] == sum(i["amount"] for i in s["cost_items"])


def test_no_hiring_needed():
    assert staffing(1)["hires"] == 0 and staffing(1)["open_questions"] == []


def test_guardrail_rejects_wrong_total():
    s = staffing(6)
    bad = StaffingPlan(hire_plan="x", training_plan="y", **{**s, "cost": s["cost"] + 1})
    ok, msg = plan_guardrail(SimpleNamespace(pydantic=bad, raw=bad.model_dump_json()))
    assert not ok and "tổng chi phí" in msg


def test_crew_runs_end_to_end_with_fake_llm(monkeypatch):
    monkeypatch.delenv("MODEL", raising=False)
    monkeypatch.setenv("FAKE_LLM_DELAY", "0")
    out = CrewaiAgentHr().crew().kickoff(inputs={"forecast": json.dumps({"sales_headcount_planned": 5})})
    plan = StaffingPlan.model_validate(out.pydantic.model_dump() if out.pydantic else json.loads(out.raw))
    assert plan.needed == 5 and plan.hires == staffing(5)["hires"]
