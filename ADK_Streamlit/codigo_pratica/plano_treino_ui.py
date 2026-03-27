import streamlit as st
import requests

st.set_page_config(page_title="Plano de treinamento para corrida")
st.title("Plano de treinamento para corrida")
distancia = st.text_input("Qual distancia deseja correr?", placeholder="ex: 21km")
tempo = st.text_input("Em quanto tempo deseja correr?", placeholder="ex: 50 minutos")
nível = st.text_input("Qual seu nível de treinamento?", placeholder="ex: avançado")
if st.button("Plan My Trip ✨"):
    if not all([distancia, tempo, nível]):
        st.warning("Please fill in all the details.")
    else:
        payload = {
            "distancia": distancia,
            "tempo": tempo,
            "nível": str(nível),
        }
        response = requests.post("http://localhost:8000/run", json=payload)
        if response.ok:
            data = response.json()
            st.subheader("Treinos")
            st.markdown(data["training_plan"])
            st.subheader("Equipamentos")
            st.markdown(data["shoes"])
        else:
            st.error("Failed to fetch training plan. Please try again.")