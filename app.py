import streamlit as st
import os
from dotenv import load_dotenv
from logic import extract_text_from_file, generate_quiz

# Load environment variables
load_dotenv()

# Page Config
st.set_page_config(
    page_title="Estudo Divertido 6º Ano",
    page_icon="📚",
    layout="centered"
)

# --- Session State Initialization ---
if 'quiz_data' not in st.session_state:
    st.session_state.quiz_data = None
if 'quiz_submitted' not in st.session_state:
    st.session_state.quiz_submitted = False
if 'quiz_id' not in st.session_state:
    st.session_state.quiz_id = 0

# --- UI Layout ---

# Sidebar
with st.sidebar:
    st.header("⚙️ Configurações")
    api_key_input = st.text_input("Gemini API Key", type="password", help="Cola aqui a tua chave da API do Google Gemini")

    # Check if API key is in env or input
    api_key = api_key_input if api_key_input else os.getenv("GOOGLE_API_KEY")

    if not api_key:
        st.warning("⚠️ Precisas de uma API Key para começar!")
        st.markdown("[Obter API Key](https://aistudio.google.com/app/apikey)")
    else:
        st.success("API Key pronta! 🚀")

    if st.button("Limpar Tudo"):
        st.session_state.quiz_data = None
        st.session_state.quiz_submitted = False
        st.rerun()

# Main Content
st.title("📚 Estudo Divertido - 6º Ano")
st.write("Olá! Vamos transformar os teus apontamentos num jogo de perguntas!")

# File Uploader
uploaded_file = st.file_uploader("Carrega o teu ficheiro (PDF ou Texto)", type=['txt', 'pdf'])

if uploaded_file:
    # Button to Generate Quiz
    if st.button("✨ Criar Novo Questionário", type="primary"):
        if not api_key:
            st.error("Por favor, insere a API Key nas configurações primeiro.")
        else:
            with st.spinner('A ler a matéria e a criar perguntas mágicas... 🤖'):
                text = extract_text_from_file(uploaded_file)
                if text:
                    quiz = generate_quiz(text, api_key)
                    if quiz:
                        st.session_state.quiz_data = quiz
                        st.session_state.quiz_submitted = False
                        st.session_state.quiz_id += 1 # Increment ID to reset widgets
                        st.rerun()
                    else:
                        st.error("Não foi possível criar o questionário. Verifica a tua API Key ou tenta novamente.")
                else:
                    st.error("Não consegui ler o ficheiro. Tenta outro.")

# Display Quiz
if st.session_state.quiz_data:
    st.divider()
    st.subheader("📝 Responde às perguntas:")

    # Form container
    with st.form(key=f"quiz_form_{st.session_state.quiz_id}"):
        user_answers = {}
        for i, q in enumerate(st.session_state.quiz_data):
            st.markdown(f"**{i+1}. {q['pergunta']}**")

            # Using radio button for options
            # We map the index to the options list
            user_answers[i] = st.radio(
                "Escolhe uma opção:",
                options=range(len(q['opcoes'])),
                format_func=lambda x: q['opcoes'][x],
                key=f"q_{st.session_state.quiz_id}_{i}",
                label_visibility="collapsed",
                index=None # No default selection
            )
            st.write("") # Spacing

        submitted = st.form_submit_button("✅ Corrigir Respostas")

        if submitted:
            st.session_state.quiz_submitted = True

    # Results Display (Shown after submission)
    if st.session_state.quiz_submitted:
        st.divider()
        st.header("📊 Resultados")

        correct_count = 0
        total_questions = len(st.session_state.quiz_data)

        for i, q in enumerate(st.session_state.quiz_data):
            # Retrieve answer from session state using the key we defined
            user_choice = st.session_state.get(f"q_{st.session_state.quiz_id}_{i}")

            st.markdown(f"**Pergunta {i+1}:** {q['pergunta']}")

            if user_choice is None:
                st.warning("⚠️ Não respondeste a esta pergunta.")
                st.info(f"💡 A resposta correta era: **{q['opcoes'][q['resposta_correta']]}**")
                with st.expander("Ver explicação"):
                    st.write(q['explicacao'])
            elif user_choice == q['resposta_correta']:
                st.success(f"✅ Correto! Escolheste: {q['opcoes'][user_choice]}")
                correct_count += 1
                with st.expander("Ver explicação"):
                     st.write(q['explicacao'])
            else:
                st.error(f"❌ Incorreto. Escolheste: {q['opcoes'][user_choice]}")
                st.info(f"💡 A resposta correta era: **{q['opcoes'][q['resposta_correta']]}**")
                with st.expander("Ver explicação"):
                    st.write(q['explicacao'])

            st.write("---")

        score = (correct_count / total_questions) * 100
        st.metric(label="Pontuação Final", value=f"{score:.0f}%")

        if score == 100:
            st.balloons()
            st.markdown("### 🎉 Parabéns! És um génio! 🎉")
        elif score >= 50:
            st.markdown("### 👍 Bom trabalho! Continua a estudar!")
        else:
            st.markdown("### 💪 Não desistas! Tenta outra vez.")
