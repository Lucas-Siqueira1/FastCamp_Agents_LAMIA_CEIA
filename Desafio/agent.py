from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
from dotenv import load_dotenv
import uvicorn

load_dotenv()

app = FastAPI()

aquivo = pd.read_csv("mtsamples.csv")

def buscar_transcricao(indice: int) -> dict:
    if indice < 0 or indice >= len(aquivo):
        return {"erro": f"Índice inválido. Escolha entre 0 e {len(aquivo) - 1}"}
    
    linha = aquivo.iloc[indice]
    return {
        "indice": indice,
        "descricao": linha["description"],
        "especialidade_real": linha["medical_specialty"],
        "transcricao": linha["transcription"]
    }

def analisar_transcricao(transcricao: str) -> dict:
    if not transcricao:
        return {"erro": "Transcrição vazia"}
    
    return {"transcricao": transcricao}

agente_classificador = Agent(
    name="agente_classificador",
    model="gemini-2.5-flash",
    description="Agente responsável por identificar qual especialidade médica aquela transcrição diz respeito.",
    instruction="""
                Você é um especialista em medicina clínica.
                Sua função é identificar a especialidade médica de uma transcrição clínica.
                Instruções:
                - Analise a transcrição recebida
                - Identifique a especialidade médica correspondente (ex: Cardiologia, Ortopedia, Neurologia, etc.)
                - Responda apenas com o nome da especialidade em português
                - Seja direto e objetivo, sem explicações adicionais
                """,
    tools=[analisar_transcricao]
)

agente_de_resumo = Agent(
    name="agente_de_resumo",
    model="gemini-2.5-flash",
    description="Agente responsável por resumir as transcrições médicas.",
    instruction="""
                Você é um assistente médico especializado em resumos clínicos.
                Sua função é resumir transcrições médicas em bullet points claros e objetivos.
                Instruções:
                - Analise a transcrição recebida
                - Extraia as informações mais importantes como: sintomas, diagnóstico, medicamentos e procedimentos
                - Apresente o resumo em bullet points em português
                - Seja claro e objetivo, use linguagem médica quando necessário
                """,
    tools=[analisar_transcricao]
)

orquestrador = Agent(
    name="orquestrador",
    model="gemini-2.5-flash",
    description="Agente responsável por delegar as tarefas para o agente especialista mais capacitado para resolvê-la.",
    instruction="""
                Você é o orquestrador de um sistema médico inteligente.
                Sua função é coordenar os agentes especializados para processar transcrições médicas.
                Instruções:
                - Quando receber um índice, use a ferramenta 'buscar_transcricao' para obter a transcrição
                - Encaminhe a transcrição para o agente_classificador identificar a especialidade
                - Encaminhe a transcrição para o agente_de_resumo gerar o resumo em bullet points
                - Consolide as respostas e retorne no seguinte formato:
                Especialidade: <especialidade identificada>
                Resumo:
                <bullet points do resumo>
                """,
    tools=[buscar_transcricao],
    sub_agents=[agente_classificador, agente_de_resumo]
)

session_service=InMemorySessionService()
runner = Runner(
    agent=orquestrador,
    app_name="medical_assistant",
    session_service=session_service
)

class Payload(BaseModel):
    indice: int

@app.post("/run")
async def processar(payload: Payload):
    session_id = f"sessao_{payload.indice}"
    
    try:
        await session_service.create_session(
            app_name="medical_assistant",
            user_id=session_id,
            session_id=session_id
        )
    except Exception:
        pass

    message = types.Content(
        role="user",
        parts=[types.Part(text=f"Processe a transcrição de índice {payload.indice}")]
    )

    async for event in runner.run_async(
        user_id=session_id,
        session_id=session_id,
        new_message=message
    ):
        if event.is_final_response():
            return {"resposta": event.content.parts[0].text}

    return {"resposta": "Não consegui processar a transcrição."}