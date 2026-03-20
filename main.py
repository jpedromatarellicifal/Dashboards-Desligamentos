import streamlit as st

# Inicializa as variáveis na sessão global
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
if "token" not in st.session_state:
    st.session_state["token"] = None

st.markdown("""
    <style>
        [data-testid="stStatusWidget"] {visibility: hidden;}
        .stDeployButton {display:none;}
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)


# Define os arquivos como páginas do Streamlit
pagina_login = st.Page("login.py", title="Login", icon="🔒")
pagina_dashboard = st.Page("api.py", title="Dashboard", icon="📊")

# Lógica de Roteamento Estrito (Bloqueia a navegação livre)
if st.session_state["autenticado"]:
    # Se estiver logado, o Streamlit SÓ conhece a página do dashboard
    pg = st.navigation([pagina_dashboard])
else:
    # Se NÃO estiver logado, o Streamlit SÓ conhece a página de login
    pg = st.navigation([pagina_login])

# Executa a página selecionada
pg.run()