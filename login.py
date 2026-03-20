import streamlit as st
import requests

st.title("Acesso ao Sistema")
st.write("Por favor, insira suas credenciais.")

st.markdown("""
    <style>
        [data-testid="stStatusWidget"] {visibility: hidden;}
        .stDeployButton {display:none;}
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)


with st.form("form_login"):
    usuario_input = st.text_input("Usuário")
    senha_input = st.text_input("Senha", type="password")
    submit = st.form_submit_button("Entrar")

if submit:
    # Substitua pela sua URL de login
    url_api = "https://apis.glorysoft.com.br/auth/auth" 
    payload = {"email": usuario_input, "password": senha_input}
    try:
        response = requests.post(url_api, json=payload)
        
        if response.status_code == 200:

            dados = response.json()

            
            # 🚀 CORREÇÃO AQUI: Pegando o token de dentro do dicionário "data"
            token_recebido = dados.get("data", {}).get("token", "")
            
            # Salva os dados na sessão
            st.session_state["autenticado"] = True
            st.session_state["token"] = token_recebido # Salva o token real
            
            # Força o recarregamento. O main.py vai assumir e trocar para api.py
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos.")
            
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao conectar com a API: {e}")