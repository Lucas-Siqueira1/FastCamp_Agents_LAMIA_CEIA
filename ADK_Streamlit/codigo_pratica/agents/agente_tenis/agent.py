from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import json

agente_tenis = Agent(
    name="agente_tenis",
    model=LiteLlm("gemini-2.5-flash"),
    description="Agente responsável por recomendar tênis de corrida com base na distância e tipo de treino.",
    instruction=(
        """
        Você é um especialista em equipamentos de corrida.

        Sua função é:
        - Recomendar tênis adequados com base na distância e objetivo do usuário

        Regras:
        - Sempre responda em português
        - Retorne apenas dados estruturados
        - Não invente modelos inexistentes
        - Sugira de 2 a 4 opções
        - Considere categorias como:
        - leve/velocidade
        - treino diário
        - amortecimento

        Formato de saída esperado:
        {
        "shoes": [
            "nome do tênis 1",
            "nome do tênis 2"
        ]
        }
        """
    )
)

session_service = InMemorySessionService()

runner = Runner(
    agent=agente_tenis,
    app_name="shoes_app",
    session_service=session_service
)

USER_ID = "user_equipment"
SESSION_ID = "session_equipment"

async def execute(request):
    session_service.create_session(
        app_name="equipment_app",
        user_id=USER_ID,
        session_id=SESSION_ID
    )

    prompt = (
        f"O usuário quer correr {request['distance']}km e tem como objetivo {request['goal']}. "
        f"Sugira de 2 a 4 tênis adequados para esse tipo de corrida. "
        f"Considere: "
        f"curtas distâncias → tênis leves, "
        f"médias → versáteis, "
        f"longas → amortecimento. "
        f"Retorne apenas JSON com a chave 'shoes'. "
        f"Use apenas modelos reais. "
        f"Responda em português."
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

                if "shoes" in parsed and isinstance(parsed["shoes"], list):
                    return {"shoes": parsed["shoes"]}
                else:
                    print("'shoes' key missing or invalid")
                    return {"shoes": response_text}  # fallback

            except json.JSONDecodeError as e:
                print("JSON parsing failed:", e)
                print("Response content:", response_text)
                return {"shoes": response_text}  # fallback