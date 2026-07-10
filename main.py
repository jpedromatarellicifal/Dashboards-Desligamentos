import streamlit as st

st.set_page_config(
    page_title="Dashboard RH - Turnover",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
        [data-testid="stStatusWidget"] {visibility: hidden;}
        .stDeployButton {display:none;}
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Inicializa as variáveis na sessão global
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False
if "token" not in st.session_state:
    st.session_state["token"] = None

# Define os arquivos como páginas do Streamlit
pagina_login = st.Page("login.py", title="Login", icon="🔒")
pagina_dashboard = st.Page("api.py", title="Dashboard", icon="📊")

# Lógica de Roteamento Estrito (Bloqueia a navegação livre)
if st.session_state["autenticado"]:
    pg = st.navigation([pagina_dashboard])
else:
    pg = st.navigation([pagina_login])

pg.run()