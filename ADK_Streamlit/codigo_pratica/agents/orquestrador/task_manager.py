from common.a2a_client import call_agent
TRAININF_PLAN_URL = "http://localhost:8002/run"
SHOES_URL = "http://localhost:8001/run"

async def run(payload):
    #Print what the host agent is sending
    print("Incoming payload:", payload)
    training_plan = await call_agent(TRAININF_PLAN_URL, payload)
    shoes = await call_agent(SHOES_URL, payload)
    # Log outputs
    print("Plano de treino:", training_plan)
    print("Equipamentos:", shoes)
    training_plan = training_plan if isinstance(training_plan, dict) else {}
    shoes = shoes if isinstance(shoes, dict) else {}
    return {
        "training_plan": training_plan.get("training_plan", "No training_plan returned."),
        "shoes": shoes.get("shoess", "No shoes options returned."),
    }