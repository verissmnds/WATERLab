import streamlit as st
import pandas as pd
import datetime
import json

# Tenta importar gspread e google credentials, mas previne falhas se não instalados
try:
    import gspread
    from google.oauth2.service_account import Credentials
    HAS_GSPREAD = True
except ImportError:
    HAS_GSPREAD = False

# Configuração de Página com Tema
st.set_page_config(
    page_title="Workshop WaterLAB",
    page_icon="💧",
    layout="centered"
)

# Estilização CSS Customizada (Cores FGV/WaterLab e Fonte Gotham/Montserrat)
st.markdown("""
    <style>
        /* Importar fonte Montserrat do Google Fonts como fallback para Gotham */
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800&display=swap');
        
        * {
            font-family: 'Gotham', 'Montserrat', 'Helvetica Neue', sans-serif;
        }

        /* Estilo geral do fundo */
        .main {
            background-color: #f4f7f9;
        }
        
        /* Cabeçalho Premium com as cores da paleta */
        .header-container {
            background: linear-gradient(135deg, #003B73 0%, #0082c8 100%);
            padding: 30px;
            border-radius: 20px;
            color: white;
            text-align: center;
            margin-bottom: 30px;
            box-shadow: 0 10px 25px rgba(0, 59, 115, 0.15);
        }
        
        .header-title {
            font-size: 2.5rem;
            font-weight: 800;
            margin-bottom: 5px;
            letter-spacing: -0.5px;
        }
        
        .header-subtitle {
            font-size: 1.1rem;
            font-weight: 300;
            opacity: 0.9;
        }

        /* Cartões explicativos das dinâmicas */
        .info-card {
            background-color: #ffffff;
            border-left: 5px solid #0082c8;
            padding: 15px 20px;
            border-radius: 12px;
            margin-bottom: 25px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        }
        
        .info-card-title {
            font-weight: 600;
            color: #003B73;
            margin-bottom: 5px;
            font-size: 1.1rem;
        }
        
        .info-card-desc {
            font-size: 0.95rem;
            color: #555555;
            line-height: 1.4;
        }

        /* Estilização para inputs e botões padrão do Streamlit */
        .stButton>button {
            background: linear-gradient(135deg, #0082c8 0%, #003B73 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 10px !important;
            padding: 12px 28px !important;
            font-weight: 600 !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 15px rgba(0, 59, 115, 0.2) !important;
        }
        
        .stButton>button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 6px 20px rgba(0, 59, 115, 0.3) !important;
        }
        
        /* Ajustar a sidebar com tons claros de gelo/cinza */
        section[data-testid="stSidebar"] {
            background-color: #e6ecf2 !important;
        }
        
        /* Centralizar botões de submit */
        .submit-btn-container {
            text-align: right;
            margin-top: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# --- FUNÇÕES DE CONEXÃO COM GOOGLE SHEETS ---

def get_gspread_client():
    if not HAS_GSPREAD:
        return None
    try:
        # Tenta carregar as credenciais a partir de st.secrets["gspread"]
        if "gspread" not in st.secrets:
            return None
        
        creds_info = dict(st.secrets["gspread"])
        
        # Corrige possíveis quebras de linha na chave privada
        if "private_key" in creds_info:
            creds_info["private_key"] = creds_info["private_key"].replace("\\n", "\n")
            
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        creds = Credentials.from_service_account_info(creds_info, scopes=scopes)
        return gspread.authorize(creds)
    except Exception as e:
        st.sidebar.error(f"Erro na autenticação do Google Sheets: {e}")
        return None

def append_to_sheet(sheet_name, row_data):
    """Adiciona uma linha na aba especificada da planilha do Google Sheets."""
    client = get_gspread_client()
    
    # Se não houver conexão configurada, exibe modo demonstração
    if client is None:
        st.warning("⚠️ **Modo de Demonstração Ativo:** O site não está conectado ao Google Sheets. Suas respostas não foram salvas na nuvem, mas você pode visualizá-las abaixo:")
        st.json(row_data)
        return True
        
    try:
        # Busca a URL da planilha nos segredos
        spreadsheet_url = st.secrets["gspread"].get("spreadsheet_url")
        if not spreadsheet_url:
            st.error("Chave 'spreadsheet_url' não configurada nos segredos.")
            return False
            
        sheet = client.open_by_url(spreadsheet_url)
        
        # Tenta abrir a aba correspondente
        try:
            worksheet = sheet.worksheet(sheet_name)
        except gspread.exceptions.WorksheetNotFound:
            # Se a aba não existir, tenta criar
            worksheet = sheet.add_worksheet(title=sheet_name, rows="100", cols="20")
            # Adiciona o cabeçalho
            worksheet.append_row(list(row_data.keys()))
            
        # Adiciona os dados na planilha
        worksheet.append_row(list(row_data.values()))
        return True
    except Exception as e:
        st.error(f"Erro ao salvar na planilha: {e}")
        # Exibe os dados para o usuário não perdê-los em caso de erro de conexão
        st.info("Aqui estão os dados que você preencheu:")
        st.json(row_data)
        return False

# --- EXIBIÇÃO DE LOGOS (TOP) ---
col_logo1, col_logo2 = st.columns([1.2, 1])
with col_logo1:
    st.image("water_lab_logo.png", use_container_width=True)
with col_logo2:
    st.image("fgv_ceri_logo.png", use_container_width=True)

# --- CABEÇALHO DO SITE ---
st.markdown("""
    <div class="header-container" style="margin-top: 10px; padding: 20px 15px;">
        <div class="header-title" style="font-size: 1.45rem; margin: 0; font-weight: 600; line-height: 1.4;">
            Plataforma Virtual do Workshop WaterLab para Coleta de Respostas
        </div>
    </div>
""", unsafe_allow_html=True)

# Menu de seleção das Dinâmicas
st.sidebar.title("Navegação")
opcao_dinamica = st.sidebar.radio(
    "Escolha a Dinâmica para Responder:",
    [
        "01. Mural 'O que te surpreendeu?'",
        "02. Canvas de Barreira por Persona",
        "03. Folha de Brainwriting",
        "04. Matriz: ideias × segmentos",
        "05. Filtro Ético",
        "06. Matriz: impacto × viabilidade",
        "07. Canvas de Desenho de Intervenção"
    ]
)

timestamp_atual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# =====================================================================
# 1. MURAL "O QUE TE SURPREENDEU?"
# =====================================================================
if opcao_dinamica == "01. Mural 'O que te surpreendeu?'":
    st.markdown("""
        <div class="info-card">
            <div class="info-card-title">01. Mural “O que te surpreendeu?”</div>
            <div class="info-card-desc">
                <b>Como usar:</b> Escreva sua percepção para cada coluna abaixo. 
                Utilize este formulário para registrar o que mais chamou sua atenção no início das atividades.
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("form_mural_surpresa", clear_on_submit=True):
        col_nome = st.text_input("Nome do Participante ou Grupo:", placeholder="Ex: Grupo Azul / Ana Silva")
        
        st.subheader("Suas percepções:")
        campo_1 = st.text_area("1. O dado ou a fala que mais me surpreendeu:", placeholder="Digite aqui...")
        campo_2 = st.text_area("2. O que isso muda no jeito como vejo o cliente:", placeholder="Digite aqui...")
        campo_3 = st.text_area("3. Uma dúvida que ficou no ar:", placeholder="Digite aqui...")
        
        submitted = st.form_submit_button("Enviar Resposta")
        if submitted:
            if not col_nome or not campo_1 or not campo_2 or not campo_3:
                st.error("Por favor, preencha todos os campos antes de enviar!")
            else:
                dados = {
                    "Timestamp": timestamp_atual,
                    "Participante/Grupo": col_nome,
                    "Dado/Fala Surpreendente": campo_1,
                    "Mudanca Visao Cliente": campo_2,
                    "Duvida no Ar": campo_3
                }
                
                with st.spinner("Enviando resposta..."):
                    sucesso = append_to_sheet("01_Mural_Surpresa", dados)
                    if sucesso:
                        st.success("🎉 Resposta enviada com sucesso!")
                        st.balloons()

# =====================================================================
# 2. CANVAS DE BARREIRA POR PERSONA
# =====================================================================
elif opcao_dinamica == "02. Canvas de Barreira por Persona":
    st.markdown("""
        <div class="info-card">
            <div class="info-card-title">02. Canvas de Barreira por Persona</div>
            <div class="info-card-desc">
                <b>Como usar:</b> 1 cópia por persona. Preencham com base em quem atende o cliente no dia a dia.
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("form_canvas_barreiras", clear_on_submit=True):
        col_grupo = st.text_input("Nome do Grupo:", placeholder="Ex: Grupo Verde")
        
        col_persona = st.selectbox(
            "Selecione a Persona sob análise:",
            ["Conservadora", "Desbravadora", "Confortável", "Apático"]
        )
        
        col_bate_cliente = st.radio(
            "Esta persona bate com o cliente que você atende?",
            ["Sim", "Em parte", "Não"]
        )
        
        col_ajustes = st.text_area(
            "Se selecionou 'Em parte' ou 'Não', descreva os ajustes necessários:", 
            placeholder="O que difere no seu dia a dia?..."
        )
        
        st.subheader("Mapa de Empatia Rápido")
        st.info("Observe esta persona pelos olhos de quem a atende")
        
        col_pensa_sente = st.text_area(
            "Pensa e sente:", 
            placeholder="Crenças sobre a água, a conta e a empresa; o que a preocupa..."
        )
        col_fala_faz = st.text_area(
            "Fala e faz:", 
            placeholder="O que diz e como age hoje (paga? reclama? evita? gambiarra?)..."
        )
        col_dores_medos = st.text_area(
            "Dores / medos:", 
            placeholder="O que trava, frustra ou assusta na hora de aderir e pagar..."
        )
        col_ganhos_desejos = st.text_area(
            "Ganhos / o que deseja:", 
            placeholder="O que faria valer a pena pagar; o que ela quer da vida e do bairro..."
        )
        
        col_barreira_dominante = st.selectbox(
            "Barreira dominante (marque a principal):",
            [
                "1. Não lembra / não prioriza",
                "2. Não consegue pagar",
                "3. Não confia / não quer"
            ]
        )
        
        col_empresa_trava = st.text_area(
            "Onde a empresa trava (processo, canal, sistema):", 
            placeholder="Ex: cliente sem comprovante de residência; sem canal de contato..."
        )
        
        submitted = st.form_submit_button("Enviar Canvas de Barreira")
        if submitted:
            if not col_grupo:
                st.error("Por favor, informe o nome do grupo!")
            else:
                dados = {
                    "Timestamp": timestamp_atual,
                    "Grupo": col_grupo,
                    "Persona": col_persona,
                    "Bate com Cliente": col_bate_cliente,
                    "Ajustes": col_ajustes,
                    "Pensa e Sente": col_pensa_sente,
                    "Fala e Faz": col_fala_faz,
                    "Dores e Medos": col_dores_medos,
                    "Ganhos e Desejos": col_ganhos_desejos,
                    "Barreira Dominante": col_barreira_dominante,
                    "Onde a Empresa Trava": col_empresa_trava
                }
                
                with st.spinner("Enviando dados..."):
                    sucesso = append_to_sheet("03_Canvas_Barreiras", dados)
                    if sucesso:
                        st.success("🎉 Canvas enviado com sucesso!")
                        st.balloons()

# =====================================================================
# 3. FOLHA DE BRAINWRITING
# =====================================================================
elif opcao_dinamica == "03. Folha de Brainwriting":
    st.markdown("""
        <div class="info-card">
            <div class="info-card-title">03. Folha de Brainwriting</div>
            <div class="info-card-desc">
                <b>Como usar:</b> Digite o desafio em foco e registre as ideias geradas pelo grupo.
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("form_brainwriting", clear_on_submit=True):
        col_grupo = st.text_input("Nome do Grupo/Mesa:", placeholder="Ex: Grupo 3")
        col_desafio = st.text_input("Desafio / segmento foco desta folha:", placeholder="Ex: Como fazer a Desbravadora aderir e pagar?")
        
        st.subheader("Geração de Ideias:")
        col_ideia1 = st.text_area("Ideia 1:", placeholder="Descreva a primeira ideia...")
        col_ideia2 = st.text_area("Ideia 2:", placeholder="Descreva a segunda ideia...")
        col_ideia3 = st.text_area("Ideia 3:", placeholder="Descreva a terceira ideia...")
        
        submitted = st.form_submit_button("Enviar Rodada de Ideias")
        if submitted:
            if not col_grupo or not col_desafio or (not col_ideia1 and not col_ideia2 and not col_ideia3):
                st.error("Preencha o grupo, o desafio e pelo menos uma ideia!")
            else:
                dados = {
                    "Timestamp": timestamp_atual,
                    "Grupo": col_grupo,
                    "Desafio Foco": col_desafio,
                    "Ideia 1": col_ideia1,
                    "Ideia 2": col_ideia2,
                    "Ideia 3": col_ideia3
                }
                
                with st.spinner("Gravando ideias..."):
                    sucesso = append_to_sheet("04_Brainwriting", dados)
                    if sucesso:
                        st.success("🎉 Ideias de Brainwriting salvas com sucesso!")
                        st.balloons()

# =====================================================================
# 4. MATRIZ: IDEIAS × SEGMENTOS
# =====================================================================
elif opcao_dinamica == "04. Matriz: ideias × segmentos":
    st.markdown("""
        <div class="info-card">
            <div class="info-card-title">04. Matriz: ideias × segmentos</div>
            <div class="info-card-desc">
                <b>Como usar:</b> Descreva uma ideia e marque para quais segmentos de personas ela se aplica. 
                Isso ajuda a identificar lacunas em conjunto.
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("form_matriz_segmentos", clear_on_submit=True):
        col_grupo = st.text_input("Nome do Grupo:", placeholder="Ex: Grupo Alpha")
        col_ideia = st.text_area("Ideia / Hipótese sob análise:", placeholder="Descreva a proposta...")
        
        st.write("Marque os segmentos (personas) atendidos por esta ideia:")
        persona_conservadora = st.checkbox("Conservadora")
        persona_desbravadora = st.checkbox("Desbravadora")
        persona_confortavel = st.checkbox("Confortável")
        persona_apatico = st.checkbox("Apático")
        
        submitted = st.form_submit_button("Registrar na Matriz")
        if submitted:
            if not col_grupo or not col_ideia:
                st.error("Preencha o nome do grupo e a ideia!")
            else:
                # Gera lista de segmentos marcados
                segmentos_selecionados = []
                if persona_conservadora: segmentos_selecionados.append("Conservadora")
                if persona_desbravadora: segmentos_selecionados.append("Desbravadora")
                if persona_confortavel: segmentos_selecionados.append("Confortável")
                if persona_apatico: segmentos_selecionados.append("Apático")
                
                dados = {
                    "Timestamp": timestamp_atual,
                    "Grupo": col_grupo,
                    "Ideia/Hipótese": col_ideia,
                    "Segmentos Relacionados": ", ".join(segmentos_selecionados) if segmentos_selecionados else "Nenhum"
                }
                
                with st.spinner("Registrando..."):
                    sucesso = append_to_sheet("05_Matriz_Ideias", dados)
                    if sucesso:
                        st.success("🎉 Item registrado na Matriz!")
                        st.balloons()

# =====================================================================
# 5. FILTRO ÉTICO
# =====================================================================
elif opcao_dinamica == "05. Filtro Ético":
    st.markdown("""
        <div class="info-card">
            <div class="info-card-title">05. Filtro Ético</div>
            <div class="info-card-desc">
                <b>Como usar:</b> Cada hipótese deve passar por este filtro antes da votação final. 
                Se 'travar' em alguma resposta ética, a proposta deve ser ajustada ou descartada.
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("form_filtro_etico", clear_on_submit=True):
        col_grupo = st.text_input("Grupo / Nome da Hipótese:", placeholder="Ex: Equipe Beta - Campanha Nudge SMS")
        
        st.subheader("Análise Ética:")
        pergunta_1 = st.text_area(
            "1. Esta hipótese amplia uma capacidade do cliente, ou explora uma vulnerabilidade dele?",
            placeholder="Responda detalhadamente..."
        )
        pergunta_2 = st.text_area(
            "2. Se o cliente soubesse exatamente o que estamos fazendo, ele se sentiria respeitado?",
            placeholder="Responda detalhadamente..."
        )
        
        col_decisao = st.radio(
            "Decisão Coletiva:",
            ["Passa", "Ajustar", "Descartar"]
        )
        
        submitted = st.form_submit_button("Submeter Filtro Ético")
        if submitted:
            if not col_grupo or not pergunta_1 or not pergunta_2:
                st.error("Por favor, preencha todos os campos do formulário!")
            else:
                dados = {
                    "Timestamp": timestamp_atual,
                    "Grupo/Hipótese": col_grupo,
                    "Capacidade vs Vulnerabilidade": pergunta_1,
                    "Respeito ao Cliente": pergunta_2,
                    "Decisao Final": col_decisao
                }
                
                with st.spinner("Salvando decisão..."):
                    sucesso = append_to_sheet("07_Filtro_Etico", dados)
                    if sucesso:
                        st.success(f"🎉 Análise Ética registrada como: **{col_decisao}**!")
                        st.balloons()

# =====================================================================
# 6. MATRIZ: IMPACTO × VIABILIDADE
# =====================================================================
elif opcao_dinamica == "06. Matriz: impacto × viabilidade":
    st.markdown("""
        <div class="info-card">
            <div class="info-card-title">06. Matriz: impacto × viabilidade</div>
            <div class="info-card-desc">
                <b>Como usar:</b> Insira o nome do grupo e a hipótese analisada, e selecione manualmente as classificações decididas pelo grupo.
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("form_impacto_viabilidade", clear_on_submit=True):
        col_grupo = st.text_input("Grupo / Nome da Hipótese:", placeholder="Ex: Grupo Sul - Canal Simplificado")
        
        col_impacto = st.selectbox("Nível de IMPACTO esperado:", ["Alto", "Baixo"])
        col_viabilidade = st.selectbox("Nível de VIABILIDADE técnica/operacional:", ["Alta", "Baixa"])
        
        col_quadrante = st.selectbox(
            "Quadrante Escolhido pelo Grupo:",
            [
                "Fazer já (pilotos prioritários)",
                "Vale o esforço (quebrar a barreira de viabilidade)",
                "Ganhos rápidos (fazer se sobrar fôlego)",
                "Descartar / depois"
            ]
        )
        
        col_justificativa = st.text_area("Justificativa / Comentários adicionais (opcional):", placeholder="Por que o grupo escolheu este quadrante?...")
        
        submitted = st.form_submit_button("Registrar na Matriz")
        
        if submitted:
            if not col_grupo:
                st.error("Informe o nome da hipótese ou grupo!")
            else:
                dados = {
                    "Timestamp": timestamp_atual,
                    "Grupo/Hipotese": col_grupo,
                    "Impacto": col_impacto,
                    "Viabilidade": col_viabilidade,
                    "Quadrante Classificado": col_quadrante,
                    "Justificativa/Comentarios": col_justificativa
                }
                
                with st.spinner("Registrando classificação..."):
                    sucesso = append_to_sheet("08_Impacto_Viabilidade", dados)
                    if sucesso:
                        st.success(f"🎉 Registrado! Quadrante: **{col_quadrante}**")
                        st.balloons()

# =====================================================================
# 7. CANVAS DE DESENHO DE INTERVENÇÃO
# =====================================================================
elif opcao_dinamica == "07. Canvas de Desenho de Intervenção":
    st.markdown("""
        <div class="info-card">
            <div class="info-card-title">07. Canvas de Desenho de Intervenção</div>
            <div class="info-card-desc">
                <b>Como usar:</b> 1 canvas por hipótese prioritária. Detalhem a proposta para transformá-la em piloto.
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    with st.form("form_desenho_intervencao", clear_on_submit=True):
        col_grupo = st.text_input("Nome do Grupo:", placeholder="Ex: Grupo 1")
        col_hipotese = st.text_input("Hipótese (nome curto):", placeholder="Ex: Nudge de Vizinhança no boleto")
        
        col_persona = st.text_input("Persona-alvo:", placeholder="Ex: Conservadora / Apático")
        col_barreira = st.text_input("Barreira que ataca:", placeholder="Ex: Não lembra de pagar")
        col_comportamento = st.text_input("Comportamento-alvo (o que queremos que a pessoa faça):", placeholder="Ex: Pagar antes do vencimento")
        
        col_intervencao = st.text_input("A intervenção, em 1 frase:", placeholder="Ex: Enviar um SMS reforçando o ganho social na véspera")
        
        st.write("Alavancas EAST aplicadas (marque as que se aplicam):")
        col1, col2, col3, col4 = st.columns(4)
        with col1: east_f = st.checkbox("Fácil")
        with col2: east_a = st.checkbox("Atrativo")
        with col3: east_s = st.checkbox("Social")
        with col4: east_o = st.checkbox("Oportuno")
        
        col_canal_msg = st.text_area(
            "Canal + mensagem-rascunho (texto real):",
            placeholder="Ex: SMS: 'Sua água de junho está pronta. Sabia que 90% dos seus vizinhos já pagaram?'"
        )
        
        col_testar = st.text_input("Com quem testar (público + tamanho):", placeholder="Ex: 50 pessoas da persona Confortável")
        col_sucesso = st.text_area("Como saber se deu certo (métrica · meta · prazo):", placeholder="Ex: Redução de 10% na inadimplência em 30 dias")
        col_responsavel = st.text_input("Responsável + próximo passo (com data):", placeholder="Ex: Carlos - programar disparos até 20/07")
        
        submitted = st.form_submit_button("Enviar Desenho de Intervenção")
        if submitted:
            if not col_grupo or not col_hipotese:
                st.error("Os campos Grupo e Hipótese são obrigatórios!")
            else:
                # Une as alavancas EAST selecionadas
                alavancas = []
                if east_f: alavancas.append("Fácil")
                if east_a: alavancas.append("Atrativo")
                if east_s: alavancas.append("Social")
                if east_o: alavancas.append("Oportuno")
                
                dados = {
                    "Timestamp": timestamp_atual,
                    "Grupo": col_grupo,
                    "Hipotese": col_hipotese,
                    "Persona-Alvo": col_persona,
                    "Barreira Atacada": col_barreira,
                    "Comportamento-Alvo": col_comportamento,
                    "Intervencao 1 Frase": col_intervencao,
                    "Alavancas EAST": ", ".join(alavancas) if alavancas else "Nenhuma",
                    "Canal e Mensagem Rascunho": col_canal_msg,
                    "Publico e Tamanho Teste": col_testar,
                    "Metrica/Meta/Prazo Sucesso": col_sucesso,
                    "Responsavel e Proximo Passo": col_responsavel
                }
                
                with st.spinner("Enviando desenho..."):
                    sucesso = append_to_sheet("09_Desenho_Intervencao", dados)
                    if sucesso:
                        st.success("🎉 Canvas de Desenho de Intervenção enviado com sucesso!")
                        st.balloons()

# --- RODAPÉ DE CRÉDITOS ---
st.markdown("""
    <hr style="border: 0.5px solid #dddddd; margin-top: 50px; margin-bottom: 20px;">
    <div style="text-align: center; color: #555555; font-size: 0.85rem; padding-bottom: 20px;">
        Aplicação desenvolvida por <b>Bruna Verissimo</b>, última atualização 15 de julho de 2026.
    </div>
""", unsafe_allow_html=True)
