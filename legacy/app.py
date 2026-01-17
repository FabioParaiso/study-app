import streamlit as st
import os
from dotenv import load_dotenv
from logic import extract_text_from_file, generate_quiz
from storage import save_study_material, load_study_material, clear_study_material

# Load environment variables
load_dotenv()

# Page Config with custom title and layout
st.set_page_config(
    page_title="Quiz Mágico de Estudo",
    page_icon="🧠",
    layout="centered"
)

# --- Custom CSS for "React-like" aesthetics ---
st.markdown("""
<style>
    /* Global Background */
    .stApp {
        background: linear-gradient(to bottom right, #f5f3ff, #e0e7ff);
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    }
    
    /* Main container styling - attempting to center and card-ify content */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 5rem;
        max-width: 800px;
    }

    /* Titles */
    h1 {
        color: #4338ca; /* Indigo 700 */
        font-weight: 800;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    h3 {
        color: #3730a3; /* Indigo 800 */
        font-weight: 600;
    }
    
    p {
        color: #4b5563; /* Gray 600 */
        font-size: 1.1rem;
    }

    /* Card Containers */
    div[data-testid="stVerticalBlock"] > div[style*="border"] {
        background-color: white;
        border-radius: 24px;
        padding: 2rem;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
        border: none !important;
    }

    /* Buttons */
    .stButton button {
        border-radius: 12px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        border: none;
    }

    /* Primary Buttons (Gradient) */
    .stButton button[kind="primary"] {
        background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
        color: white;
        box-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.3);
    }
    .stButton button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 10px -1px rgba(79, 70, 229, 0.4);
    }

    /* Secondary Buttons (Options) */
    .stButton button[kind="secondary"] {
        background-color: white;
        border: 2px solid #e2e8f0;
        color: #1e293b;
        text-align: left;
        display: flex;
        justify-content: flex-start;
        padding-left: 1.5rem;
    }
    .stButton button[kind="secondary"]:hover {
        border-color: #6366f1;
        background-color: #eef2ff;
        color: #4338ca;
    }

    /* Input Fields */
    .stTextInput input, .stTextArea textarea {
        border-radius: 12px;
        border: 2px solid #e2e8f0;
        padding: 1rem;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #6366f1;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.2);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        font-weight: bold;
        color: #64748b;
    }
    .stTabs [aria-selected="true"] {
        color: #4f46e5;
    }

    /* Progress Bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #6366f1, #a855f7);
    }

    /* Text Preview Box */
    .text-preview {
        background: #f8fafc;
        padding: 1.5rem;
        border-radius: 16px;
        border-left: 4px solid #6366f1;
        font-family: monospace;
        font-size: 0.9rem;
        color: #334155;
        margin-bottom: 2rem;
    }

    /* Feedback Box */
    .feedback-box {
        padding: 2rem;
        border-radius: 16px;
        margin-top: 1.5rem;
        animation: slideUp 0.4s ease-out;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
    }
    @keyframes slideUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
</style>
""", unsafe_allow_html=True)

# --- Session State Management ---
if 'game_state' not in st.session_state:
    st.session_state.game_state = 'intro' # intro, playing, results
if 'quiz_data' not in st.session_state:
    st.session_state.quiz_data = []
if 'current_q_index' not in st.session_state:
    st.session_state.current_q_index = 0
if 'score' not in st.session_state:
    st.session_state.score = 0
if 'selected_option' not in st.session_state:
    st.session_state.selected_option = None # None or index
if 'show_explanation' not in st.session_state:
    st.session_state.show_explanation = False

# --- Helper Functions ---
def reset_game():
    st.session_state.game_state = 'intro'
    st.session_state.quiz_data = []
    st.session_state.current_q_index = 0
    st.session_state.score = 0
    st.session_state.selected_option = None
    st.session_state.show_explanation = False

def handle_option_click(index, correct_index):
    st.session_state.selected_option = index
    st.session_state.show_explanation = True
    if index == correct_index:
        st.session_state.score += 1

