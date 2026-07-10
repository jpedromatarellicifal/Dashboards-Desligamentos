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
pagina_login = st.Page("login.py", title="Login", icon="🔒", default=True)
pagina_dashboard = st.Page("api.py", title="Dashboard", icon="📊")

# Usa a navegação estática oculta para evitar bugs de roteamento e recarregamento
pg = st.navigation([pagina_login, pagina_dashboard], position="hidden")

# Se não estiver logado e tentar acessar o dashboard, redireciona pro login
if not st.session_state["autenticado"] and pg.title == "Dashboard":
    st.switch_page("login.py")

pg.run()