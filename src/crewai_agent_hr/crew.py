from crewai import Agent, Crew, Process, Task
from crewai.a2a import A2AServerConfig
from crewai.a2a.auth import SimpleTokenAuth
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, crew, task
from pydantic import BaseModel

from crewai_agent_hr.fake_llm import llm
from crewai_agent_hr.script import HrFakeLLM
from crewai_agent_hr.tools.staffing import StaffingPlanTool, staffing


class StaffingPlan(BaseModel):
    hire_plan: str
    training_plan: str
    current_sales_reps: int
    needed: int
    gap: int
    hires: int
    cost_items: list[dict]
    cost: int
    timeline_weeks: int
    open_questions: list[dict] = []


def plan_guardrail(output):
    """Code check: the total is the sum of its items, and the hires match what the team data allows."""
    p = output.pydantic or StaffingPlan.model_validate_json(output.raw)
    errors = []
    if p.cost != sum(int(i["amount"]) for i in p.cost_items):
        errors.append(f"tổng chi phí {p.cost} khác tổng các hạng mục")
    if p.hires != staffing(p.needed)["hires"]:
        errors.append(f"số người tuyển {p.hires} không khớp dữ liệu đội ({staffing(p.needed)['hires']})")
    return (False, "Sửa lại: " + "; ".join(errors)) if errors else (True, output)


@CrewBase
class CrewaiAgentHr():
    """HR: một agent, gọi được trực tiếp (/kickoff) hoặc qua A2A (AMP mở /a2a; token = AUTH_TOKEN)."""

    agents: list[BaseAgent]
    tasks: list[Task]

    @agent
    def hr_lead(self) -> Agent:
        return Agent(
            config=self.agents_config['hr_lead'],  # type: ignore[index]
            tools=[StaffingPlanTool()],
            llm=llm(HrFakeLLM),
            max_iter=4,
            a2a=A2AServerConfig(name="HR", description="Kế hoạch nhân sự bán hàng: tuyển, đào tạo, chi phí",
                                auth=SimpleTokenAuth()),
            verbose=True,
        )

    @task
    def staffing_task(self) -> Task:
        return Task(
            config=self.tasks_config['staffing_task'],  # type: ignore[index]
            output_pydantic=StaffingPlan,
            guardrail=plan_guardrail,
        )

    @crew
    def crew(self) -> Crew:
        return Crew(agents=self.agents, tasks=self.tasks, process=Process.sequential, verbose=True)
