import streamlit as st
import sqlite3
import json
import pandas as pd
import plotly.graph_objects as go
import random
from datetime import datetime

# ==========================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(
    page_title="CCM - Nivelamento Teológico",
    page_icon="🛡️",
    layout="wide"
)

# SENHA DO PROFESSOR (Altere aqui se desejar)
SENHA_PROFESSOR = "ccm2026@TG"

# ==========================================
# DADOS DO CURSO (Wayne Grudem - Bases da Fé)
# ==========================================
MODULES = [
    {"id": 1, "name": "I. Revelação e Deus", "shortName": "Bíblia & Trindade"},
    {"id": 2, "name": "II. Criador e Mundo Espiritual", "shortName": "Mundo Espiritual"},
    {"id": 3, "name": "III. Homem e Cristo", "shortName": "Homem & Cristo"},
    {"id": 4, "name": "IV. Soteriologia", "shortName": "Salvação"},
    {"id": 5, "name": "V. Eclesiologia", "shortName": "Igreja & Vida"},
    {"id": 6, "name": "VI. Escatologia", "shortName": "Últimas Coisas"}
]

QUESTIONS = [
    {"mod": 1, "text": "O que a Teologia Sistemática quer dizer quando afirma a 'suficiência' da Bíblia?", "options": ["A Bíblia contém tudo o que Deus quis nos dizer para a salvação e a vida cristã perfeita.", "A Bíblia precisa ser complementada por novas revelações.", "A Bíblia falha em questões morais modernas.", "A Bíblia contém todas as verdades científicas."], "correct": 0},
    {"mod": 1, "text": "Qual das afirmações abaixo expressa corretamente a doutrina bíblica da Trindade?", "options": ["Deus é uma única pessoa que muda de forma.", "Existem três deuses distintos em harmonia.", "Há um só Deus em três pessoas distintas, cada uma plenamente Deus.", "O Pai criou o Filho e o Espírito Santo."], "correct": 2},
    {"mod": 2, "text": "Segundo a doutrina da Providência, como Deus se relaciona com o mundo?", "options": ["Criou e deixou rodar sozinho.", "Apenas reage ao que os humanos fazem.", "Sustenta, concorre e governa ativamente todas as coisas.", "Controla só as coisas boas."], "correct": 2},
    {"mod": 2, "text": "Qual é a principal arma do cristão na Batalha Espiritual?", "options": ["Gritar com demônios territoriais.", "Submeter-se a Deus e resistir ao diabo na Verdade.", "Usar objetos ungidos.", "Ignorar o mundo espiritual."], "correct": 1},
    {"mod": 3, "text": "O que herdamos de Adão no 'Pecado Original'?", "options": ["Apenas um mau exemplo.", "Culpa legal e natureza corrompida.", "Maldições financeiras.", "Fraqueza física apenas."], "correct": 1},
    {"mod": 3, "text": "Sobre a natureza de Jesus (União Hipostática):", "options": ["50% Deus, 50% homem.", "Plenamente Deus e plenamente homem, em uma pessoa.", "Homem que virou divino.", "Espírito que parecia humano."], "correct": 1},
    {"mod": 4, "text": "O que ocorreu através da 'Expiação Substitutiva Penal'?", "options": ["Cristo recebeu nossa culpa e suportou a ira de Deus.", "Apenas deu exemplo moral.", "Pagou resgate a Satanás.", "Anulou a justiça de Deus."], "correct": 0},
    {"mod": 4, "text": "Na Ordem da Salvação, o que é a Regeneração?", "options": ["Levantar a mão no culto.", "Mudar de comportamento.", "Batismo nas águas.", "Ato secreto do Espírito que dá nova vida para crermos."], "correct": 3},
    {"mod": 5, "text": "Qual a diferença entre Justificação e Santificação?", "options": ["Justificação é melhorar; Santificação é o momento da salvação.", "Justificação é declaração legal instantânea; Santificação é processo contínuo.", "São a mesma coisa.", "Justificação é graça, Santificação garante a salvação."], "correct": 1},
    {"mod": 5, "text": "O que é a 'Igreja Invisível'?", "options": ["Igreja sem templo físico.", "Crentes anônimos.", "Todos os verdadeiros crentes, conhecidos perfeitamente só por Deus.", "Anjos que protegem o culto."], "correct": 2},
    {"mod": 6, "text": "O que acontece com a alma do cristão um minuto após a morte?", "options": ["Dorme inconsciente no túmulo.", "Vai para o purgatório.", "Fica vagando pela terra.", "Vai consciente para a presença do Senhor."], "correct": 3},
    {"mod": 6, "text": "Qual a esperança final do cristão (Novo Céu e Nova Terra)?", "options": ["Espíritos flutuando no espaço.", "Reencarnações sucessivas.", "Corpos físicos glorificados em um universo material redimido.", "Salvação universal de todos."], "correct": 2}
]

