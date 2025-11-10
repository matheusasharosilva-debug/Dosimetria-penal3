import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.title("⚖️ Simulador de Dosimetria da Pena - CORRIGIDO")
st.write("**Calculadora completa da dosimetria penal conforme Art. 68 do CP**")

# Upload do arquivo
uploaded_file = st.file_uploader("Faça upload do arquivo crimes_cp_final_sem_art68.csv", type=["csv"])

@st.cache_data
def processar_dados_crimes(df):
    """Processa os dados dos crimes para o formato necessário"""
    if df.empty:
        return {}
        
    crimes_dict = {}
    
    for idx, row in df.iterrows():
        artigo_base = row['Artigo_Base'] if pd.notna(row['Artigo_Base']) else ''
        artigo_completo = row['Artigo_Completo'] if pd.notna(row['Artigo_Completo']) else artigo_base
        descricao = row['Descricao_Crime'] if pd.notna(row['Descricao_Crime']) else ''
        pena_min_valor = row['Pena_Minima_Valor'] if pd.notna(row['Pena_Minima_Valor']) else 0
        pena_min_unidade = row['Pena_Minima_Unidade'] if pd.notna(row['Pena_Minima_Unidade']) else 'mês'
        pena_max_valor = row['Pena_Maxima_Valor'] if pd.notna(row['Pena_Maxima_Valor']) else 0
        pena_max_unidade = row['Pena_Maxima_Unidade'] if pd.notna(row['Pena_Maxima_Unidade']) else 'mês'
        tipo_penal = row['Tipo_Penal_Estrutural'] if pd.notna(row['Tipo_Penal_Estrutural']) else 'Crime Base (Caput)'
        
        # Converter para anos
        if pena_min_unidade == 'mês':
            pena_min_anos = pena_min_valor / 12
        elif pena_min_unidade == 'dia':
            pena_min_anos = pena_min_valor / 360
        else:
            pena_min_anos = pena_min_valor
            
        if pena_max_unidade == 'mês':
            pena_max_anos = pena_max_valor / 12
        elif pena_max_unidade == 'dia':
            pena_max_anos = pena_max_valor / 360
        else:
            pena_max_anos = pena_max_valor
        
        # Criar chave única para o crime
        if pd.notna(artigo_completo) and pd.notna(descricao):
            chave = f"{artigo_completo} - {descricao[:80]}..."
            crimes_dict[chave] = {
                'artigo': artigo_completo,
                'artigo_base': artigo_base,
                'descricao_completa': descricao,
                'pena_min': pena_min_anos,
                'pena_max': pena_max_anos,
                'tipo_penal': tipo_penal,
                'pena_min_original': pena_min_valor,
                'pena_max_original': pena_max_valor,
                'unidade_original': pena_min_unidade
            }
    
    return crimes_dict

# Carregar dados baseado no upload
df = pd.DataFrame()
crimes_data = {}

if uploaded_file is not None:
    try:
        # Tenta diferentes codificações
        codificacoes = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252', 'utf-8-sig']
        
        for encoding in codificacoes:
            try:
                uploaded_file.seek(0)  # Reset file pointer
                df = pd.read_csv(uploaded_file, encoding=encoding)
                st.success(f"✅ Dados carregados com sucesso! (Codificação: {encoding})")
                crimes_data = processar_dados_crimes(df)
                break
            except (UnicodeDecodeError, pd.errors.EmptyDataError):
                continue
        else:
            # Se nenhuma codificação funcionou, tenta com engine python
            try:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, encoding='latin-1', engine='python')
                st.success("✅ Dados carregados com engine python")
                crimes_data = processar_dados_crimes(df)
            except Exception as e:
                st.error(f"❌ Erro ao carregar arquivo: {e}")
    except Exception as e:
        st.error(f"❌ Erro inesperado: {e}")
else:
    st.info("📁 Faça upload do arquivo CSV para começar")

