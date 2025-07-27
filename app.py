import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import re

# Configuração da página
st.set_page_config(
    page_title="Sistema de Gestão de Metas",
    page_icon="🌊",
    layout="wide"
)

# CSS personalizado para tema azul marinho com texto branco
st.markdown("""
    <style>
    .stApp {
        background-color: #003366;
        color: white;
    }
    .stButton button {
        background-color: #f4ebe2;
        color: #003366;
    }
    .stTextInput input, .stSelectbox select, .stDateInput input {
        color: white;
        background-color: rgba(255, 255, 255, 0.1);
        border-color: #637252;
    }
    div[data-baseweb="select"] > div {
        background-color: rgba(255, 255, 255, 0.1);
        border-color: #637252;
        color: white;
    }
    div[data-testid="stDataFrame"] {
        color: white;
    }
    .stDataFrame {
        background-color: rgba(255, 255, 255, 0.1);
    }
    div[data-testid="stMarkdown"] {
        color: white;
    }
    .stTab {
        background-color: #637252;
        color: #f4ebe2;
    }
    .stTab [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #003366;
    }
    .stTab [data-baseweb="tab"] {
        background-color: #637252;
        border-radius: 4px;
        color: white;
        padding: 8px 16px;
    }
    .stTab [aria-selected="true"] {
        background-color: #f4ebe2;
        color: #003366;
    }

    /* Estilo para a barra de progresso */
    .stSlider [data-baseweb="slider"] {
        background-color: rgba(255, 255, 255, 0.2);
    }
    
    .stSlider [data-baseweb="slider"] div::before {
        background-color: #637252;
    }
    
    .stSlider [data-baseweb="thumb"] {
        background-color: #637252;
        border-color: #637252;
    }
    </style>
""", unsafe_allow_html=True)

# Título com emoji de onda
st.title("🌊 Sistema de Gestão de Metas")