# ==========================================
# GESTÃO DO BANCO DE DADOS
# ==========================================
def init_db():
    conn = sqlite3.connect('ccm_responses.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS responses (id INTEGER PRIMARY KEY AUTOINCREMENT, answers TEXT, timestamp DATETIME)')
    conn.commit()
    conn.close()

def save_response(answers_dict):
    conn = sqlite3.connect('ccm_responses.db')
    c = conn.cursor()
    c.execute('INSERT INTO responses (answers, timestamp) VALUES (?, ?)', (json.dumps(answers_dict), datetime.now()))
    conn.commit()
    conn.close()

def get_responses():
    conn = sqlite3.connect('ccm_responses.db')
    c = conn.cursor()
    c.execute('SELECT answers FROM responses')
    rows = c.fetchall()
    conn.close()
    return [json.loads(row[0]) for row in rows]

def clear_db():
    conn = sqlite3.connect('ccm_responses.db')
    c = conn.cursor()
    c.execute('DELETE FROM responses')
    conn.commit()
    conn.close()

def generate_mock_data():
    conn = sqlite3.connect('ccm_responses.db')
    c = conn.cursor()
    for _ in range(20):
        ans = {}
        for i, q in enumerate(QUESTIONS):
            # Lacuna proposital nos módulos 3 e 5
            chance = 0.45 if q["mod"] in [3, 5] else 0.8
            ans[str(i)] = q["correct"] if random.random() < chance else random.choice([idx for idx in range(4) if idx != q["correct"]])
        c.execute('INSERT INTO responses (answers, timestamp) VALUES (?, ?)', (json.dumps(ans), datetime.now()))
    conn.commit()
    conn.close()

