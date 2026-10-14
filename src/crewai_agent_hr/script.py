"""What the scripted model says as the HR lead (see fake_llm.py)."""
from __future__ import annotations

import re

from crewai_agent_hr.fake_llm import ScriptedLLM, act, final, first_json, last_observation


class HrFakeLLM(ScriptedLLM):
    def respond(self, text: str) -> str:
        obs = last_observation(text)
        if obs is None:
            req = first_json(text)
            needed = req.get("sales_headcount_planned") or req.get("sales_headcount_needed")
            if not needed:  # running right after Sale in one crew: the forecast arrives as task context
                m = re.search(r'"sales_headcount_planned":\s*(\d+)', text)
                needed = int(m.group(1)) if m else 1
            return act("staffing_plan", {"sales_headcount_needed": int(needed)},
                       "Cần tính số người phải tuyển và chi phí theo dữ liệu đội hiện tại.")
        plan = {"hire_plan": f"Tuyển {obs['hires']} nhân viên bán hàng (đang có {obs['current_sales_reps']}, cần "
                             f"{obs['needed']})" if obs["hires"] else "Không cần tuyển thêm",
                "training_plan": f"{obs['hires']} người mới học sản phẩm + kỹ năng bán 2 tuần" if obs["hires"]
                                 else "Đào tạo nhắc lại cho đội hiện tại",
                **obs}
        return final(plan, "Đã có kế hoạch nhân sự, gửi lại cho Marketing.")
