import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.title("⚖️ Simulador de Dosimetria da Pena")
st.write("**Calculadora completa da dosimetria penal conforme Art. 68 do CP**")

# Upload do arquivo
uploaded_file = st.file_uploader("Faça upload do arquivo crimes_privacao_liberdade_processado.csv", type=["csv"])

@st.cache_data
def processar_dados_crimes(df):
    """Processa os dados dos crimes para o formato necessário"""
    if df.empty:
        return {}
        
    crimes_dict = {}
    
    for idx, row in df.iterrows():
        # Ajustar para a estrutura do seu CSV
        crime_base = row['Crime_Base'] if 'Crime_Base' in df.columns and pd.notna(row['Crime_Base']) else ''
        artigo = row['Artigo'] if 'Artigo' in df.columns and pd.notna(row['Artigo']) else ''
        qualificadora = row['Qualificadora'] if 'Qualificadora' in df.columns and pd.notna(row['Qualificadora']) else ''
        pena_min = row['Pena_Minima_Meses'] if 'Pena_Minima_Meses' in df.columns and pd.notna(row['Pena_Minima_Meses']) else 0
        pena_max = row['Pena_Maxima_Meses'] if 'Pena_Maxima_Meses' in df.columns and pd.notna(row['Pena_Maxima_Meses']) else 0
        
        # Converter meses para anos
        pena_min_anos = pena_min / 12
        pena_max_anos = pena_max / 12
        
        # Criar descrição completa
        descricao_completa = crime_base
        if pd.notna(qualificadora) and qualificadora != '':
            descricao_completa += f" ({qualificadora})"
        
        # Criar chave única para o crime
        if pd.notna(artigo) and pd.notna(descricao_completa):
            chave = f"{artigo} - {descricao_completa[:80]}..."
            crimes_dict[chave] = {
                'artigo': artigo,
                'artigo_base': artigo.split()[0] if pd.notna(artigo) else '',
                'descricao_completa': descricao_completa,
                'qualificadora': qualificadora,
                'pena_min': pena_min_anos,
                'pena_max': pena_max_anos,
                'tipo_penal': 'Crime Base' if pd.isna(qualificadora) or qualificadora == '' else 'Qualificado',
                'pena_min_original': pena_min,
                'pena_max_original': pena_max,
                'unidade_original': 'mês'
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
    1. **Faça upload do arquivo `crimes_privacao_liberdade_processado.csv` acima**
    2. **O arquivo deve conter as colunas:**
       - Crime_Base, Artigo, Qualificadora
       - Pena_Minima_Meses, Pena_Maxima_Meses
    """)
    st.stop()

# Fase 1: Pena Base e Circunstâncias
st.header("1️⃣ Fase 1: Pena Base e Circunstâncias")
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
    circunstancia = st.radio("Circunstância do Crime:", ["Neutra", "Desfavorável", "Gravemente Desfavorável"])
    pena_base_inicial = min_pena
    ajuste_circunstancia = {"Neutra": 0, "Desfavorável": 0.2, "Gravemente Desfavorável": 0.4}
    fator_circunstancia = ajuste_circunstancia[circunstancia]
    pena_base_ajustada = pena_base_inicial * (1 + fator_circunstancia)
    
    st.write(f"**Pena prevista:** {min_pena:.1f} a {max_pena:.1f} anos")
    st.write(f"**Pena base inicial:** {pena_base_inicial:.1f} anos")
    st.write(f"**Circunstância {circunstancia.lower()}:** {fator_circunstancia*100:.0f}%")
    st.success(f"**PENA BASE APÓS CIRCUNSTÂNCIAS: {pena_base_ajustada:.1f} anos**")

# Fase 2: Atenuantes e Agravantes
st.header("2️⃣ Fase 2: Atenuantes e Agravantes Gerais")
col1, col2 = st.columns(2)

with col1:
    st.subheader("🔽 Atenuantes (Art. 65 CP)")
    atenuantes = st.multiselect("Selecione as atenuantes:", [
        "Réu primário de bons antecedentes", "Arrependimento espontâneo", 
        "Confissão espontânea", "Reparação do dano", "Coação moral", 
        "Embriaguez acidental", "Motivo de relevante valor social/moral"
    ])

with col2:
    st.subheader("🔼 Agravantes (Art. 61 CP)")
    agravantes = st.multiselect("Selecione as agravantes:", [
        "Reincidente específico", "Motivo fútil/torpe", "Crime contra idoso/doente", 
        "Uso de disfarce/emboscada", "Abuso de confiança/poder", 
        "Racismo/xenofobia", "Aumento do dano maliciosamente"
    ])

# Fase 3: Majorantes e Minorantes
st.header("3️⃣ Fase 3: Causas de Aumento/Diminuição")
majorantes_minorantes_generico = {
    "majorantes": [
        "Uso de arma (1/6 a 1/2)", "Violência grave (1/3 a 2/3)", 
        "Concurso de 2+ pessoas (1/4 a 1/2)", "Restrição à liberdade (1/6 a 1/3)", 
        "Abuso de confiança (1/6 a 1/3)"
    ],
    "minorantes": [
        "Valor ínfimo (1/6 a 1/3)", "Arrependimento posterior (1/6 a 1/3)", 
        "Circunstâncias atenuantes não previstas (1/6 a 1/3)"
    ]
}

col1, col2 = st.columns(2)
with col1:
    majorantes = st.multiselect("Causas de aumento (majorantes):", majorantes_minorantes_generico["majorantes"])
with col2:
    minorantes = st.multiselect("Causas de diminuição (minorantes):", majorantes_minorantes_generico["minorantes"])

# Fase 4: Cálculo Final
st.header("4️⃣ Fase 4: Cálculo Final da Pena")

if st.button("🎯 Calcular Pena Definitiva", type="primary"):
    pena_calculada = pena_base_ajustada
    
    st.subheader("📊 Detalhamento do Cálculo")
    calculo_detalhado = f"| Etapa | Valor | Ajuste |\n|-------|-------|---------|\n| **Pena Base Inicial** | {pena_base_inicial:.1f} anos | - |\n| Circunstância {circunstancia} | {pena_base_ajustada:.1f} anos | {fator_circunstancia*100:+.0f}% |\n"
    
    # Aplicar atenuantes
    ajustes_atenuantes = []
    for i, atenuante in enumerate(atenuantes, 1):
        reducao = pena_base_ajustada * (1/6)
        pena_calculada -= reducao
        ajustes_atenuantes.append(reducao)
        calculo_detalhado += f"| Atenuante {i} | {pena_calculada:.1f} anos | -{reducao:.1f} anos |\n"
    
    # Aplicar agravantes
    ajustes_agravantes = []
    for i, agravante in enumerate(agravantes, 1):
        aumento = pena_base_ajustada * (1/6)
        pena_calculada += aumento
        ajustes_agravantes.append(aumento)
        calculo_detalhado += f"| Agravante {i} | {pena_calculada:.1f} anos | +{aumento:.1f} anos |\n"
    
    # Aplicar majorantes
    ajustes_majorantes = []
    for i, majorante in enumerate(majorantes, 1):
        aumento = pena_base_ajustada * (1/4)
        pena_calculada += aumento
        ajustes_majorantes.append(aumento)
        calculo_detalhado += f"| Majorante {i} | {pena_calculada:.1f} anos | +{aumento:.1f} anos |\n"
    
    # Aplicar minorantes
    ajustes_minorantes = []
    for i, minorante in enumerate(minorantes, 1):
        reducao = pena_base_ajustada * (1/4)
        pena_calculada -= reducao
        ajustes_minorantes.append(reducao)
        calculo_detalhado += f"| Minorante {i} | {pena_calculada:.1f} anos | -{reducao:.1f} anos |\n"
    
    # Aplicar limites legais
    pena_final = max(min_pena, min(max_pena, pena_calculada))
    calculo_detalhado += f"| **LIMITES LEGAIS** | **{pena_final:.1f} anos** | **Ajuste final** |"
    
    st.markdown(calculo_detalhado)

    # Fase 5: Tipo de Pena Privativa
    st.header("5️⃣ Fase 5: Tipo de Pena Privativa")
    
    # Determinar tipo de pena (Reclusão ou Detenção) baseado na descrição do crime
    descricao = crime_info['descricao_completa'].lower()
    
    # Crimes que geralmente são reclusão
    crimes_reclusao = [
        'homicídio', 'latrocínio', 'estupro', 'sequestro', 'roubo', 'tráfico',
        'extorsão', 'cárcere privado', 'redução à condição análoga à de escravo'
    ]
    
    # Crimes que geralmente são detenção  
    crimes_detencao = [
        'ameaça', 'injúria', 'difamação', 'calúnia', 'danos', 'furto'
    ]
    
    if any(crime in descricao for crime in crimes_reclusao):
        tipo_pena = "RECLUSÃO"
        cor_tipo_pena = "#ff4444"
        descricao_tipo = "Pena mais grave - Regimes: Fechado, Semiaberto ou Aberto"
    elif any(crime in descricao for crime in crimes_detencao):
        tipo_pena = "DETENÇÃO"
        cor_tipo_pena = "#ffaa00"
        descricao_tipo = "Pena menos grave - Regimes: Semiaberto ou Aberto"
    else:
        # Por padrão, considerar como reclusão se pena máxima > 4 anos
        if max_pena > 4:
            tipo_pena = "RECLUSÃO"
            cor_tipo_pena = "#ff4444"
            descricao_tipo = "Pena mais grave - Regimes: Fechado, Semiaberto ou Aberto"
        else:
            tipo_pena = "DETENÇÃO"
            cor_tipo_pena = "#ffaa00"
            descricao_tipo = "Pena menos grave - Regimes: Semiaberto ou Aberto"
    
    st.markdown(f"""
    <div style="background-color: {cor_tipo_pena}20; padding: 15px; border-radius: 10px; border-left: 5px solid {cor_tipo_pena};">
        <h3 style="color: {cor_tipo_pena}; margin: 0;">📋 TIPO DE PENA: {tipo_pena}</h3>
        <p style="margin: 5px 0 0 0;">{descricao_tipo}</p>
    </div>
    """, unsafe_allow_html=True)

    # Fase 6: Regime de Cumprimento
    st.header("6️⃣ Fase 6: Regime de Cumprimento")
    
    # Verificar reincidência
    reincidente = "Reincidente específico" in agravantes
    
    # Determinar regime conforme Art. 33 CP
    if tipo_pena == "RECLUSÃO":
        if pena_final > 8:
            regime = "FECHADO"
            cor_regime = "#ff4444"
            descricao = "Presídio de segurança máxima/média"
            fundamento = "Art. 33, §2º, 'a' - Pena superior a 8 anos"
        elif pena_final >= 4:
            if not reincidente:
                regime = "SEMIABERTO"
                cor_regime = "#ffaa00"
                descricao = "Colônia agrícola, industrial ou similar"
                fundamento = "Art. 33, §2º, 'b' - Não reincidente, pena 4-8 anos"
            else:
                regime = "FECHADO"
                cor_regime = "#ff4444"
                descricao = "Presídio de segurança máxima/média"
                fundamento = "Art. 33, §2º - Reincidente, pena 4-8 anos"
        else:
            if not reincidente:
                regime = "ABERTO"
                cor_regime = "#44cc44"
                descricao = "Casa de albergado, trabalho externo"
                fundamento = "Art. 33, §2º, 'c' - Não reincidente, pena até 4 anos"
            else:
                regime = "SEMIABERTO"
                cor_regime = "#ffaa00"
                descricao = "Colônia agrícola, industrial ou similar"
                fundamento = "Art. 33, §2º - Reincidente, pena até 4 anos"
    
    else:  # DETENÇÃO
        if pena_final >= 4:
            regime = "SEMIABERTO"
            cor_regime = "#ffaa00"
            descricao = "Colônia agrícola, industrial ou similar"
            fundamento = "Art. 33 - Detenção: regime semiaberto ou aberto"
        else:
            regime = "ABERTO"
            cor_regime = "#44cc44"
            descricao = "Casa de albergado, trabalho externo"
            fundamento = "Art. 33 - Detenção: regime semiaberto ou aberto"
    
    st.markdown(f"""
    <div style="background-color: {cor_regime}20; padding: 20px; border-radius: 10px; border-left: 5px solid {cor_regime};">
        <h2 style="color: {cor_regime}; margin: 0;">🔒 REGIME {regime}</h2>
        <p style="margin: 10px 0 0 0; font-size: 16px;"><strong>{descricao}</strong></p>
        <p style="margin: 5px 0 0 0; font-size: 12px; color: #666;"><em>{fundamento}</em></p>
    </div>
    """, unsafe_allow_html=True)

    # Fase 7: Substituição da Pena
    st.header("7️⃣ Fase 7: Substituição por Pena Restritiva de Direitos")
    
    # Verificar condições para substituição (Art. 44 CP)
    pode_substituir = False
    condicoes = []
    
    # Condição I: Pena até 4 anos e crime sem violência
    if pena_final <= 4:
        condicoes.append("✅ Pena não superior a 4 anos")
        # Verificar se é crime violento (simplificado)
        crimes_violentos = ["homicídio", "lesão corporal", "latrocínio", "estupro", "roubo", "sequestro"]
        crime_violento = any(violento in crime_info['descricao_completa'].lower() for violento in crimes_violentos)
        
        if not crime_violento:
            condicoes.append("✅ Crime sem violência ou grave ameaça")
            pode_substituir = True
        else:
            condicoes.append("❌ Crime com violência ou grave ameaça")
    else:
        condicoes.append("❌ Pena superior a 4 anos")
    
    # Condição II: Não reincidente
    if not reincidente:
        condicoes.append("✅ Réu não reincidente")
        pode_substituir = pode_substituir and True
    else:
        condicoes.append("❌ Réu reincidente")
        # Exceção: Art. 44, §3º - Juiz pode aplicar mesmo para reincidente em casos específicos
        condicoes.append("⚠️ Juiz pode analisar aplicação excepcional")
    
    # Condição III: Análise do Art. 59
    condicoes.append("✅ Análise favorável dos critérios do Art. 59")
    
    if pode_substituir:
        substituicao = "**CABE SUBSTITUIÇÃO** por pena restritiva de direitos"
        cor_subst = "#44cc44"
        fundamento_subst = "Art. 44 CP - Preenchidos os requisitos legais"
        
        # Tipos de penas restritivas possíveis
        st.subheader("📋 Penas Restritivas de Direitos Possíveis (Art. 43 CP)")
        
        col_penas1, col_penas2 = st.columns(2)
        
        with col_penas1:
            st.write("""
            **Penas Restritivas:**
            - 💰 Prestação pecuniária
            - 🏛️ Prestação de serviços à comunidade
            - 🚫 Interdição temporária de direitos
            - 🎯 Limitação de fim de semana
            - 📉 Perda de bens e valores
            """)
        
        with col_penas2:
            st.write("""
            **Regras de Conversão:**
            - Pena ≤ 1 ano: multa OU 1 restritiva
            - Pena > 1 ano: 1 restritiva + multa OU 2 restritivas
            - Descumprimento: conversão em privativa (Art. 44, §4º)
            """)
    
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
    
    # Mostrar condições analisadas
    st.write("**📝 Condições analisadas para substituição:**")
    for condicao in condicoes:
        st.write(condicao)

    # GRÁFICOS PLOTLY
    st.header("📊 Visualização da Dosimetria")
    
    # Gráfico 1: Composição da Pena
    st.subheader("🎯 Composição da Pena Final")
    
    # Preparar dados para o gráfico de composição
    categorias = []
    valores = []
    cores = []
    textos = []
    
    # Pena base
    categorias.append("Pena Base")
    valores.append(pena_base_inicial)
    cores.append("#2196F3")
    textos.append(f"Base: {pena_base_inicial:.1f} anos")
    
    # Ajuste por circunstância
    if fator_circunstancia > 0:
        categorias.append(f"Circunstância<br>({circunstancia})")
        valores.append(pena_base_ajustada - pena_base_inicial)
        cores.append("#9C27B0")
        textos.append(f"+{(pena_base_ajustada - pena_base_inicial):.1f} anos")
    
    # Atenuantes
    if ajustes_atenuantes:
        categorias.append("Atenuantes")
        valores.append(-sum(ajustes_atenuantes))
        cores.append("#4CAF50")
        textos.append(f"-{sum(ajustes_atenuantes):.1f} anos")
    
    # Agravantes
    if ajustes_agravantes:
        categorias.append("Agravantes")
        valores.append(sum(ajustes_agravantes))
        cores.append("#FF9800")
        textos.append(f"+{sum(ajustes_agravantes):.1f} anos")
    
    # Majorantes
    if ajustes_majorantes:
        categorias.append("Majorantes")
        valores.append(sum(ajustes_majorantes))
        cores.append("#F44336")
        textos.append(f"+{sum(ajustes_majorantes):.1f} anos")
    
    # Minorantes
    if ajustes_minorantes:
        categorias.append("Minorantes")
        valores.append(-sum(ajustes_minorantes))
        cores.append("#00BCD4")
        textos.append(f"-{sum(ajustes_minorantes):.1f} anos")
    
    # Criar gráfico de barras horizontal
    fig_composicao = go.Figure()
    
    for i, (cat, val, cor, texto) in enumerate(zip(categorias, valores, cores, textos)):
        fig_composicao.add_trace(go.Bar(
            y=[cat],
            x=[val],
            orientation='h',
            marker_color=cor,
            text=[texto],
            textposition='auto',
            hovertemplate=f"<b>{cat}</b><br>Valor: {val:+.1f} anos<extra></extra>",
            name=cat
        ))
    
    fig_composicao.update_layout(
        title="Impacto dos Componentes na Pena Final",
        xaxis_title="Anos de Pena",
        yaxis_title="Componentes",
        showlegend=False,
        height=400,
        plot_bgcolor='rgba(240,240,240,0.8)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12),
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    # Adicionar linha da pena final
    fig_composicao.add_vline(x=pena_final, line_dash="dash", line_color="#FF5722", 
                            annotation_text=f"Pena Final: {pena_final:.1f} anos",
                            annotation_position="top right")
    
    st.plotly_chart(fig_composicao, use_container_width=True)

    # Resumo final estilizado
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 25px; border-radius: 15px; margin: 20px 0; text-align: center; box-shadow: 0 8px 25px rgba(0,0,0,0.2);">
        <h3 style="color: white; margin: 0 0 15px 0; font-weight: 600;">🎯 RESUMO FINAL DA DOSIMETRIA</h3>
        <div style="display: flex; justify-content: space-around; align-items: center; flex-wrap: wrap;">
            <div style="background: rgba(255,255,255,0.9); padding: 15px; border-radius: 10px; margin: 5px; min-width: 200px;">
                <div style="font-weight: bold; color: #333; font-size: 16px;">Pena Final</div>
                <div style="font-size: 24px; font-weight: bold; color: #2196F3;">{pena_final:.1f} anos</div>
            </div>
            <div style="background: rgba(255,255,255,0.9); padding: 15px; border-radius: 10px; margin: 5px; min-width: 200px;">
                <div style="font-weight: bold; color: #333; font-size: 16px;">Tipo de Pena</div>
                <div style="font-size: 16px; font-weight: bold; color: {cor_tipo_pena};">{tipo_pena}</div>
            </div>
            <div style="background: rgba(255,255,255,0.9); padding: 15px; border-radius: 10px; margin: 5px; min-width: 200px;">
                <div style="font-weight: bold; color: #333; font-size: 16px;">Regime</div>
                <div style="font-size: 16px; font-weight: bold; color: {cor_regime};">{regime}</div>
            </div>
            <div style="background: rgba(255,255,255,0.9); padding: 15px; border-radius: 10px; margin: 5px; min-width: 200px;">
                <div style="font-weight: bold; color: #333; font-size: 16px;">Substituição</div>
                <div style="font-size: 14px; font-weight: bold; color: {cor_subst};">{substituicao.replace('**', '')}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# SEÇÃO DE REFERÊNCIAS LEGAIS COMPLETAS
st.header("📚 Referências Legais Completas")

tab1, tab2, tab3, tab4 = st.tabs(["📋 Regimes", "⚖️ Penas Restritivas", "🔍 Súmulas", "📊 Progressão"])

with tab1:
    st.subheader("Art. 33 CP - Reclusão e Detenção")
    st.write("""
    **§ 1º - Considera-se:**
    - 🔒 **Regime Fechado**: Execução em estabelecimento de segurança máxima/média
    - 🔐 **Regime Semiaberto**: Execução em colônia agrícola, industrial ou similar  
    - 🔓 **Regime Aberto**: Execução em casa de albergado
    
    **§ 2º - Critérios para regime inicial:**
    - Pena > 8 anos: FECHADO
    - Pena 4-8 anos (não reincidente): SEMIABERTO
    - Pena ≤ 4 anos (não reincidente): ABERTO
    """)

with tab2:
    st.subheader("Arts. 43-48 CP - Penas Restritivas de Direitos")
    st.write("""
    **Art. 43 - Espécies:**
    - 💰 Prestação pecuniária
    - 📉 Perda de bens e valores  
    - 🏛️ Prestação de serviços à comunidade
    - 🚫 Interdição temporária de direitos
    - 🎯 Limitação de fim de semana
    
    **Art. 44 - Requisitos para substituição:**
    - Pena ≤ 4 anos + crime sem violência
    - Não reincidente em crime doloso
    - Análise favorável do Art. 59
    """)

with tab3:
    st.subheader("Súmulas Relevantes")
    st.write("""
    **Súmula 231 STJ:**
    - A substituição da pena privativa por restritiva de direitos pressupõe requisitos cumulativos
    
    **Súmula 444 STJ:**
    - A dosimetria da pena deve observar o sistema trifásico do Art. 68 CP
    - O juiz deve fundamentar cada fase do cálculo
    """)

with tab4:
    st.subheader("Progressão de Regime")
    st.write("""
    **Regras de progressão:**
    - 1/6 da pena no regime anterior (condenação comum)
    - 2/5 da pena para crimes hediondos
    - Requer bom comportamento e demais requisitos
    - Análise pelo Juízo da Execução Penal
    """)

st.markdown("---")
st.write("**⚖️ Ferramenta educacional - Consulte sempre a legislação atual e um profissional do direito**")
st.write("**📚 Base legal:** Arts. 33, 43-48, 59, 61, 65, 68 do Código Penal Brasileiro")