# Sidebar
st.sidebar.header("💡 Sobre")
st.sidebar.write("**Base Legal:** Art. 68 do Código Penal - Fases: 1.Pena base 2.Atenuantes/Agravantes 3.Majorantes/Minorantes 4.Cálculo 5.Regime 6.Substituição")
st.sidebar.write(f"**📊 Crimes carregados:** {len(crimes_data)}")

# Busca na sidebar
st.sidebar.write("**🔍 Buscar crime:**")
busca = st.sidebar.text_input("Digite o artigo ou descrição:")

if busca and crimes_data:
    crimes_filtrados = {k: v for k, v in crimes_data.items() if busca.lower() in k.lower()}
    st.sidebar.write(f"**Resultados ({len(crimes_filtrados)}):**")
    for chave in list(crimes_filtrados.keys())[:5]:
        crime_info = crimes_filtrados[chave]
        st.sidebar.write(f"**{crime_info['artigo']}** - Pena: {crime_info['pena_min']:.1f}-{crime_info['pena_max']:.1f} anos")

# Se não há dados carregados, mostrar mensagem
if not crimes_data:
    st.warning("""
    **⚠️ Aguardando upload do dataset**
    
    Para usar o simulador:
    1. **Faça upload do arquivo `crimes_cp_final_sem_art68.csv` acima**
    2. **Ou certifique-se que o arquivo está no repositório GitHub**
    
    O arquivo CSV deve conter as colunas:
    - Artigo_Base, Artigo_Completo, Descricao_Crime
    - Pena_Minima_Valor, Pena_Minima_Unidade
    - Pena_Maxima_Valor, Pena_Maxima_Unidade
    - Tipo_Penal_Estrutural
    """)
    st.stop()

# Fase 1: Pena Base e Circunstâncias - CORRIGIDO CONFORME SÚMULA 231
st.header("1️⃣ Fase 1: Pena Base e Circunstâncias (Art. 59 CP)")
col1, col2 = st.columns([2, 1])

with col1:
    if crimes_data:
        crime_selecionado = st.selectbox("Selecione o Crime:", options=list(crimes_data.keys()), format_func=lambda x: x)
        crime_info = crimes_data[crime_selecionado]
        min_pena = crime_info['pena_min']
        max_pena = crime_info['pena_max']
        
        st.write(f"**Artigo:** {crime_info['artigo']}")
        st.write(f"**Tipo penal:** {crime_info['tipo_penal']}")
        st.write(f"**Descrição:** {crime_info['descricao_completa']}")
        st.write(f"**Pena original:** {crime_info['pena_min_original']} {crime_info['unidade_original']} a {crime_info['pena_max_original']} {crime_info['unidade_original']}")
    else:
        st.error("Erro ao carregar dados dos crimes.")

