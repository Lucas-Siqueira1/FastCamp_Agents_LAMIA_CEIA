from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import json

agente_treino = Agent(
    name="agente_treino",
    model=LiteLlm("gemini-2.5-flash"),
    description="Agente responsável por gerar recomendações de treinos de corrida com base na distância e nível do usuário.",
    instruction=(
        """
        Você é um especialista em treinamento de corrida.

        Sua função é:
        - Receber a distância, nível e objetivo do usuário
        - Gerar um plano de treino simples e eficiente

        Regras:
        - Sempre responda em português
        - Retorne apenas dados estruturados (não escreva textos longos)
        - Inclua tipos de treino como:
        - corrida leve
        - treino intervalado
        - longão
        - Adapte o volume e intensidade ao nível do usuário

        Formato de saída esperado:
        {
        "training_plan": [
            "descrição do treino 1",
            "descrição do treino 2",
            ...
        ]
        }
        """
    )
)

session_service = InMemorySessionService()

runner = Runner(
    agent=agente_treino,
    app_name="training_app",
    session_service=session_service
)

USER_ID = "user_training"
SESSION_ID = "session_training"

async def execute(request):
    session_service.create_session(
        app_name="training_app",
        user_id=USER_ID,
        session_id=SESSION_ID
    )

    prompt = (
        f"O usuário quer correr {request['distance']}km, possui nível {request['level']} "
        f"e tem como objetivo {request['goal']}. "
        f"Gere um plano de treino com 3 a 5 sessões semanais. "
        f"Inclua corrida leve, treino intervalado e longão. "
        f"Adapte a intensidade ao nível do usuário. "
        f"Retorne apenas JSON com a chave 'training_plan'. "
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

                if "training_plan" in parsed and isinstance(parsed["training_plan"], list):
                    return {"training_plan": parsed["training_plan"]}
                else:
                    print("'training_plan' key missing or invalid")
                    return {"training_plan": response_text}  # fallback

            except json.JSONDecodeError as e:
                print("JSON parsing failed:", e)
                print("Response content:", response_text)
                return {"training_plan": response_text}  # fallback