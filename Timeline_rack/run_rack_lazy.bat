@echo off
REM Chạy pipeline timeline rack lazy
python -c "from timeline_rack_v5_lazy import timeline_rack_v5_lazy; from request_cc_from_robot_pipeline import request_cc_from_robot_pipeline; timeline_rack_v5_lazy(request_cc_fn=request_cc_from_robot_pipeline)"
pause