def next_question():
    if st.session_state.current_q_index < len(st.session_state.quiz_data) - 1:
        st.session_state.current_q_index += 1
        st.session_state.selected_option = None
        st.session_state.show_explanation = False
    else:
        st.session_state.game_state = 'results'

def load_from_storage():
    """Tries to load saved material."""
    saved_data = load_study_material()
    if saved_data and 'text' in saved_data:
        return saved_data['text'], saved_data.get('source', 'Matéria Guardada')
    return None, None

def clear_storage_and_reset():
    clear_study_material()
    reset_game()
    st.rerun()

# --- UI Render ---

# Sidebar for API Key
with st.sidebar:
    st.header("⚙️ Configurações")
    api_key_input = st.text_input("OpenAI API Key", type="password", help="Chave da API OpenAI")
    api_key = api_key_input if api_key_input else os.getenv("OPENAI_API_KEY")
    
    st.divider()
    if st.button("🗑️ Apagar Matéria Guardada"):
        clear_storage_and_reset()
        st.success("Matéria apagada!")
    
    if st.button("🔄 Reiniciar App"):
        reset_game()
        st.rerun()

# 1. INTRO SCREEN
if st.session_state.game_state == 'intro':
    st.markdown("<div style='text-align: center; margin-bottom: 2rem;'><h1>🧠 Quiz Mágico de Estudo</h1><p>Transforma os teus apontamentos num jogo!</p></div>", unsafe_allow_html=True)
    
    # Check for saved material
    saved_text, saved_source = load_from_storage()
    
    # If we have saved text, prioritize showing that unless user wants to change
    has_saved_material = saved_text is not None
    
    # Logic: If we have saved material, we can skip upload IF user chooses to "Use Saved"
    # But usually, we might just auto-load it into a state or show a card "Resume Study?".
    # Let's auto-load into the context but let user override.
    
    if has_saved_material:
        with st.container(border=True):
            st.markdown(f"### 📂 A continuar estudo de: **{saved_source}**")
            st.markdown(f"<div class='text-preview'>{saved_text[:200]}...</div>", unsafe_allow_html=True)
            
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("✨ Criar Novo Quiz com Isto", type="primary", use_container_width=True):
                    # Proceed with saved text
                    if not api_key:
                        st.error("⚠️ Falta a API Key!")
                    else:
                        with st.spinner("🤖 A gerar perguntas..."):
                            quiz = generate_quiz(saved_text, api_key)
                            if quiz:
                                st.session_state.quiz_data = quiz
                                st.session_state.game_state = 'playing'
                                st.rerun()
                            else:
                                st.error("Erro ao gerar. Tenta novamente.")
            with col_b:
                if st.button("❌ Escolher Outra Matéria", use_container_width=True):
                    clear_storage_and_reset()

    else:
        # Standard Upload Flow
        with st.container(border=True):
            st.markdown("### 1. Carrega a tua matéria 📚")
            
            tab1, tab2 = st.tabs(["📄 Upload Ficheiro", "✍️ Colar Texto"])
            
            text_content = None
            source_name = "Texto Colado"
            
            with tab1:
                uploaded_file = st.file_uploader("PDF ou Texto", type=['pdf', 'txt'])
                if uploaded_file:
                    text_content = extract_text_from_file(uploaded_file)
                    source_name = uploaded_file.name
            
            with tab2:
                raw_text = st.text_area("Cola aqui o teu resumo:", height=150)
                if raw_text:
                    text_content = raw_text

            st.markdown("### 2. Cria o Quiz ✨")
            
            generate_btn = st.button("🚀 Gerar Perguntas Mágicas", type="primary", use_container_width=True)
            
            if generate_btn:
                if not api_key:
                    st.error("⚠️ Falta a API Key nas configurações!")
                elif not text_content:
                    st.warning("⚠️ Precisas de carregar um ficheiro ou escrever texto primeiro.")
                else:
                    # SAVE MATERIAL HERE
                    save_study_material(text_content, source_name)
                    
                    with st.spinner("🤖 A ler a matéria e a preparar o teste..."):
                        quiz = generate_quiz(text_content, api_key)
                        if quiz:
                            st.session_state.quiz_data = quiz
                            st.session_state.game_state = 'playing'
                            st.rerun()
                        else:
                            st.error("Ups! Ocorreu um erro. Tenta novamente.")

