from fastapi import FastAPI, Request
from Timeline_rack.timeline_rack_v5_lazy import timeline_rack_v5_lazy

app = FastAPI()

@app.post("/run")
async def run_pipeline(request: Request):
    data = await request.json()
    route = data["route"]
    result = timeline_rack_v5_lazy(route)
    return result