with col2:
    # CRITÉRIOS DO ART. 59 CP - CORRIGIDO: PENA BASE NÃO PODE SER INFERIOR AO MÍNIMO LEGAL
    st.subheader("Critérios do Art. 59 CP")
    
    culpabilidade = st.select_slider(
        "Culpabilidade:",
        options=["Mínima", "Baixa", "Média", "Alta", "Máxima"]
    )
    
    antecedentes = st.select_slider(
        "Antecedentes:",
        options=["Excelentes", "Bons", "Regulares", "Ruins", "Péssimos"]
    )
    
    conduta_social = st.select_slider(
        "Conduta Social:",
        options=["Exemplar", "Boa", "Regular", "Ruim", "Péssima"]
    )
    
    personalidade = st.select_slider(
        "Personalidade do Agente:",
        options=["Favorável", "Moderada", "Desfavorável"]
    )
    
    # Calcular pena base baseada nos critérios do Art. 59 - CORRIGIDO
    # A pena base deve ficar ENTRE o mínimo e o máximo legal
    fatores = {
        "Culpabilidade": {"Mínima": -0.3, "Baixa": -0.15, "Média": 0, "Alta": 0.15, "Máxima": 0.3},
        "Antecedentes": {"Excelentes": -0.2, "Bons": -0.1, "Regulares": 0, "Ruins": 0.1, "Péssimos": 0.2},
        "Conduta Social": {"Exemplar": -0.15, "Boa": -0.07, "Regular": 0, "Ruim": 0.07, "Péssima": 0.15},
        "Personalidade": {"Favorável": -0.1, "Moderada": 0, "Desfavorável": 0.1}
    }
    
    fator_total = (
        fatores["Culpabilidade"][culpabilidade] +
        fatores["Antecedentes"][antecedentes] +
        fatores["Conduta Social"][conduta_social] +
        fatores["Personalidade"][personalidade]
    )
    
    # CORREÇÃO CRÍTICA: A pena base deve ser calculada dentro da faixa legal
    # Usando o sistema de 3/6 da diferença entre min e max
    diferenca_penas = max_pena - min_pena
    
    # Posição inicial na faixa (50% = pena média)
    posicao_inicial = 0.5
    
    # Ajustar posição baseado nos fatores do Art. 59
    posicao_ajustada = posicao_inicial + (fator_total * 0.3)  # Limitar o ajuste
    posicao_ajustada = max(0, min(1, posicao_ajustada))  # Manter entre 0 e 1
    
    pena_base_ajustada = min_pena + (diferenca_penas * posicao_ajustada)
    
    # GARANTIR que a pena base não seja inferior ao mínimo legal
    pena_base_ajustada = max(min_pena, pena_base_ajustada)
    
    st.write(f"**Pena prevista:** {min_pena:.1f} a {max_pena:.1f} anos")
    st.write(f"**Faixa de variação:** {diferenca_penas:.1f} anos")
    st.write(f"**Posição na faixa:** {posicao_ajustada*100:.1f}%")
    st.write(f"**Ajuste Art. 59:** {fator_total*100:+.1f}%")
    
    # DESTACAR A CORREÇÃO DA SÚMULA 231
    st.success(f"**PENA BASE DEFINITIVA: {pena_base_ajustada:.1f} anos**")
    st.info("**✅ CORRETO:** Pena base dentro dos limites legais conforme Súmula 231 STJ")

# Fase 2: Atenuantes e Agravantes
st.header("2️⃣ Fase 2: Atenuantes e Agravantes Gerais")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🔽 Atenuantes (Art. 65 CP)")
    atenuantes = st.multiselect("Selecione as atenuantes:", [
        "Menor de 21 anos na data do fato", 
        "Maior de 70 anos na data da sentença",
        "Desconhecimento da lei",
        "Motivo de relevante valor social ou moral",
        "Arrependimento espontâneo (minimizar consequências)",
        "Reparação do dano antes do julgamento",
        "Coação a que podia resistir",
        "Ordem de autoridade superior",
        "Violenta emoção por ato injusto da vítima",
        "Confissão espontânea perante autoridade",
        "Influência de multidão em tumulto (sem provocação)"
    ])

with col2:
    st.subheader("🔼 Agravantes (Art. 61 CP)")
    agravantes = st.multiselect("Selecione as agravantes:", [
        "Reincidência",
        "Motivo fútil ou torpe",
        "Facilitar/assegurar execução de outro crime",
        "Traição, emboscada ou dissimulação",
        "Emprego de veneno, fogo, explosivo, tortura",
        "Meio insidioso ou cruel",
        "Perigo comum",
        "Crime contra ascendente, descendente, irmão ou cônjuge",
        "Abuso de autoridade ou relações domésticas",
        "Violência contra a mulher",
        "Abuso de poder ou violação de dever",
        "Crime contra criança, maior de 60 anos, enfermo ou grávida",
        "Ofendido sob proteção imediata da autoridade",
        "Ocorrência durante calamidade pública",
        "Embriaguez preordenada",
        "Nas dependências de instituição de ensino"
    ])

