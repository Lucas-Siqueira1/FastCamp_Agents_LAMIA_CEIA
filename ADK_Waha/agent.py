from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from google.adk.tools import google_search
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import requests
import uvicorn

load_dotenv()
app = FastAPI()

def calcular_parcelas(preco: float, meses: int, taxa: float): #ferramenta responsável por calcular o valor das parcelas, usando o sistema de juros compostos
    total = preco * ((1+taxa) ** meses)
    parcelas = total/meses

    return {
        "total": round(total, 2),
        "parcelas": round(parcelas, 2)

    }

def calcular_media(precos: list[float]): #ferramenta responsável por calcular a média dos preços dos produtos que o agente encontrar, assim fornecendo o preço médio
    return sum(precos)/len(precos)



#Aqui é criado o agente que irá usar a ferramenta do ADK, google search, para pesquisar os preços dos produtos que o usuário desejar. Também podendo usar 
#a ferramenta 'calcular_media' para calcular a media dos produtos
agente_preco = Agent( 
    name="agente_preco",
    model="gemini-2.5-flash",
    description="Agente especializado em buscar preços de produtos na internet.",
    instruction="""
                Você é um especialista em pesquisa de preços.
                Use a ferramenta google_search para encontrar 5 preços recentes do produto no Brasil.
                Liste os preços encontrados e calcule o preço médio usando a ferramenta 'calcular_media'.
                Responda em português, mostrando:
                 - o preço médio
                 - a faixa de preços encontrada
                """,
    tools=[google_search, calcular_media],
)

#Aqui é criado o agente de finanças, responsável por calcular quanto ficará o valor total e cada parcela de um produto divido em uma determinada quantidade
#de vezes e com determinada taxa de juros, podendo usar a ferramenta de calcular parcelas 
agente_financas = Agent(
    name="agente_financas",
    model="gemini-2.5-flash",
    description="Agente especializado em montante de parcelamentos e valores de parcelas.",
    instruction="""
                Você é um especialista em cálculos financeiros, focado em parcelamentos e juros.
                Sua função é calcular valores de compras parceladas com ou sem juros, de forma precisa.
                REGRAS IMPORTANTES:
                1. Sempre responda em português.
                2. Seja claro, direto e organizado.
                3. Mostre sempre:
                - valor total
                - valor de cada parcela
                TIPOS DE CÁLCULO:
                - Se o usuário disser "sem juros":
                → Divida o valor total pelo número de parcelas.
                - Se o usuário informar uma taxa de juros:
                → Use a ferramenta 'calcular_parcelas'
                INTERPRETAÇÃO:
                - "6x com 11%" → juros compostos com taxa de 11% ao período
                - Se não for especificado, assuma sem juros.
                FORMATO DA RESPOSTA:
                Responda sempre neste formato:
                - Parcelamento:
                Preço: R$ X
                Parcelas: Nx
               
                Se for sem juros:
                Parcela: R$ Y
                Total: R$ X

                Se for com juros:
                Taxa: X%
                Parcela: R$ Y
                Total: R$ Z

                Não invente valores.
                Se não tiver o preço, peça para o usuário informar.
                """,
    tools=[calcular_parcelas],
)

#Por fim, esse é o agente orquestrador, que é responsável por delegar as tarefas para os agentes especializados, ele lida diretamente com as requisições do usuário
orquestrador = Agent(
    name="orquestrador",
    model="gemini-2.5-flash",
    description="Agente que organiza e gerencia o sistema",
    instruction="""
                Você é o agente orquestrador.
                Sua função é entender a intenção do usuário e delegar a tarefa para o agente correto.

                - Se a pergunta for sobre preços de algum produto -> use o 'agente_preco'
                - Se a pergunta for sobre parcelamento -> use o 'agente_financas'

                Sempre responda em português.
                Não resolva problemas sozinho, mande para o agente especializado.
                Se a mensagem não estiver clara, peça mais detalhes para o usuário.
                """,
    sub_agents=[agente_financas, agente_preco],
)

#A seguir é usado o 'InMemorySessionService()' para o agente conseguir guardar na memória o que está sendo falado naquela sessão
session_service = InMemorySessionService()
runner = Runner(
    agent=orquestrador,
    app_name="buy_assistant",
    session_service=session_service
)

#Aqui é usado o pydantic para validar os dados que serão passados para o payload
class Payload(BaseModel):
    mensagem: str
    user_id: str
    session_id: str

#Por fim, o endpoint que enviará a resposta para o n8n
@app.post("/run")
async def run(payload: Payload):
    session_id = payload.user_id.replace("@", "_").replace(".", "_")
    try:
        await session_service.create_session(
            app_name="buy_assistant",
            user_id=session_id,
            session_id=session_id
        )
    except Exception:
        pass
    message = types.Content(
        role="user",
        parts=[types.Part(text=payload.mensagem)]
    )
    async for event in runner.run_async(
        user_id=session_id,
        session_id=session_id,
        new_message=message
    ):
        if event.is_final_response():
            return {"resposta": event.content.parts[0].text}
    return {"resposta": "Não consegui processar sua mensagem."}