# ==========================================
# INTERFACE PRINCIPAL
# ==========================================
def main():
    init_db()
    
    # Barra Lateral
    # st.sidebar.image("https://quadrangular.org/wp-content/uploads/2022/09/logo-footer.png", width=120)
    with st.sidebar:
        # LINHA CORRIGIDA: O comentário e o bloco abaixo agora estão devidamente indentados
        try:
            st.image("logo_tg.JPG", width=150)
        except:
            st.markdown("<h1 style='text-align: center;'>📖</h1>", unsafe_allow_html=True)
            
    st.sidebar.title("CCM - IEQ Templo Gospel")
    menu = st.sidebar.selectbox("Navegação", ["Portal do Aluno", "Painel do Professor"])
    
    if menu == "Portal do Aluno":
        st.title("📝 Teste de Nivelamento")
        st.markdown("### Bases da Fé Cristã")
        st.write("Suas respostas ajudam o professor a planejar as aulas conforme a necessidade da turma.")
        
        with st.form("form_aluno"):
            user_answers = {}
            for i, q in enumerate(QUESTIONS):
                st.subheader(f"{i+1}. {q['text']}")
                choice = st.radio("Selecione a opção correta:", q['options'], key=f"ans_{i}", label_visibility="collapsed")
                user_answers[str(i)] = q['options'].index(choice)
                st.markdown("---")
            
            submit = st.form_submit_button("Enviar Avaliação", use_container_width=True)
            if submit:
                save_response(user_answers)
                st.balloons()
                st.success("Excelente! Sua avaliação foi enviada. Deus abençoe, pode fechar esta página.")

    else:
        st.title("📊 Painel de Gestão Docente")
        
        # Proteção por Senha
        pswd = st.sidebar.text_input("Palavra-passe:", type="password")
        if pswd != SENHA_PROFESSOR:
            if pswd == "":
                st.info("Insira a senha na barra lateral para ver os dados.")
            else:
                st.error("Senha Incorreta.")
            return

        # --- SEÇÃO AUTORIZADA ---
        responses = get_responses()
        
        # Configuração de Pesos na Lateral
        st.sidebar.markdown("---")
        st.sidebar.subheader("Expectativa Pastoral")
        st.sidebar.info("Peso de importância para cada módulo (1 a 5)")
        weights = {m['id']: st.sidebar.slider(m['shortName'], 1, 5, 4) for m in MODULES}

        if not responses:
            st.warning("O banco de dados está vazio. Aguarde os alunos responderem.")
            if st.button("Simular Turma (20 alunos)"):
                generate_mock_data()
                st.rerun()
        else:
            # Cálculos de Estatística
            rows = []
            for m in MODULES:
                m_qs = [i for i, q in enumerate(QUESTIONS) if q['mod'] == m['id']]
                total_pos = len(m_qs) * len(responses)
                hits = sum(1 for r in responses for idx in m_qs if r[str(idx)] == QUESTIONS[idx]['correct'])
                
                class_perc = (hits / total_pos * 100)
                pastor_perc = (weights[m['id']] / 5 * 100)
                gap = max(0, pastor_perc - class_perc)
                
                rows.append({
                    "Módulo": m['name'],
                    "Sigla": m['shortName'],
                    "Turma (%)": class_perc,
                    "Pastor (%)": pastor_perc,
                    "Gap": gap
                })
            
            df = pd.DataFrame(rows)
            
            # 1. MÉTRICAS DE TOPO
            m1, m2, m3 = st.columns(3)
            m1.metric("Alunos na Base", len(responses))
            
            avg_class = df['Turma (%)'].mean()
            m2.metric("Média da Turma", f"{avg_class:.1f}%")
            
            crit = df.loc[df['Gap'].idxmax()]
            m3.metric("Módulo Crítico", crit['Sigla'], f"{crit['Gap']:.1f}% de defasagem", delta_color="inverse")
            
            st.markdown("---")

            # 2. ABAS DE CONTEÚDO
            tab1, tab2 = st.tabs(["🎯 Gráfico de Radar", "🛠️ Detalhamento & Manutenção"])
            
            with tab1:
                col_chart, col_text = st.columns([2, 1])
                
                with col_chart:
                    # Gráfico Radar
                    categories = df['Sigla'].tolist()
                    fig = go.Figure()
                    
                    fig.add_trace(go.Scatterpolar(
                        r=df['Pastor (%)'].tolist() + [df['Pastor (%)'][0]],
                        theta=categories + [categories[0]],
                        fill='toself', name='Expectativa', line=dict(color='#ff9800', dash='dash')
                    ))
                    fig.add_trace(go.Scatterpolar(
                        r=df['Turma (%)'].tolist() + [df['Turma (%)'][0]],
                        theta=categories + [categories[0]],
                        fill='toself', name='Realidade', line=dict(color='#1f77b4', width=3)
                    ))
                    
                    fig.update_layout(
                        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                        margin=dict(l=40, r=40, t=20, b=20)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col_text:
                    st.subheader("Análise Pedagógica")
                    st.write(f"O módulo **{crit['Módulo']}** é o que apresenta maior distanciamento da expectativa ministerial.")
                    st.info(f"Recomendação: Inicie o curso focando nos fundamentos de {crit['Sigla']}, pois a turma demonstrou menor clareza nesta área.")

            with tab2:
                st.subheader("Aproveitamento por Tema")
                for _, row in df.iterrows():
                    cols = st.columns([2, 5, 1])
                    cols[0].write(f"**{row['Sigla']}**")
                    cols[1].progress(row['Turma (%)']/100)
                    cols[2].write(f"{row['Turma (%)']:.0f}%")
                
                st.markdown("---")
                st.subheader("⚠️ Zona de Manutenção")
                
                # Botão de Limpar com confirmação
                col_btn1, col_btn2 = st.columns(2)
                
                with col_btn1:
                    if st.button("Gerar +20 Alunos de Teste"):
                        generate_mock_data()
                        st.rerun()
                
                with col_btn2:
                    confirmar = st.checkbox("Confirmar que desejo apagar TUDO")
                    if st.button("🗑️ Limpar Banco de Dados", type="primary", disabled=not confirmar):
                        clear_db()
                        st.success("Banco de dados reiniciado!")
                        st.rerun()

if __name__ == "__main__":
    main()
