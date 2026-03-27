from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import json

stay_agent = Agent(
    name="stay_agent",
    model=LiteLlm("gemini-2.5-flash"),
    description="Suggests accommodation options for a trip.",
    instruction=(
        "Given a destination, dates, and budget, suggest 2 accommodation options. "
        "For each stay, provide hotel name, price per night, location, and a short description. "
        "Respond in JSON format with key 'stays', containing a list of stay objects. "
        "Each stay must have: name, price_per_night, location, and description."
    )
)

session_service = InMemorySessionService()

runner = Runner(
    agent=stay_agent,
    app_name="stay_app",
    session_service=session_service
)

USER_ID = "user_stay"
SESSION_ID = "session_stay"

async def execute(request):
    session_service.create_session(
        app_name="stay_app",
        user_id=USER_ID,
        session_id=SESSION_ID
    )

    prompt = (
        f"User is traveling to {request['destination']} from {request['start_date']} to {request['end_date']}, "
        f"with a budget of {request['budget']}. Suggest 2 accommodation options. "
        f"For each stay include: name, price_per_night, location, and description. "
        f"Respond ONLY in valid JSON using key 'stays'."
    )

    message = types.Content(role="user", parts=[types.Part(text=prompt)])

    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=message
    ):
        if event.is_final_response():
            response_text = event.content.parts[0].text

            try:
                parsed = json.loads(response_text)

                if "stays" in parsed and isinstance(parsed["stays"], list):
                    return {"stays": parsed["stays"]}
                else:
                    print("'stays' key missing or invalid")
                    return {"stays": response_text}

            except json.JSONDecodeError as e:
                print("JSON parsing failed:", e)
                print("Response content:", response_text)
                return {"stays": response_text}