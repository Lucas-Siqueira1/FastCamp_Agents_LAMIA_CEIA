from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import json

flight_agent = Agent(
    name="flight_agent",
    model=LiteLlm("gemini-2.5-flash"),
    description="Suggests flight options for a user trip.",
    instruction=(
        "Given a destination, dates, and budget, suggest 2 flight options. "
        "For each flight, provide airline name, price, departure time, and flight details. "
        "Respond in JSON format with key 'flights', containing a list of flight objects. "
        "Each flight must have: airline, price, departure_time, and details."
    )
)

session_service = InMemorySessionService()

runner = Runner(
    agent=flight_agent,
    app_name="flight_app",
    session_service=session_service
)

USER_ID = "user_flights"
SESSION_ID = "session_flights"

async def execute(request):
    session_service.create_session(
        app_name="flight_app",
        user_id=USER_ID,
        session_id=SESSION_ID
    )

    prompt = (
        f"User is traveling to {request['destination']} from {request['start_date']} to {request['end_date']}, "
        f"with a budget of {request['budget']}. Suggest 2 flight options. "
        f"For each flight include: airline, price, departure_time, and details. "
        f"Respond in JSON format using key 'flights'."
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

                if "flights" in parsed and isinstance(parsed["flights"], list):
                    return {"flights": parsed["flights"]}
                else:
                    print("'flights' key missing or invalid")
                    return {"flights": response_text}  # fallback

            except json.JSONDecodeError as e:
                print("JSON parsing failed:", e)
                print("Response content:", response_text)
                return {"flights": response_text}  # fallback