from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from dotenv import load_dotenv
import os

load_dotenv()

orquestrador = Agent(
    name="orquestrador",
    model=LiteLlm("gemini-2.5-flash"),
    description="Agente responsável por coordenar recomendações de treino e equipamentos de corrida com base nos objetivos do usuário.",
    instruction=
            """
            Você é um treinador de corrida experiente.

            Sua função é:
            - Entender o objetivo do usuário (distância, nível e meta)
            - Solicitar recomendações de treino ao training_agent
            - Solicitar recomendações de equipamentos ao gear_agent
            - Combinar todas as informações em uma resposta clara e organizada

            Regras:
            - Sempre responda em português
            - Organize a resposta em seções (ex: treino, equipamentos)
            - Seja direto e didático
            - Não invente dados — utilize apenas as informações retornadas pelos outros agentes
            - Use linguagem de treinador (motivadora, mas objetiva)

            Formato esperado:
            - Introdução breve
            - Seção de treino
            - Seção de equipamentos
            - Dica final (opcional)
            """
)
session_service = InMemorySessionService()
runner = Runner(
    agent=orquestrador,
    app_name="host_app",
    session_service=session_service
)
USER_ID = "user_host"
SESSION_ID = "session_host"

async def execute(request):
    # Ensure session exists
    session_service.create_session(
        app_name="host_app",
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    prompt = (
        f"O usuário quer correr {request['distance']}km, possui nível {request['level']} "
        f"e tem como objetivo {request['goal']}. "
        f"Você recebeu as seguintes recomendações de outros agentes: "
        f"Treinos: {request.get('training_plan', [])}, "
        f"Tênis: {request.get('shoes', [])}, "
        f"Nutrição: {request.get('nutrition_tips', [])}. "
        f"Organize essas informações em uma resposta clara e estruturada. "
        f"Divida em seções: treino, equipamentos e nutrição. "
        f"Use linguagem objetiva e motivadora. "
        f"Responda em português."
    )
    message = types.Content(role="user", parts=[types.Part(text=prompt)])
    async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=message):
        if event.is_final_response():
            return {"summary": event.content.parts[0].text}