from common.a2a_server import create_app
from .task_manager import execute  # importa a função que você criou

app = create_app(agent=type("Agent", (), {"execute": execute}))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8001)