class GestorMetas:
    def __init__(self):
        self.init_database()

    def init_database(self):
        """Inicializa o banco de dados SQLite."""
        conn = sqlite3.connect('metas.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_name TEXT NOT NULL,
                department TEXT NOT NULL,
                goal_description TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT NOT NULL,
                status TEXT NOT NULL,
                progress INTEGER NOT NULL,
                completion_date TEXT,
                diagnosis TEXT,
                suggestions TEXT
            )
        ''')
        
        conn.commit()
        conn.close()

    def add_meta(self, employee_name, department, goal_description, start_date, end_date, status, progress):
        """Adiciona uma nova meta ao banco de dados."""
        conn = sqlite3.connect('metas.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO metas (employee_name, department, goal_description, start_date, end_date, status, progress)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (employee_name, department, goal_description, start_date, end_date, status, progress))
        
        conn.commit()
        conn.close()
        return True

    def get_all_metas(self):
        """Retorna todas as metas do banco de dados."""
        conn = sqlite3.connect('metas.db')
        df = pd.read_sql_query('SELECT * FROM metas', conn)
        conn.close()
        return df

    def update_meta(self, meta_id, **kwargs):
        """Atualiza uma meta específica."""
        conn = sqlite3.connect('metas.db')
        cursor = conn.cursor()
        
        set_clause = ', '.join([f"{key} = ?" for key in kwargs.keys()])
        values = list(kwargs.values()) + [meta_id]
        
        cursor.execute(f'''
            UPDATE metas SET {set_clause} WHERE id = ?
        ''', values)
        
        conn.commit()
        conn.close()
        return True

    def delete_meta(self, meta_id):
        """Remove uma meta do banco de dados."""
        conn = sqlite3.connect('metas.db')
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM metas WHERE id = ?', (meta_id,))
        
        conn.commit()
        conn.close()
        return True

    def get_meta_by_id(self, meta_id):
        """Retorna uma meta específica pelo ID."""
        conn = sqlite3.connect('metas.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM metas WHERE id = ?', (meta_id,))
        result = cursor.fetchone()
        
        conn.close()
        return result

def main():
    gestor = GestorMetas()
    
    # Tabs horizontais com cores personalizadas
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📝 Adicionar Meta",
        "📊 Visualizar Metas",
        "🔄 Atualizar Meta",
        "🔍 Diagnóstico",
        "📈 Relatórios"
    ])

    with tab1:
        st.subheader("Adicionar Nova Meta")
        with st.form("nova_meta"):
            col1, col2 = st.columns(2)
            with col1:
                employee_name = st.text_input("Nome do Funcionário")
                department = st.selectbox(
                    "Área/Departamento",
                    ["Vendas", "Marketing", "RH", "Financeiro", "TI", 
                     "Operações", "Administrativo", "Produção", "Logística"]
                )
                goal_description = st.text_area("Descrição da Meta")
            
            with col2:
                start_date = st.date_input("Data Início")
                end_date = st.date_input("Data Fim")
                status = st.selectbox(
                    "Status",
                    ["Em Andamento", "Concluída", "Não Concluída", "Atrasada"]
                )
                progress = st.slider("Progresso (%)", 0, 100, 0)

            submitted = st.form_submit_button("Adicionar Meta")
            if submitted:
                if employee_name and department and goal_description:
                    try:
                        gestor.add_meta(
                            employee_name=employee_name,
                            department=department,
                            goal_description=goal_description,
                            start_date=str(start_date),
                            end_date=str(end_date),
                            status=status,
                            progress=progress
                        )
                        st.success("Meta adicionada com sucesso!")
                    except Exception as e:
                        st.error(f"Erro ao adicionar meta: {e}")
                else:
                    st.error("Por favor, preencha todos os campos obrigatórios.")

    with tab2:
        st.subheader("Visualizar Metas")
        
        # Filtros
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_department = st.selectbox(
                "Filtrar por Departamento",
                ["Todos", "Vendas", "Marketing", "RH", "Financeiro", "TI", 
                 "Operações", "Administrativo", "Produção", "Logística"]
            )
        with col2:
            filter_status = st.selectbox(
                "Filtrar por Status",
                ["Todos", "Em Andamento", "Concluída", "Não Concluída", "Atrasada"]
            )
        with col3:
            st.write("")  # Espaçamento
        
        try:
            df = gestor.get_all_metas()
            
            if not df.empty:
                # Aplicar filtros
                if filter_department != "Todos":
                    df = df[df['department'] == filter_department]
                if filter_status != "Todos":
                    df = df[df['status'] == filter_status]
                
                # Exibir dataframe
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Estatísticas
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total de Metas", len(df))
                with col2:
                    concluidas = len(df[df['status'] == 'Concluída'])
                    st.metric("Concluídas", concluidas)
                with col3:
                    em_andamento = len(df[df['status'] == 'Em Andamento'])
                    st.metric("Em Andamento", em_andamento)
                with col4:
                    progresso_medio = df['progress'].mean() if not df.empty else 0
                    st.metric("Progresso Médio", f"{progresso_medio:.1f}%")
            else:
                st.info("Nenhuma meta encontrada. Adicione uma meta na aba 'Adicionar Meta'.")
                
        except Exception as e:
            st.error(f"Erro ao carregar metas: {e}")

    with tab3:
        st.subheader("Atualizar Meta")
        
        try:
            df = gestor.get_all_metas()
            
            if not df.empty:
                # Seleção da meta
                meta_options = [f"ID {row['id']} - {row['employee_name']} - {row['goal_description'][:50]}..." 
                               for _, row in df.iterrows()]
                selected_meta = st.selectbox("Selecione a meta para atualizar:", meta_options)
                
                if selected_meta:
                    meta_id = int(selected_meta.split(" ")[1])
                    meta_data = df[df['id'] == meta_id].iloc[0]
                    
                    with st.form("atualizar_meta"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            new_employee_name = st.text_input("Nome do Funcionário", value=meta_data['employee_name'])
                            new_department = st.selectbox(
                                "Área/Departamento",
                                ["Vendas", "Marketing", "RH", "Financeiro", "TI", 
                                 "Operações", "Administrativo", "Produção", "Logística"],
                                index=["Vendas", "Marketing", "RH", "Financeiro", "TI", 
                                       "Operações", "Administrativo", "Produção", "Logística"].index(meta_data['department'])
                            )
                            new_goal_description = st.text_area("Descrição da Meta", value=meta_data['goal_description'])
                        
                        with col2:
                            new_start_date = st.date_input("Data Início", value=pd.to_datetime(meta_data['start_date']).date())
                            new_end_date = st.date_input("Data Fim", value=pd.to_datetime(meta_data['end_date']).date())
                            new_status = st.selectbox(
                                "Status",
                                ["Em Andamento", "Concluída", "Não Concluída", "Atrasada"],
                                index=["Em Andamento", "Concluída", "Não Concluída", "Atrasada"].index(meta_data['status'])
                            )
                            new_progress = st.slider("Progresso (%)", 0, 100, int(meta_data['progress']))
                        
                        col_update, col_delete = st.columns(2)
                        with col_update:
                            update_submitted = st.form_submit_button("Atualizar Meta", type="primary")
                        with col_delete:
                            delete_submitted = st.form_submit_button("Excluir Meta", type="secondary")
                        
                        if update_submitted:
                            try:
                                gestor.update_meta(
                                    meta_id,
                                    employee_name=new_employee_name,
                                    department=new_department,
                                    goal_description=new_goal_description,
                                    start_date=str(new_start_date),
                                    end_date=str(new_end_date),
                                    status=new_status,
                                    progress=new_progress
                                )
                                st.success("Meta atualizada com sucesso!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao atualizar meta: {e}")
                        
                        if delete_submitted:
                            try:
                                gestor.delete_meta(meta_id)
                                st.success("Meta excluída com sucesso!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao excluir meta: {e}")
            else:
                st.info("Nenhuma meta encontrada para atualizar.")
                
        except Exception as e:
            st.error(f"Erro ao carregar metas: {e}")

    with tab4:
        st.subheader("Diagnóstico de Metas")
        
        # Seleção do tipo de diagnóstico
        diagnostic_type = st.selectbox(
            "Tipo de Diagnóstico:",
            ["Análise Geral", "Diagnóstico Interativo", "Análise Individual de Meta"]
        )
        
        try:
            df = gestor.get_all_metas()
            
            if not df.empty:
                if diagnostic_type == "Análise Geral":
                    # Análise geral (código existente)
                    st.markdown("### 📊 Análise Geral")
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        # Distribuição por status
                        status_counts = df['status'].value_counts()
                        st.markdown("**Distribuição por Status:**")
                        for status, count in status_counts.items():
                            percentage = (count / len(df)) * 100
                            st.write(f"• {status}: {count} ({percentage:.1f}%)")
                    
                    with col2:
                        # Distribuição por departamento
                        dept_counts = df['department'].value_counts()
                        st.markdown("**Distribuição por Departamento:**")
                        for dept, count in dept_counts.items():
                            percentage = (count / len(df)) * 100
                            st.write(f"• {dept}: {count} ({percentage:.1f}%)")
                    
                    with col3:
                        # Estatísticas de progresso
                        avg_progress = df['progress'].mean()
                        min_progress = df['progress'].min()
                        max_progress = df['progress'].max()
                        
                        st.markdown("**Estatísticas de Progresso:**")
                        st.write(f"• Média: {avg_progress:.1f}%")
                        st.write(f"• Mínimo: {min_progress}%")
                        st.write(f"• Máximo: {max_progress}%")
                    
                    st.markdown("---")
                    
                    # Metas críticas
                    st.markdown("### ⚠️ Metas que Precisam de Atenção")
                    
                    metas_criticas = df[
                        (df['status'].isin(['Em Andamento', 'Atrasada'])) & 
                        (df['progress'] < 50)
                    ]
                    
                    if not metas_criticas.empty:
                        for _, meta in metas_criticas.iterrows():
                            with st.expander(f"🔴 {meta['employee_name']} - {meta['goal_description'][:50]}..."):
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.write(f"**Funcionário:** {meta['employee_name']}")
                                    st.write(f"**Departamento:** {meta['department']}")
                                    st.write(f"**Status:** {meta['status']}")
                                with col2:
                                    st.write(f"**Progresso:** {meta['progress']}%")
                                    st.write(f"**Data Início:** {meta['start_date']}")
                                    st.write(f"**Data Fim:** {meta['end_date']}")
                                
                                # Diagnóstico automático
                                if meta['progress'] < 25:
                                    st.warning("🚨 **Diagnóstico:** Meta com progresso muito baixo. Recomenda-se revisão urgente.")
                                elif meta['progress'] < 50:
                                    st.info("⚡ **Diagnóstico:** Meta precisando de aceleração para atingir objetivo.")
                    else:
                        st.success("✅ Todas as metas estão com progresso satisfatório!")
                    
                    # Metas de destaque
                    st.markdown("### 🌟 Metas de Destaque")
                    metas_destaque = df[df['progress'] >= 80]
                    
                    if not metas_destaque.empty:
                        for _, meta in metas_destaque.iterrows():
                            st.success(f"🎯 {meta['employee_name']} - {meta['goal_description'][:50]}... ({meta['progress']}%)")
                    else:
                        st.info("Nenhuma meta com progresso acima de 80% encontrada.")

                elif diagnostic_type == "Diagnóstico Interativo":
                    st.markdown("### 🔍 Diagnóstico Interativo")
                    st.markdown("Responda às perguntas abaixo para obter um diagnóstico personalizado das metas:")
                    
                    with st.form("diagnostic_form"):
                        st.markdown("#### 1. Contexto Organizacional")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            recursos_adequados = st.radio(
                                "Os funcionários têm recursos adequados para atingir suas metas?",
                                ["Sim, completamente", "Parcialmente", "Não, faltam recursos", "Não sei avaliar"]
                            )
                            
                            comunicacao_clara = st.radio(
                                "As metas foram comunicadas de forma clara?",
                                ["Sim, muito clara", "Razoavelmente clara", "Pouco clara", "Confusa"]
                            )
                            
                            prazo_realista = st.radio(
                                "Os prazos estabelecidos são realistas?",
                                ["Sim, adequados", "Um pouco apertados", "Muito apertados", "Impossíveis"]
                            )
                        
                        with col2:
                            apoio_gestao = st.radio(
                                "Há apoio suficiente da gestão?",
                                ["Sim, total apoio", "Apoio moderado", "Pouco apoio", "Sem apoio"]
                            )
                            
                            treinamento = st.radio(
                                "Os funcionários receberam treinamento adequado?",
                                ["Sim, completo", "Parcial", "Mínimo", "Nenhum"]
                            )
                            
                            motivacao_equipe = st.radio(
                                "Como está a motivação da equipe?",
                                ["Muito alta", "Alta", "Média", "Baixa", "Muito baixa"]
                            )
                        
                        st.markdown("#### 2. Obstáculos e Desafios")
                        
                        col3, col4 = st.columns(2)
                        with col3:
                            principais_obstaculos = st.multiselect(
                                "Quais são os principais obstáculos?",
                                ["Falta de tempo", "Recursos insuficientes", "Falta de conhecimento técnico", 
                                 "Problemas de comunicação", "Mudanças de prioridades", "Sobrecarga de trabalho",
                                 "Falta de apoio da gestão", "Problemas externos", "Outros"]
                            )
                            
                            frequencia_revisao = st.radio(
                                "Com que frequência as metas são revisadas?",
                                ["Semanalmente", "Quinzenalmente", "Mensalmente", "Trimestralmente", "Raramente"]
                            )
                        
                        with col4:
                            feedback_regular = st.radio(
                                "Há feedback regular sobre o progresso?",
                                ["Sim, constante", "Ocasionalmente", "Raramente", "Nunca"]
                            )
                            
                            ferramentas_adequadas = st.radio(
                                "As ferramentas de trabalho são adequadas?",
                                ["Sim, excelentes", "Adequadas", "Básicas", "Inadequadas"]
                            )
                        
                        st.markdown("#### 3. Expectativas e Melhorias")
                        
                        areas_melhoria = st.multiselect(
                            "Que áreas precisam de melhoria?",
                            ["Planejamento de metas", "Comunicação", "Recursos e ferramentas", 
                             "Treinamento", "Acompanhamento", "Motivação da equipe", 
                             "Processos internos", "Suporte técnico"]
                        )
                        
                        comentarios_adicionais = st.text_area(
                            "Comentários ou observações adicionais:",
                            placeholder="Descreva qualquer situação específica ou sugestão..."
                        )
                        
                        submit_diagnostic = st.form_submit_button("🔍 Gerar Diagnóstico")
                        
                        if submit_diagnostic:
                            # Gerar diagnóstico baseado nas respostas
                            st.markdown("---")
                            st.markdown("## 📋 Resultado do Diagnóstico")
                            
                            # Análise de recursos
                            if recursos_adequados in ["Não, faltam recursos", "Parcialmente"]:
                                st.warning("⚠️ **Recursos:** Identificada deficiência de recursos que pode impactar o cumprimento das metas.")
                                st.markdown("**Recomendação:** Revisar e alocar recursos adicionais ou redistribuir cargas de trabalho.")
                            
                            # Análise de comunicação
                            if comunicacao_clara in ["Pouco clara", "Confusa"]:
                                st.error("🚨 **Comunicação:** Problemas na clareza da comunicação das metas.")
                                st.markdown("**Recomendação:** Reorganizar reuniões de alinhamento e documentar metas de forma mais clara.")
                            
                            # Análise de prazos
                            if prazo_realista in ["Muito apertados", "Impossíveis"]:
                                st.error("🚨 **Prazos:** Prazos inadequados podem levar ao fracasso das metas.")
                                st.markdown("**Recomendação:** Revisar cronograma e ajustar prazos de forma realista.")
                            
                            # Análise de apoio
                            if apoio_gestao in ["Pouco apoio", "Sem apoio"]:
                                st.error("🚨 **Gestão:** Falta de apoio da gestão é crítica para o sucesso.")
                                st.markdown("**Recomendação:** Engajar liderança e estabelecer canais de suporte.")
                            
                            # Análise de motivação
                            if motivacao_equipe in ["Baixa", "Muito baixa"]:
                                st.warning("⚠️ **Motivação:** Baixa motivação da equipe pode comprometer resultados.")
                                st.markdown("**Recomendação:** Implementar programas de motivação e reconhecimento.")
                            
                            # Análise de obstáculos
                            if principais_obstaculos:
                                st.info(f"📌 **Obstáculos Identificados:** {', '.join(principais_obstaculos)}")
                                st.markdown("**Recomendação:** Criar plano de ação específico para cada obstáculo identificado.")
                            
                            # Análise de frequência de revisão
                            if frequencia_revisao in ["Raramente"]:
                                st.warning("⚠️ **Acompanhamento:** Baixa frequência de revisão pode levar à perda de controle.")
                                st.markdown("**Recomendação:** Estabelecer ciclos regulares de revisão (pelo menos mensais).")
                            
                            # Score geral
                            score_pontos = 0
                            total_pontos = 6
                            
                            if recursos_adequados == "Sim, completamente": score_pontos += 1
                            if comunicacao_clara == "Sim, muito clara": score_pontos += 1
                            if prazo_realista == "Sim, adequados": score_pontos += 1
                            if apoio_gestao == "Sim, total apoio": score_pontos += 1
                            if treinamento == "Sim, completo": score_pontos += 1
                            if motivacao_equipe in ["Muito alta", "Alta"]: score_pontos += 1
                            
                            score_percentual = (score_pontos / total_pontos) * 100
                            
                            st.markdown("### 🎯 Score de Saúde das Metas")
                            st.progress(score_percentual / 100)
                            st.write(f"**Score:** {score_percentual:.0f}% ({score_pontos}/{total_pontos} pontos)")
                            
                            if score_percentual >= 80:
                                st.success("🌟 **Excelente!** Ambiente muito favorável ao cumprimento das metas.")
                            elif score_percentual >= 60:
                                st.info("👍 **Bom!** Algumas melhorias podem otimizar os resultados.")
                            elif score_percentual >= 40:
                                st.warning("⚠️ **Atenção!** Várias áreas precisam de melhoria urgente.")
                            else:
                                st.error("🚨 **Crítico!** Ambiente desfavorável. Revisão completa necessária.")
                            
                            if comentarios_adicionais:
                                st.markdown("### 💬 Observações Registradas")
                                st.info(comentarios_adicionais)

                elif diagnostic_type == "Análise Individual de Meta":
                    st.markdown("### 🎯 Análise Individual de Meta")
                    
                    # Seleção da meta
                    meta_options = [f"ID {row['id']} - {row['employee_name']} - {row['goal_description'][:50]}..." 
                                   for _, row in df.iterrows()]
                    selected_meta = st.selectbox("Selecione a meta para análise detalhada:", meta_options)
                    
                    if selected_meta:
                        meta_id = int(selected_meta.split(" ")[1])
                        meta_data = df[df['id'] == meta_id].iloc[0]
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("#### 📊 Informações da Meta")
                            st.write(f"**Funcionário:** {meta_data['employee_name']}")
                            st.write(f"**Departamento:** {meta_data['department']}")
                            st.write(f"**Descrição:** {meta_data['goal_description']}")
                            st.write(f"**Status:** {meta_data['status']}")
                            st.write(f"**Progresso:** {meta_data['progress']}%")
                        
                        with col2:
                            st.markdown("#### 📅 Cronograma")
                            st.write(f"**Data Início:** {meta_data['start_date']}")
                            st.write(f"**Data Fim:** {meta_data['end_date']}")
                            
                            # Calcular dias restantes
                            from datetime import datetime
                            try:
                                end_date = datetime.strptime(meta_data['end_date'], '%Y-%m-%d')
                                today = datetime.now()
                                days_remaining = (end_date - today).days
                                
                                if days_remaining > 0:
                                    st.write(f"**Dias Restantes:** {days_remaining}")
                                elif days_remaining == 0:
                                    st.write("**Prazo:** Hoje!")
                                else:
                                    st.write(f"**Atrasada:** {abs(days_remaining)} dias")
                            except:
                                st.write("**Dias Restantes:** Não calculado")
                        
                        # Análise específica da meta
                        st.markdown("#### 🔍 Análise Detalhada")
                        
                        progress = meta_data['progress']
                        status = meta_data['status']
                        
                        if status == 'Concluída':
                            st.success("🎉 **Meta Concluída!** Parabéns pelo sucesso!")
                        elif status == 'Não Concluída':
                            st.error("❌ **Meta Não Concluída** - Necessária análise para próximas ações.")
                        elif status == 'Atrasada':
                            st.error(f"⏰ **Meta Atrasada** - Progresso atual: {progress}%")
                            if progress < 50:
                                st.warning("🚨 Progresso baixo para meta atrasada. Intervenção urgente necessária.")
                        elif status == 'Em Andamento':
                            if progress >= 80:
                                st.success(f"🚀 **Excelente progresso!** {progress}% - Meta no caminho certo.")
                            elif progress >= 60:
                                st.info(f"👍 **Bom progresso!** {progress}% - Manter o ritmo.")
                            elif progress >= 40:
                                st.warning(f"⚠️ **Progresso moderado** {progress}% - Pode precisar de aceleração.")
                            else:
                                st.error(f"🚨 **Progresso baixo** {progress}% - Revisão urgente necessária.")
                        
                        # Recomendações específicas
                        st.markdown("#### 💡 Recomendações")
                        
                        if progress < 25:
                            st.markdown("""
                            - 🔄 **Revisar estratégia** - A abordagem atual pode não estar funcionando
                            - 🤝 **Buscar suporte** - Solicitar ajuda da gestão ou colegas
                            - 📚 **Capacitação** - Considerar treinamento adicional
                            - ⏰ **Reagendamento** - Avaliar se o prazo é realista
                            """)
                        elif progress < 50:
                            st.markdown("""
                            - ⚡ **Acelerar ritmo** - Intensificar esforços nas atividades principais
                            - 🎯 **Focar prioridades** - Concentrar em tarefas de maior impacto
                            - 📞 **Comunicação** - Manter gestão informada sobre desafios
                            - 🔧 **Otimizar processos** - Buscar eficiências operacionais
                            """)
                        elif progress < 80:
                            st.markdown("""
                            - 📈 **Manter progresso** - Continuar com a estratégia atual
                            - 🔍 **Monitorar de perto** - Acompanhar indicadores regularmente
                            - 🚀 **Últimos 20%** - Preparar para o sprint final
                            """)
                        else:
                            st.markdown("""
                            - 🎯 **Finalizar com qualidade** - Foco na entrega final
                            - 📝 **Documentar aprendizados** - Registrar boas práticas
                            - 🏆 **Celebrar conquista** - Reconhecer o bom trabalho
                            """)
                        
                        # Formulário para adicionar observações
                        with st.form("individual_observations"):
                            st.markdown("#### 📝 Diagnóstico Individual da Meta")
                            st.markdown("Responda às perguntas abaixo para gerar um diagnóstico específico desta meta:")
                            
                            col_q1, col_q2 = st.columns(2)
                            
                            with col_q1:
                                q1 = st.radio(
                                    "A meta foi percebida como realista e possível de atingir?",
                                    ["Sim", "Não"],
                                    key="q1"
                                )
                                
                                q2 = st.radio(
                                    "Os recursos disponíveis foram suficientes para a execução da meta?",
                                    ["Sim", "Não"],
                                    key="q2"
                                )
                                
                                q3 = st.radio(
                                    "Há sinais de engajamento ou motivação ao longo do período?",
                                    ["Sim", "Não"],
                                    key="q3"
                                )
                                
                                q4 = st.radio(
                                    "Houve sinais de cansaço excessivo ou sobrecarga?",
                                    ["Sim", "Não"],
                                    key="q4"
                                )
                            
                            with col_q2:
                                q5 = st.radio(
                                    "O acompanhamento e o feedback foram oferecidos com regularidade?",
                                    ["Sim", "Não"],
                                    key="q5"
                                )
                                
                                q6 = st.radio(
                                    "As expectativas e objetivos da meta estavam claros desde o início?",
                                    ["Sim", "Não"],
                                    key="q6"
                                )
                                
                                q7 = st.radio(
                                    "Houve mudanças ou imprevistos no período da meta?",
                                    ["Sim", "Não"],
                                    key="q7"
                                )
                                
                                q8 = st.radio(
                                    "O funcionário participou da definição da meta?",
                                    ["Sim", "Não"],
                                    key="q8"
                                )
                            
                            if st.form_submit_button("🔍 Gerar Diagnóstico Individual"):
                                # Gerar diagnóstico baseado nas respostas
                                diagnoses = []
                                suggestions = []
                                
                                # Análise das respostas
                                if q1 == 'Não':
                                    diagnoses.append("Meta pode ser irrealista")
                                    suggestions.append("Reavalie a meta junto ao funcionário para garantir que esteja adequada ao tempo e ao escopo.")
                                
                                if q2 == 'Não':
                                    diagnoses.append("Falta de recursos")
                                    suggestions.append("Verifique se há necessidade de suporte adicional, como ferramentas, tempo ou equipe.")
                                
                                if q3 == 'Não':
                                    diagnoses.append("Baixa motivação")
                                    suggestions.append("Agende uma conversa para entender o que pode estar afetando a motivação e como apoiar melhor.")
                                
                                if q4 == 'Sim':
                                    diagnoses.append("Possível burnout")
                                    suggestions.append("Considere redistribuir tarefas ou revisar prazos para evitar esgotamento.")
                                
                                if q5 == 'Não':
                                    diagnoses.append("Falta de feedback")
                                    suggestions.append("Estabeleça checkpoints periódicos para fortalecer o alinhamento e o suporte.")
                                
                                if q6 == 'Não':
                                    diagnoses.append("Falta de clareza")
                                    suggestions.append("Reforce os critérios de sucesso e prazos de forma objetiva com o funcionário.")
                                
                                if q7 == 'Sim':
                                    diagnoses.append("Ocorreram imprevistos")
                                    suggestions.append("Considere adaptar prazos ou prioridades diante de imprevistos relevantes.")
                                
                                if q8 == 'Não':
                                    diagnoses.append("Meta imposta sem participação")
                                    suggestions.append("Envolva o funcionário na construção das metas para aumentar clareza e comprometimento.")
                                
                                # Compilar diagnóstico final
                                if diagnoses:
                                    final_diagnosis = "DIAGNÓSTICO AUTOMÁTICO:\n• " + "\n• ".join(diagnoses)
                                    final_suggestions = "SUGESTÕES AUTOMÁTICAS:\n• " + "\n• ".join(suggestions)
                                else:
                                    final_diagnosis = "DIAGNÓSTICO AUTOMÁTICO:\n• Nenhum problema crítico identificado. Meta apresenta boas condições de execução."
                                    final_suggestions = "SUGESTÕES AUTOMÁTICAS:\n• Continue com a estratégia atual e mantenha o acompanhamento regular."
                                
                                # Salvar no banco de dados
                                try:
                                    gestor.update_meta(
                                        meta_id,
                                        diagnosis=final_diagnosis,
                                        suggestions=final_suggestions
                                    )
                                    st.success("✅ Diagnóstico individual gerado e salvo com sucesso!")
                                except Exception as e:
                                    st.error(f"Erro ao salvar diagnóstico: {e}")
                                
                                # Exibir resultado do diagnóstico imediatamente
                                st.markdown("---")
                                st.markdown("### 📋 Resultado do Diagnóstico Individual")
                                
                                if diagnoses:
                                    st.markdown("#### 🚨 Problemas Identificados:")
                                    for i, diagnosis in enumerate(diagnoses):
                                        if "irrealista" in diagnosis.lower():
                                            st.error(f"🎯 {diagnosis}")
                                        elif "falta de recursos" in diagnosis.lower():
                                            st.warning(f"🔧 {diagnosis}")
                                        elif "baixa motivação" in diagnosis.lower():
                                            st.warning(f"😔 {diagnosis}")
                                        elif "burnout" in diagnosis.lower():
                                            st.error(f"😰 {diagnosis}")
                                        elif "falta de feedback" in diagnosis.lower():
                                            st.warning(f"📢 {diagnosis}")
                                        elif "falta de clareza" in diagnosis.lower():
                                            st.warning(f"❓ {diagnosis}")
                                        elif "imprevistos" in diagnosis.lower():
                                            st.info(f"⚡ {diagnosis}")
                                        elif "imposta" in diagnosis.lower():
                                            st.warning(f"🤝 {diagnosis}")
                                        else:
                                            st.info(f"📌 {diagnosis}")
                                    
                                    st.markdown("#### 💡 Ações Recomendadas:")
                                    for i, suggestion in enumerate(suggestions):
                                        st.markdown(f"**{i+1}.** {suggestion}")
                                    
                                    # Score de risco
                                    risk_score = len(diagnoses)
                                    total_questions = 8
                                    risk_percentage = (risk_score / total_questions) * 100
                                    
                                    st.markdown("#### 📊 Nível de Risco da Meta")
                                    if risk_percentage == 0:
                                        st.success(f"🟢 **Baixo Risco** - {risk_score}/8 problemas identificados")
                                        st.info("Meta apresenta condições favoráveis para o sucesso.")
                                    elif risk_percentage <= 25:
                                        st.info(f"🟡 **Risco Moderado** - {risk_score}/8 problemas identificados")
                                        st.warning("Alguns pontos de atenção identificados.")
                                    elif risk_percentage <= 50:
                                        st.warning(f"🟠 **Risco Alto** - {risk_score}/8 problemas identificados")
                                        st.error("Vários fatores podem comprometer o sucesso da meta.")
                                    else:
                                        st.error(f"🔴 **Risco Crítico** - {risk_score}/8 problemas identificados")
                                        st.error("Meta em situação crítica. Intervenção urgente necessária.")
                                        
                                else:
                                    st.success("🌟 **Excelente!** Nenhum problema crítico identificado.")
                                    st.info("A meta apresenta boas condições de execução. Continue com a estratégia atual.")

            else:
                st.info("Nenhuma meta encontrada para diagnóstico.")
                
        except Exception as e:
            st.error(f"Erro ao gerar diagnóstico: {e}")

    with tab5:
        st.subheader("Relatórios")
        
        try:
            df = gestor.get_all_metas()
            
            if not df.empty:
                # Seleção do tipo de relatório
                report_type = st.selectbox(
                    "Tipo de Relatório:",
                    ["Relatório Geral", "Por Departamento", "Por Status", "Por Funcionário"]
                )
                
                if report_type == "Relatório Geral":
                    st.markdown("### 📋 Relatório Geral de Metas")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Resumo Executivo:**")
                        total_metas = len(df)
                        concluidas = len(df[df['status'] == 'Concluída'])
                        em_andamento = len(df[df['status'] == 'Em Andamento'])
                        atrasadas = len(df[df['status'] == 'Atrasada'])
                        nao_concluidas = len(df[df['status'] == 'Não Concluída'])
                        
                        st.write(f"• **Total de Metas:** {total_metas}")
                        st.write(f"• **Concluídas:** {concluidas} ({(concluidas/total_metas*100):.1f}%)")
                        st.write(f"• **Em Andamento:** {em_andamento} ({(em_andamento/total_metas*100):.1f}%)")
                        st.write(f"• **Atrasadas:** {atrasadas} ({(atrasadas/total_metas*100):.1f}%)")
                        st.write(f"• **Não Concluídas:** {nao_concluidas} ({(nao_concluidas/total_metas*100):.1f}%)")
                    
                    with col2:
                        st.markdown("**Indicadores de Performance:**")
                        avg_progress = df['progress'].mean()
                        success_rate = (concluidas / total_metas) * 100
                        
                        st.write(f"• **Progresso Médio:** {avg_progress:.1f}%")
                        st.write(f"• **Taxa de Sucesso:** {success_rate:.1f}%")
                        
                        # Departamento com melhor performance
                        dept_performance = df.groupby('department')['progress'].mean()
                        best_dept = dept_performance.idxmax()
                        best_score = dept_performance.max()
                        
                        st.write(f"• **Melhor Departamento:** {best_dept} ({best_score:.1f}%)")
                
                elif report_type == "Por Departamento":
                    st.markdown("### 🏢 Relatório por Departamento")
                    
                    dept_stats = df.groupby('department').agg({
                        'id': 'count',
                        'progress': ['mean', 'min', 'max'],
                        'status': lambda x: (x == 'Concluída').sum()
                    }).round(1)
                    
                    dept_stats.columns = ['Total Metas', 'Progresso Médio', 'Progresso Mín', 'Progresso Máx', 'Concluídas']
                    dept_stats['Taxa Sucesso %'] = (dept_stats['Concluídas'] / dept_stats['Total Metas'] * 100).round(1)
                    
                    st.dataframe(dept_stats, use_container_width=True)
                
                elif report_type == "Por Status":
                    st.markdown("### 📊 Relatório por Status")
                    
                    status_stats = df.groupby('status').agg({
                        'id': 'count',
                        'progress': ['mean', 'min', 'max']
                    }).round(1)
                    
                    status_stats.columns = ['Quantidade', 'Progresso Médio', 'Progresso Mín', 'Progresso Máx']
                    status_stats['Percentual %'] = (status_stats['Quantidade'] / len(df) * 100).round(1)
                    
                    st.dataframe(status_stats, use_container_width=True)
                
                elif report_type == "Por Funcionário":
                    st.markdown("### 👤 Relatório por Funcionário")
                    
                    employee_stats = df.groupby('employee_name').agg({
                        'id': 'count',
                        'progress': ['mean', 'min', 'max'],
                        'status': lambda x: (x == 'Concluída').sum()
                    }).round(1)
                    
                    employee_stats.columns = ['Total Metas', 'Progresso Médio', 'Progresso Mín', 'Progresso Máx', 'Concluídas']
                    employee_stats['Taxa Sucesso %'] = (employee_stats['Concluídas'] / employee_stats['Total Metas'] * 100).round(1)
                    
                    st.dataframe(employee_stats, use_container_width=True)
                
                # Opção de download
                st.markdown("---")
                st.markdown("### 💾 Download de Dados")
                
                if st.button("📥 Baixar Dados Completos (CSV)"):
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="Clique aqui para download",
                        data=csv,
                        file_name=f"metas_completo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                    
            else:
                st.info("Nenhuma meta encontrada para gerar relatórios.")
                
        except Exception as e:
            st.error(f"Erro ao gerar relatório: {e}")

if __name__ == "__main__":
    main()