# 2. PLAYING SCREEN
elif st.session_state.game_state == 'playing':
    q_data = st.session_state.quiz_data
    curr_idx = st.session_state.current_q_index
    question = q_data[curr_idx]
    
    # Progress Bar
    progress = (curr_idx) / len(q_data)
    st.progress(progress, text=f"Pergunta {curr_idx + 1} de {len(q_data)}")
    
    with st.container(border=True):
        st.markdown(f"### {question['pergunta']}")
        
        # Options
        opts = question['opcoes']
        correct_idx = question['resposta_correta']
        
        for i, opt in enumerate(opts):
            # Button styling logic
            btn_label = opt
            btn_type = "secondary"
            disabled = False
            
            if st.session_state.show_explanation:
                disabled = True
                if i == correct_idx:
                    btn_label = f"✅ {opt}"
                    btn_type = "primary"
                elif i == st.session_state.selected_option:
                    btn_label = f"❌ {opt}"
            
            if not st.session_state.show_explanation:
                if st.button(opt, key=f"q{curr_idx}_opt{i}", use_container_width=True):
                    handle_option_click(i, correct_idx)
                    st.rerun()
            else:
                st.button(btn_label, key=f"q{curr_idx}_opt{i}_disabled", disabled=True, type=btn_type, use_container_width=True)

    # Explanation Area
    if st.session_state.show_explanation:
        feedback_color = "green" if st.session_state.selected_option == correct_idx else "orange"
        feedback_title = "Excelente! 🎉" if st.session_state.selected_option == correct_idx else "Quase! 📚"
        
        st.markdown(f"""
        <div class="feedback-box" style="background-color: {'#dcfce7' if feedback_color == 'green' else '#ffedd5'}; color: {'#166534' if feedback_color == 'green' else '#9a3412'};">
            <h3>{feedback_title}</h3>
            <p>{question['explicacao']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("")
        if st.button("➡️ Próxima Pergunta" if curr_idx < len(q_data)-1 else "🏆 Ver Resultados", type="primary", use_container_width=True):
            next_question()
            st.rerun()

# 3. RESULTS SCREEN
elif st.session_state.game_state == 'results':
    score = st.session_state.score
    total = len(st.session_state.quiz_data)
    percent = int((score / total) * 100)
    
    st.balloons()
    
    with st.container(border=True):
        st.markdown("<h2 style='text-align: center;'>Quiz Terminado! 🏁</h2>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.metric("Pontuação Final", f"{score}/{total}", f"{percent}%")
        
        if percent == 100:
            msg = "🌟 Fantástico! És um génio!"
        elif percent >= 70:
            msg = "👏 Muito bom! Continua assim!"
        elif percent >= 50:
            msg = "👍 Bom esforço! Mais um pouco de estudo e chegas lá."
        else:
            msg = "💪 Não desistas! Vamos rever a matéria?"
            
        st.markdown(f"<div style='text-align: center; padding: 1rem; font-size: 1.2rem;'>{msg}</div>", unsafe_allow_html=True)
        
        if st.button("🔄 Criar Novo Quiz (Mesma Matéria)", type="primary", use_container_width=True):
             # Just restart logic, no need to clear persistent storage
             st.session_state.game_state = 'intro' 
             st.session_state.quiz_data = []
             st.session_state.current_q_index = 0
             st.session_state.score = 0
             st.rerun()
             
        if st.button("📂 Escolher Nova Matéria", use_container_width=True):
            clear_storage_and_reset()