# Agravantes do Art. 62 CP
st.subheader("🔼 Agravantes no Concurso de Pessoas (Art. 62 CP)")
agravantes_concurso = st.multiselect("Selecione as agravantes de concurso:", [
    "Promove/organiza cooperação no crime",
    "Dirige atividade dos demais agentes", 
    "Coage ou induz outrem à execução material",
    "Instiga/determina crime a pessoa sob sua autoridade",
    "Executa crime mediante paga ou promessa de recompensa"
])

# Fase 3: Majorantes e Minorantes
st.header("3️⃣ Fase 3: Causas de Aumento/Diminuição")
majorantes_minorantes_generico = {
    "majorantes": [
        "Uso de arma (1/6 a 1/2)", 
        "Violência grave (1/3 a 2/3)", 
        "Concurso de 2+ pessoas (1/4 a 1/2)", 
        "Restrição à liberdade (1/6 a 1/3)", 
        "Abuso de confiança (1/6 a 1/3)",
        "Aumento por continuidade delitiva (1/6 a 2/3)"
    ],
    "minorantes": [
        "Valor ínfimo (1/6 a 1/3)", 
        "Arrependimento posterior (1/6 a 1/3)", 
        "Circunstâncias atenuantes não previstas (1/6 a 1/3)",
        "Diminuição por confissão (1/6 a 1/3)"
    ]
}

col1, col2 = st.columns(2)
with col1:
    majorantes = st.multiselect("Causas de aumento (majorantes):", majorantes_minorantes_generico["majorantes"])
with col2:
    minorantes = st.multiselect("Causas de diminuição (minorantes):", majorantes_minorantes_generico["minorantes"])

# Fase 4: Cálculo Final - CORRIGIDO PARA RESPEITAR LIMITES LEGAIS
st.header("4️⃣ Fase 4: Cálculo Final da Pena (Art. 68 CP)")

