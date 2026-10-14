# crewai-agent-hr

Agent **HR** trong sample vận hành "Kế hoạch chiến dịch quý" (Marketing · Sale · HR) chạy trên CrewAI AMP.

- Nhận dự báo nhân lực của Sale → kế hoạch tuyển, đào tạo, chi phí, thời gian; nếu không tuyển đủ thì hỏi lại Sale (qua Marketing).
- Số liệu tính bằng code trong tool `staffing_plan` theo `src/crewai_agent_hr/team.yaml`; guardrail code kiểm tổng chi phí và số người tuyển.
- Gọi được 2 cách: `/kickoff` của deployment (input `forecast`, JSON) hoặc **A2A** (`/a2a`, agent card ở `/.well-known/agent-card.json`), xác thực `Authorization: Bearer $AUTH_TOKEN`.
- LLM: **FakeLLM** trả lời theo kịch bản (`script.py`) — không cần khóa. Đặt `MODEL=<provider/model>` (+ khóa) để dùng LLM thật.

```bash
uv sync --group dev && .venv/bin/pytest -q      # test offline
.venv/bin/crewai run                            # chạy với dữ liệu mẫu
.venv/bin/crewai deploy validate                # kiểm tra trước deploy
```

`src/crewai_agent_hr/fake_llm.py` được sinh từ `ams/template/` (sửa ở đó rồi chạy `ams/scripts/sync_template.py`).
