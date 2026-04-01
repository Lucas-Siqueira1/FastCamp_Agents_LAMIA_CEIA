import streamlit as st
import requests

st.set_page_config(page_title="Assistente Médico", page_icon="🩺")
st.title("Analisador de Transcrições Médicas")

indice = st.number_input("Selecione o índice da transcrição", min_value=0, step=1)

if st.button("Analisar Transcrição 🧠"):
    payload = {
        "indice": indice
    }

    with st.spinner("Analisando transcrição..."):
        response = requests.post("http://localhost:8000/run", json=payload)

    if response.ok:
        data = response.json()

        st.subheader(" Resultado")
        st.markdown(data.get("resposta", "").replace("Resumo:", "\n\n###  Resumo\n"))
    else:
        st.error("Falha ao analisar a transcrição. Tente novamente.")