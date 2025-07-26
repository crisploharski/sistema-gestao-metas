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
        
        try:
            df = gestor.get_all_metas()
            
            if not df.empty:
                # Análise geral
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
