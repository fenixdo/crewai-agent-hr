"""staffing_plan: hires, training and cost from code and team.yaml."""
from __future__ import annotations

import json
from pathlib import Path

import yaml
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

TEAM = Path(__file__).resolve().parents[1] / "team.yaml"


def team() -> dict:
    return yaml.safe_load(TEAM.read_text())


def staffing(sales_headcount_needed: int) -> dict:
    t = team()
    gap = max(0, sales_headcount_needed - t["current_sales_reps"])
    hires = min(gap, t["max_hires_per_quarter"])
    items = [{"item": "tuyển dụng", "amount": hires * t["recruit_cost_per_hire"]},
             {"item": "đào tạo sản phẩm + kỹ năng bán", "amount": hires * t["training_cost_per_hire"]},
             {"item": "lương người mới trong quý", "amount": hires * t["monthly_salary"] * t["salary_months_in_quarter"]}]
    questions = []
    if gap > hires:
        questions.append({"to": "sale", "max_headcount": t["current_sales_reps"] + hires,
                          "text": f"Quý này chỉ tuyển được tối đa {hires} người (thiếu {gap - hires}). Sale chạy được với "
                                  f"{t['current_sales_reps'] + hires} người và chỉ tiêu cao hơn không?"})
    return {"current_sales_reps": t["current_sales_reps"], "needed": sales_headcount_needed, "gap": gap,
            "hires": hires, "cost_items": items, "cost": sum(i["amount"] for i in items),
            "timeline_weeks": (t["weeks_to_hire"] + t["weeks_training"]) if hires else 0, "open_questions": questions}


class StaffingInput(BaseModel):
    sales_headcount_needed: int = Field(..., description="Số nhân viên bán hàng Sale cần cho chiến dịch")


class StaffingPlanTool(BaseTool):
    name: str = "staffing_plan"
    description: str = ("Lập kế hoạch nhân sự bán hàng: số người cần tuyển, chi phí tuyển + đào tạo + lương, thời gian, "
                        "và câu hỏi cần làm rõ nếu không tuyển đủ. Trả JSON.")
    args_schema: type[BaseModel] = StaffingInput

    def _run(self, sales_headcount_needed: int) -> str:
        return json.dumps(staffing(int(sales_headcount_needed)), ensure_ascii=False)