if st.button("🎯 Calcular Pena Definitiva", type="primary"):
    pena_calculada = pena_base_ajustada
    
    st.subheader("📊 Detalhamento do Cálculo")
    calculo_detalhado = f"| Etapa | Valor | Ajuste |\n|-------|-------|---------|\n| **Pena Base Inicial** | {min_pena:.1f} anos | - |\n| **Ajuste Art. 59** | {pena_base_ajustada:.1f} anos | {posicao_ajustada*100:.1f}% da faixa |\n"
    
    # Aplicar atenuantes (Art. 65)
    ajustes_atenuantes = []
    for i, atenuante in enumerate(atenuantes, 1):
        # Atenuantes têm peso variável conforme gravidade
        if "Menor de 21" in atenuante or "Maior de 70" in atenuante:
            reducao = diferenca_penas * (1/6)  # Baseado na diferença, não na pena base
        elif "Confissão espontânea" in atenuante:
            reducao = diferenca_penas * (1/8)
        elif "Reparação do dano" in atenuante:
            reducao = diferenca_penas * (1/5)
        else:
            reducao = diferenca_penas * (1/8)
            
        pena_calculada -= reducao
        ajustes_atenuantes.append(reducao)
        calculo_detalhado += f"| Atenuante {i} | {pena_calculada:.1f} anos | -{reducao:.1f} anos |\n"
    
    # Aplicar agravantes (Art. 61)
    ajustes_agravantes = []
    for i, agravante in enumerate(agravantes, 1):
        # Agravantes têm peso variável conforme gravidade
        if "Reincidência" in agravante:
            aumento = diferenca_penas * (1/4)
        elif "veneno" in agravante.lower() or "tortura" in agravante.lower() or "explosivo" in agravante.lower():
            aumento = diferenca_penas * (1/5)
        elif "criança" in agravante.lower() or "idoso" in agravante.lower() or "grávida" in agravante.lower():
            aumento = diferenca_penas * (1/6)
        else:
            aumento = diferenca_penas * (1/8)
            
        pena_calculada += aumento
        ajustes_agravantes.append(aumento)
        calculo_detalhado += f"| Agravante {i} | {pena_calculada:.1f} anos | +{aumento:.1f} anos |\n"
    
    # Aplicar agravantes de concurso (Art. 62)
    ajustes_agravantes_concurso = []
    for i, agravante_conc in enumerate(agravantes_concurso, 1):
        aumento = diferenca_penas * (1/6)
        pena_calculada += aumento
        ajustes_agravantes_concurso.append(aumento)
        calculo_detalhado += f"| Agravante Concurso {i} | {pena_calculada:.1f} anos | +{aumento:.1f} anos |\n"
    
    # Aplicar majorantes
    ajustes_majorantes = []
    for i, majorante in enumerate(majorantes, 1):
        aumento = diferenca_penas * (1/6)
        pena_calculada += aumento
        ajustes_majorantes.append(aumento)
        calculo_detalhado += f"| Majorante {i} | {pena_calculada:.1f} anos | +{aumento:.1f} anos |\n"
    
    # Aplicar minorantes
    ajustes_minorantes = []
    for i, minorante in enumerate(minorantes, 1):
        reducao = diferenca_penas * (1/6)
        pena_calculada -= reducao
        ajustes_minorantes.append(reducao)
        calculo_detalhado += f"| Minorante {i} | {pena_calculada:.1f} anos | -{reducao:.1f} anos |\n"
    
    # CORREÇÃO CRÍTICA: Aplicar limites legais - NUNCA abaixo do mínimo ou acima do máximo
    pena_final = max(min_pena, min(max_pena, pena_calculada))
    
    # Verificar se houve ajuste por limites
    if pena_calculada < min_pena:
        ajuste_limite = f"⤴️ Ajuste para mínimo legal: +{min_pena - pena_calculada:.1f} anos"
    elif pena_calculada > max_pena:
        ajuste_limite = f"⤵️ Ajuste para máximo legal: -{pena_calculada - max_pena:.1f} anos"
    else:
        ajuste_limite = "✅ Dentro dos limites legais"
    
    calculo_detalhado += f"| **LIMITES LEGAIS** | **{pena_final:.1f} anos** | **{ajuste_limite}** |"
    
    st.markdown(calculo_detalhado)
    
    # ALERTA SOBRE A SÚMULA 231
    if pena_calculada < min_pena:
        st.error("""
        **🚨 ATENÇÃO - SÚMULA 231 STJ:** 
        A pena não pode ser fixada abaixo do mínimo legal! 
        O sistema automaticamente ajustou para o mínimo permitido.
        """)

    # [CONTINUAÇÃO DO CÓDIGO... As demais fases (5, 6, 7) permanecem iguais ao código anterior]
    
    # Fase 5: Tipo de Pena Privativa
    st.header("5️⃣ Fase 5: Tipo de Pena Privativa")
    
    # Determinar tipo de pena (Reclusão ou Detenção)
    tipo_pena_info = crime_info.get('tipo_penal', '')
    if 'Reclusão' in str(tipo_pena_info):
        tipo_pena = "RECLUSÃO"
        cor_tipo_pena = "#ff4444"
        descricao_tipo = "Art. 33 - Regimes: Fechado, Semiaberto ou Aberto"
    elif 'Detenção' in str(tipo_pena_info):
        tipo_pena = "DETENÇÃO" 
        cor_tipo_pena = "#ffaa00"
        descricao_tipo = "Art. 33 - Regimes: Semiaberto ou Aberto (salvo transferência)"
    else:
        tipo_pena = "PENA PRIVATIVA DE LIBERDADE"
        cor_tipo_pena = "#666666"
        descricao_tipo = "Tipo de pena a ser definido conforme a natureza do crime"
    
    st.markdown(f"""
    <div style="background-color: {cor_tipo_pena}20; padding: 15px; border-radius: 10px; border-left: 5px solid {cor_tipo_pena};">
        <h3 style="color: {cor_tipo_pena}; margin: 0;">📋 TIPO DE PENA: {tipo_pena}</h3>
        <p style="margin: 5px 0 0 0;">{descricao_tipo}</p>
    </div>
    """, unsafe_allow_html=True)

    # Fase 6: Regime de Cumprimento
    st.header("6️⃣ Fase 6: Regime de Cumprimento (Art. 33 CP)")
    
    # Verificar reincidência conforme Art. 63-64 CP
    reincidente = "Reincidência" in agravantes
    
    # Determinar regime conforme Art. 33 CP
    if tipo_pena == "RECLUSÃO":
        if pena_final > 8:
            regime = "FECHADO"
            cor_regime = "#ff4444"
            descricao = "Estabelecimento de segurança máxima/média - Art. 33, §2º, a"
            fundamento = "Art. 33, §2º, 'a' - Pena superior a 8 anos"
        elif pena_final > 4:
            if not reincidente:
                regime = "SEMIABERTO"
                cor_regime = "#ffaa00" 
                descricao = "Colônia agrícola, industrial ou similar - Art. 33, §2º, b"
                fundamento = "Art. 33, §2º, 'b' - Não reincidente, pena superior a 4 anos"
            else:
                regime = "FECHADO"
                cor_regime = "#ff4444"
                descricao = "Estabelecimento de segurança máxima/média"
                fundamento = "Art. 33, §2º - Reincidente, pena superior a 4 anos"
        else:
            if not reincidente:
                regime = "ABERTO"
                cor_regime = "#44cc44"
                descricao = "Casa de albergado ou estabelecimento adequado - Art. 33, §2º, c"
                fundamento = "Art. 33, §2º, 'c' - Não reincidente, pena igual/inferior a 4 anos"
            else:
                regime = "SEMIABERTO"
                cor_regime = "#ffaa00"
                descricao = "Colônia agrícola, industrial ou similar"
                fundamento = "Art. 33, §2º - Reincidente, pena igual/inferior a 4 anos"
    
    else:  # DETENÇÃO
        regime = "SEMIABERTO"
        cor_regime = "#ffaa00"
        descricao = "Colônia agrícola, industrial ou similar"
        fundamento = "Art. 33 - Detenção em regime semiaberto ou aberto"
        
        if pena_final <= 4 and not reincidente:
            regime = "ABERTO"
            cor_regime = "#44cc44"
            descricao = "Casa de albergado ou estabelecimento adequado"
            fundamento = "Art. 33 - Detenção: pode iniciar em aberto se pena ≤ 4 anos e não reincidente"
    
    st.markdown(f"""
    <div style="background-color: {cor_regime}20; padding: 20px; border-radius: 10px; border-left: 5px solid {cor_regime};">
        <h2 style="color: {cor_regime}; margin: 0;">🔒 REGIME INICIAL: {regime}</h2>
        <p style="margin: 10px 0 0 0; font-size: 16px;"><strong>{descricao}</strong></p>
        <p style="margin: 5px 0 0 0; font-size: 12px; color: #666;"><em>{fundamento}</em></p>
        <p style="margin: 10px 0 0 0; font-size: 14px;"><strong>Reincidência:</strong> {'SIM' if reincidente else 'NÃO'} (Art. 63-64 CP)</p>
    </div>
    """, unsafe_allow_html=True)

    # Fase 7: Substituição da Pena
    st.header("7️⃣ Fase 7: Substituição por Pena Restritiva de Direitos")
    
    # Verificar condições para substituição (Art. 44 CP)
    pode_substituir = False
    condicoes = []
    
    crime_culposo = "culposo" in crime_info['descricao_completa'].lower()
    
    if pena_final <= 4 or crime_culposo:
        if crime_culposo:
            condicoes.append("✅ Crime CULPOSO - pode substituir independente da pena")
            pode_substituir = True
        else:
            condicoes.append("✅ Pena não superior a 4 anos")
            crimes_violentos = ["homicídio", "lesão corporal", "latrocínio", "estupro", "roubo", "sequestro"]
            crime_violento = any(violento in crime_info['descricao_completa'].lower() for violento in crimes_violentos)
            
            if not crime_violento:
                condicoes.append("✅ Crime sem violência ou grave ameaça")
                pode_substituir = True
            else:
                condicoes.append("❌ Crime com violência ou grave ameaça")
    else:
        condicoes.append("❌ Pena superior a 4 anos e crime doloso")
    
    if not reincidente:
        condicoes.append("✅ Réu não reincidente em crime doloso")
        pode_substituir = pode_substituir and True
    else:
        condicoes.append("❌ Réu reincidente em crime doloso")
        condicoes.append("⚠️ Art. 44, §3º: Juiz pode aplicar se socialmente recomendável")
    
    condicoes.append("✅ Análise dos critérios do Art. 59 CP")
    
    if pode_substituir:
        substituicao = "**CABE SUBSTITUIÇÃO** por pena restritiva de direitos"
        cor_subst = "#44cc44"
        fundamento_subst = "Art. 44 CP - Preenchidos os requisitos legais"
    else:
        substituicao = "**NÃO CABE SUBSTITUIÇÃO**"
        cor_subst = "#ff4444"
        fundamento_subst = "Art. 44 CP - Não preenchidos os requisitos legais"
    
    st.markdown(f"""
    <div style="background-color: {cor_subst}20; padding: 15px; border-radius: 10px; border-left: 5px solid {cor_subst};">
        <h3 style="color: {cor_subst}; margin: 0;">{substituicao}</h3>
        <p style="margin: 5px 0 0 0;">{fundamento_subst}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("**📝 Condições analisadas para substituição (Art. 44 CP):**")
    for condicao in condicoes:
        st.write(condicao)

    # SEÇÃO DE REFERÊNCIAS LEGAIS COM SÚMULA 231
    st.header("📚 Referências Legais e Jurisprudenciais")

    tab1, tab2, tab3, tab4 = st.tabs(["📋 Súmulas", "⚖️ Penas", "🔍 Arts. 59-68", "📊 Progressão"])

    with tab1:
        st.subheader("Súmulas Relevantes STJ")
        st.write("""
        **SÚMULA 231 STJ:**
        > *"É inadmissível a fixação da pena abaixo do mínimo legal, ainda que em decorrência da aplicação de atenuantes."*
        
        **Súmula 444 STJ:**
        > *"A dosimetria da pena deve observar o sistema trifásico do Art. 68 CP, com fundamentação de cada fase."*
        
        **Súmula 145 STJ:**
        > *"A pena-base deve ser fixada entre o mínimo e o máximo abstratamente cominado ao crime."*
        """)

    with tab2:
        st.subheader("Arts. 33-48 CP - Penas")
        st.write("""
        **Art. 33 - Regimes:**
        - Reclusão: Fechado, Semiaberto ou Aberto
        - Detenção: Semiaberto ou Aberto
        
        **Art. 44 - Substituição:**
        - Requisitos cumulativos
        - Pena ≤ 4 anos + sem violência
        - Não reincidente
        - Análise Art. 59
        """)

    with tab3:
        st.subheader("Arts. 59-68 CP - Dosimetria")
        st.write("""
        **Art. 59 - Critérios:**
        - Culpabilidade, antecedentes, conduta social
        - Personalidade, motivos, circunstâncias
        
        **Art. 68 - Fases:**
        1. Pena-base (Art. 59)
        2. Atenuantes/Agravantes
        3. Majorantes/Minorantes
        """)

    with tab4:
        st.subheader("Progressão de Regime")
        st.write("""
        **Regras gerais:**
        - 1/6 da pena no regime anterior
        - 2/5 para crimes hediondos
        - Requer bom comportamento
        - Juízo da Execução Penal
        """)

st.markdown("---")
st.write("**⚖️ Ferramenta educacional - Consulte sempre a legislação atual e um profissional do direito**")
st.write("**📚 Base legal:** Arts. 33, 43-48, 59, 61, 65, 68 do Código Penal Brasileiro")
st.write("**⚡ Correção aplicada:** Respeito ao mínimo legal conforme Súmula 231 STJ")
    # Resumo final estilizado
    st.mark
