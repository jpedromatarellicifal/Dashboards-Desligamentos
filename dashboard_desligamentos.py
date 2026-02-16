import requests
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import altair as alt
from dados import Dados_teste

url = "http://localhost:3000/v1/rh_desligamento"

response = requests.get(url)

if response.status_code == 200:
    Dados_teste = response.json()
else:
    print(f"Erro na requisição: {response.status_code}")



st.set_page_config(
    page_title="Dashboard RH - Turnover",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    [data-testid="stMetricValue"] { font-size: 30px; }
    .css-1d391kg { padding-top: 1rem; }
    .painel-metas { background-color: rgba(255, 255, 255, 0.05); padding: 20px; border-radius: 10px; border-left: 5px solid #f39c12; margin-bottom: 25px; }
    .linha-meta { display: flex; justify-content: space-between; margin-bottom: 15px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 5px; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_and_process_data(data):
    df = pd.DataFrame(data)
    for col in ['admissao', 'demissao']:
        df[col] = df[col].replace('None', pd.NaT)
        df[col] = pd.to_datetime(df[col], errors='coerce').dt.tz_localize(None)
    return df

df_raw = load_and_process_data(Dados_teste)

# --- INÍCIO DA SIDEBAR AJUSTADA ---
with st.sidebar:
    st.subheader("📅 Período de Análise")
    data_min = datetime(2024, 1, 1).date()
    start_date = st.date_input("Data Inicial", value=data_min)
    end_date = st.date_input("Data Final", value=datetime.now().date())
    start_ts, end_ts = pd.to_datetime(start_date), pd.to_datetime(end_date)

    st.divider()
    
    # --- NAVEGAÇÃO UNIFICADA ---
    st.title("📂 Navegação")
    
    opcao_selecionada = st.selectbox(
        "Selecione o painel desejado:",
        [
            "Turnover", 
            "Taxa de Desligamento", 
            "Detalhamento por Ano"
        ]
    )
    
    # Lógica Implícita: A escolha do painel define a métrica automaticamente
    # Isso elimina a necessidade do st.radio separado ("Configuração")
    if opcao_selecionada == "Turnover":
        opcao_painel = "Turnover"
        coluna_ativa = "Turnover Tradicional %"
        nome_metrica = "Turnover"
    elif opcao_selecionada == "Taxa de Desligamento":
        opcao_painel = "Taxa de Desligamento"
        coluna_ativa = "Taxa Desligamento (Média) %"
        nome_metrica = "Taxa de Desligamento"
    else:
        opcao_painel = "Detalhamento por Ano"
        coluna_ativa = None
        nome_metrica = "Análise Anual"

    st.divider()
    st.header("🔍 Filtros de Cadastro")
    
    # Filtros de Dados
    empresa_sel = st.selectbox("Empresa", ["Todas"] + sorted(df_raw["empregis"].dropna().unique().tolist()))
    cidade_sel = st.selectbox("Cidade", ["Todas"] + sorted(df_raw["nomcid"].dropna().unique().tolist()))
    depto_sel = st.selectbox("Departamento", ["Todos"] + sorted(df_raw["nomdep"].dropna().unique().tolist()))
    sexo_sel = st.selectbox("Gênero", ["Todos"] + sorted(df_raw["sexo"].dropna().unique().tolist()))
    gerente_sel = st.selectbox("Gerente", ["Todos"] + sorted(df_raw["nomegerente"].dropna().unique().tolist()))
    cc_sel = st.selectbox("Centro de Custo", ["Todos"] + sorted(df_raw["dessetordesp"].dropna().unique().tolist()))
    cargo_sel = st.selectbox("Cargo", ["Todos"] + sorted(df_raw["nomefuncao"].dropna().unique().tolist()))
    
    st.caption("Versão 2.1.2026 - Dashboard Integrado")
# --- FIM DA SIDEBAR ---

# Aplicação dos filtros no DataFrame
df_filtered = df_raw.copy()
if empresa_sel != "Todas": df_filtered = df_filtered[df_filtered["empregis"] == empresa_sel]
if cidade_sel != "Todas": df_filtered = df_filtered[df_filtered["nomcid"] == cidade_sel]
if depto_sel != "Todos": df_filtered = df_filtered[df_filtered["nomdep"] == depto_sel]
if sexo_sel != "Todos": df_filtered = df_filtered[df_filtered["sexo"] == sexo_sel]
if gerente_sel != "Todos": df_filtered = df_filtered[df_filtered["nomegerente"] == gerente_sel]
if cc_sel != "Todos": df_filtered = df_filtered[df_filtered["dessetordesp"] == cc_sel]
if cargo_sel != "Todos": df_filtered = df_filtered[df_filtered["nomefuncao"] == cargo_sel]

def get_metrics(df_in, s_date, e_date):
    if df_in.empty: return pd.DataFrame()
    dates = pd.date_range(start=s_date, end=e_date, freq='MS')
    res = []
    for d in dates:
        m_end = d + pd.offsets.MonthEnd(0)
        hc_ini = df_in[(df_in['admissao'] < d) & ((df_in['demissao'].isna()) | (df_in['demissao'] >= d))].shape[0]
        hc_fim = df_in[(df_in['admissao'] <= m_end) & ((df_in['demissao'].isna()) | (df_in['demissao'] > m_end))].shape[0]
        des = df_in[(df_in['demissao'] >= d) & (df_in['demissao'] <= m_end)].shape[0]
        res.append({
            'Data': d, 'Mês': d.strftime('%b/%Y'), 'Headcount': hc_fim, 'Desligamentos': des,
            'Turnover Tradicional %': round((des / hc_fim * 100), 2) if hc_fim > 0 else 0,
            'Taxa Desligamento (Média) %': round((des / ((hc_ini + hc_fim)/2) * 100), 2) if (hc_ini + hc_fim) > 0 else 0,
            'Meta': 5.0
        })
    return pd.DataFrame(res)

df_dash = get_metrics(df_filtered, start_ts, end_ts)

# Lógica Principal do Dashboard
if opcao_painel in ["Turnover", "Taxa de Desligamento"]:
    k1, k2, k3, k4 = st.columns(4)
    current_hc = df_dash.iloc[-1]['Headcount'] if not df_dash.empty else 0
    total_adm = df_filtered[(df_filtered['admissao'] >= start_ts) & (df_filtered['admissao'] <= end_ts)].shape[0]
    total_des = df_filtered[(df_filtered['demissao'] >= start_ts) & (df_filtered['demissao'] <= end_ts)].shape[0]
    
    avg_metric = df_dash[coluna_ativa].mean() if not df_dash.empty else 0

    k1.metric("👤 Headcount Atual", f"{current_hc}")
    k2.metric("🟢 Admissões (Período)", f"{total_adm}")
    k3.metric("🔴 Desligamentos (Período)", f"{total_des}")
    k4.metric(f"📊 {nome_metrica} Médio (%)", f"{avg_metric:.2f}%")

    # --- LÓGICA DINÂMICA DE ANOS ---
    ano_atual = datetime.now().year
    ano_anterior = ano_atual - 1
    ano_retrasado = ano_atual - 2
    
    st.markdown(f"## 🚀 Planejamento {ano_atual}")

    col_graf, col_txt = st.columns([2.5, 1])

    with col_graf:
        setores = ["Administrativo", "Comercial", "Operacional"]
        data_metas = []
        for s in setores:
            df_s = df_filtered[df_filtered['nomdep'].str.contains(s, na=False, case=False)]
            
            # Cálculo dinâmico para o ano retrasado (Ex: 2024 se hoje for 2026)
            v_retrasado = get_metrics(df_s, pd.to_datetime(f"{ano_retrasado}-01-01"), pd.to_datetime(f"{ano_retrasado}-12-31"))
            v_retrasado = v_retrasado[coluna_ativa].mean() if not v_retrasado.empty else 0
            
            # Cálculo dinâmico para o ano anterior (Ex: 2025 se hoje for 2026)
            v_anterior = get_metrics(df_s, pd.to_datetime(f"{ano_anterior}-01-01"), pd.to_datetime(f"{ano_anterior}-12-31"))
            v_anterior = v_anterior[coluna_ativa].mean() if not v_anterior.empty else 0

            data_metas.append({"Setor": s, "Ano": str(ano_retrasado), "Valor": round(v_retrasado, 1)})
            data_metas.append({"Setor": s, "Ano": str(ano_anterior), "Valor": round(v_anterior, 1)})
            data_metas.append({"Setor": s, "Ano": f"Meta {ano_atual}", "Valor": 5.0})

        # Cores dinâmicas
        cores_map = {
            str(ano_retrasado): "#4A708B", 
            str(ano_anterior): "#36a2eb", 
            f"Meta {ano_atual}": "#f39c12"
        }

        fig_metas = px.bar(pd.DataFrame(data_metas), x="Setor", y="Valor", color="Ano", barmode="group", text="Valor",
                           color_discrete_map=cores_map)
        fig_metas.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=380, margin=dict(t=10))
        st.plotly_chart(fig_metas, width='stretch')

    with col_txt:
        st.markdown("<br>", unsafe_allow_html=True)
        for s in setores:
            # Busca o valor do ano anterior dinamicamente
            val_anterior = next((x['Valor'] for x in data_metas if x['Setor'] == s and x['Ano'] == str(ano_anterior)), 0)
            dist = val_anterior - 5.0
            cor = "#2ecc71" if dist <= 0 else "#e74c3c"
            st.markdown(f"""
                <div class="linha-meta">
                    <span style="color:#B0C4DE; font-size:14px;">{s}</span>
                    <span style="font-weight:bold; color:white;">5.0%</span>
                </div>
                <div style="color:{cor}; font-size:12px; font-weight:bold; margin-top:-10px; margin-bottom:15px;">
                    Distância da Meta: {dist:+.2f} pp | <br>     Valor {ano_anterior}: {val_anterior:.1f}%
                </div>
            """, unsafe_allow_html=True)

    st.divider()

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 🚻 Proporção por Gênero")
        df_des = df_filtered[df_filtered['demissao'].notna()].copy()
        if not df_des.empty:
            df_des['sexo'] = df_des['sexo'].map({'M': 'Masculino', 'F': 'Feminino'}).fillna(df_des['sexo'])
            fig_gen = px.pie(df_des, names='sexo', hole=0.6, color_discrete_sequence=["#36a2eb", "#FF00DD", "#ffe600"])
            fig_gen.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', height=350)
            st.plotly_chart(fig_gen, width='stretch')

    with c2:
        st.markdown("### ⏳ Turnover por Tempo de Empresa")
        if not df_des.empty:
            df_des['dias'] = (df_des['demissao'] - df_des['admissao']).dt.days
            df_des = df_des.copy()
            df_des['Faixa'] = pd.cut(df_des['dias'], bins=[0, 180, 365, 730, 99999], labels=['0-6m', '6-12m', '1-2a', '2a+'])
            counts = df_des['Faixa'].value_counts().reindex(['0-6m', '6-12m', '1-2a', '2a+'], fill_value=0).reset_index()
            counts.columns = ['Faixa', 'count']
            # Alterna entre azul e laranja
            cores_alternadas = ['#36a2eb', '#f39c12', '#36a2eb', '#f39c12']
            fig_faixa = px.bar(counts, x='count', y='Faixa', orientation='h', color='Faixa', color_discrete_sequence=cores_alternadas)
            fig_faixa.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', height=350, showlegend=False)
            st.plotly_chart(fig_faixa, width='stretch')

    st.divider()

    st.markdown("### 📋 Detalhamento Mensal")
    st.dataframe(df_dash.sort_values(by="Data", ascending=False), width='stretch', hide_index=True,
                 column_order=("Mês", "Headcount", "Desligamentos", coluna_ativa, "Meta"),
                 column_config={coluna_ativa: st.column_config.ProgressColumn(f"{nome_metrica} (%)", format="%.2f%%", min_value=0, max_value=15)})

    st.divider()

    st.subheader("📈 Evolução do Headcount")
    fig_hc = px.line(df_dash, x='Mês', y='Headcount', markers=True, template="plotly_dark")
    st.plotly_chart(fig_hc, width='stretch')

    st.subheader("📊 Comparativo de Admissões vs Desligamentos")
    adm_mes_list = []
    for d in pd.date_range(start=start_ts, end=end_ts, freq='MS'):
        m_end = d + pd.offsets.MonthEnd(0)
        adm = df_filtered[(df_filtered['admissao'] >= d) & (df_filtered['admissao'] <= m_end)].shape[0]
        adm_mes_list.append(adm)
    
    fig_comp = go.Figure(data=[
        go.Bar(name='Admissões', x=df_dash['Mês'], y=adm_mes_list, marker_color='#2ecc71'),
        go.Bar(name='Desligamentos', x=df_dash['Mês'], y=df_dash['Desligamentos'], marker_color='#e74c3c')
    ])
    fig_comp.update_layout(barmode='group', template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_comp, width='stretch')

elif opcao_painel == "Detalhamento por Ano":
    st.title("📅 Detalhamento por Ano")
    for ano in range(start_ts.year, end_ts.year + 1):
        st.subheader(f"Ano {ano}")
        df_ano_adm = df_filtered[df_filtered["admissao"].dt.year == ano]
        df_ano_dem = df_filtered[df_filtered["demissao"].dt.year == ano]
        meses = list(range(1, 13))
        a_m = df_ano_adm.groupby(df_ano_adm["admissao"].dt.month).size().reindex(meses, fill_value=0)
        d_m = df_ano_dem.groupby(df_ano_dem["demissao"].dt.month).size().reindex(meses, fill_value=0)
        df_ano_plot = pd.DataFrame({"Mes": meses, "Admissões": a_m.values, "Desligamentos": d_m.values}).melt(id_vars="Mes")
        chart = alt.Chart(df_ano_plot).mark_bar().encode(
            x="Mes:O", y="value:Q", color=alt.Color("variable:N", scale=alt.Scale(range=["#2ecc71", "#e74c3c"])), xOffset="variable:N"
        ).properties(height=300)
        st.altair_chart(chart, width='stretch')

st.markdown("### 👥 Lista de Colaboradores")


# 1. Cria a cópia de visualização
df_view = df_filtered[['nomfun','empregis', 'nomcid', 'nomdep', 'nomefuncao','nomegerente', 'dessetordesp', 'admissao', 'demissao']].copy()

# 2. Formata as datas para texto (DD/MM/AAAA)
df_view['admissao'] = df_view['admissao'].dt.strftime('%d/%m/%Y')
df_view['demissao'] = df_view['demissao'].dt.strftime('%d/%m/%Y')

# 3. REGRA ESPECÍFICA: Na coluna 'demissao', nulo vira VAZIO
df_view['demissao'] = df_view['demissao'].fillna('').replace('None', '')

# 4. REGRA GERAL: Nos outros campos, nulo vira "Não cadastrado"
# (Como já tratamos a demissão acima, ela não será afetada por essa linha)
df_view = df_view.fillna('Não cadastrado').replace('None', 'Não cadastrado')

# 5. Exibe
st.dataframe(
    df_view.rename(columns={
        'nomfun': 'Funcionário',
        'empregis': 'Empresa Registro',
        'nomcid': 'Cidade',
        'nomdep': 'Departamento',
        'nomefuncao': 'Cargo',
        'nomegerente': 'Gerente',
        'dessetordesp': 'Centro de Custo',
        'admissao': 'Data Admissão',
        'demissao': 'Data Demissão'
    }),
    width='stretch'

)
