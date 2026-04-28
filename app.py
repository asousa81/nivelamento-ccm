import streamlit as st
import sqlite3
import json
import pandas as pd
import plotly.graph_objects as go
import random
from datetime import datetime

# ==========================================
# CONFIGURAÇÃO E DADOS
# ==========================================
st.set_page_config(page_title="Nivelamento CCM", page_icon="📖", layout="wide")

MODULES = [
    {"id": 1, "name": "I. Revelação e Deus", "shortName": "Deus & Bíblia"},
    {"id": 2, "name": "II. Mundo Espiritual", "shortName": "Mundo Espiritual"},
    {"id": 3, "name": "III. Cristo e Homem", "shortName": "Cristo & Homem"},
    {"id": 4, "name": "IV. Soteriologia", "shortName": "Soteriologia"},
    {"id": 5, "name": "V. A Igreja", "shortName": "Igreja & Vida"},
    {"id": 6, "name": "VI. Escatologia", "shortName": "Escatologia"}
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
# BANCO DE DADOS
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

# ==========================================
# INTERFACE
# ==========================================
def main():
    init_db()
    st.sidebar.title("Navegação CCM")
    menu = st.sidebar.radio("Selecione a tela:", ("🎓 Portal do Aluno", "📊 Painel do Professor"))

    if menu == "🎓 Portal do Aluno":
        st.title("📖 Teste de Nivelamento")
        with st.form("prova"):
            answers = {}
            for i, q in enumerate(QUESTIONS):
                ans = st.radio(f"{i+1}. {q['text']}", q['options'], key=f"q_{i}")
                answers[str(i)] = q['options'].index(ans)
            if st.form_submit_button("Enviar Respostas", use_container_width=True):
                save_response(answers)
                st.success("Enviado com sucesso!")

    else:
        st.title("📊 Dashboard Docente")
        responses = get_responses()
        
        # Pesos do Pastor
        st.sidebar.header("Expectativa")
        weights = {m['id']: st.sidebar.slider(m['shortName'], 1, 5, 4) for m in MODULES}
        
        if not responses:
            st.warning("Nenhuma resposta no banco de dados.")
        else:
            # Cálculos
            stats = []
            for m in MODULES:
                m_qs = [i for i, q in enumerate(QUESTIONS) if q['mod'] == m['id']]
                total = len(m_qs) * len(responses)
                correct = sum(1 for r in responses for idx in m_qs if r[str(idx)] == QUESTIONS[idx]['correct'])
                stats.append({
                    "name": m["shortName"], 
                    "class": (correct/total*100) if total > 0 else 0,
                    "pastor": (weights[m['id']]/5*100)
                })
            
            df = pd.DataFrame(stats)
            
            # Radar Chart
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(r=df['pastor'].tolist()+[df['pastor'][0]], theta=df['name'].tolist()+[df['name'][0]], fill='toself', name='Pastor', line=dict(dash='dash', color='orange')))
            fig.add_trace(go.Scatterpolar(r=df['class'].tolist()+[df['class'][0]], theta=df['name'].tolist()+[df['name'][0]], fill='toself', name='Turma', line=dict(color='blue')))
            fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])))
            st.plotly_chart(fig)

if __name__ == "__main__":
    main()
