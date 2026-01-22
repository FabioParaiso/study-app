# 🦉 Super Study! - Aprender é uma Aventura

Bem-vindo ao **Super Study**, a plataforma de estudo inteligente que transforma apontamentos escolares numa aventura gamificada! 🚀

Este projeto foi desenhado especificamente para alunos do **6º ano (10-12 anos)**, combinando Inteligência Artificial com metodologias pedagógicas comprovadas (Taxonomia de Bloom + Repetição Espaçada) para tornar o estudo viciante e eficaz.

---

## ✨ Funcionalidades Mágicas

### 🧠 Estudo Inteligente & Adaptativo
A nossa IA não cria apenas perguntas aleatórias. Ela analisa os teus apontamentos (PDF/Texto) e cria um plano de estudo personalizado:
*   **Deteção de Tópicos:** A IA organiza a matéria em tópicos claros (ex: "Fotossíntese", "Revolução Liberal").
*   **Analítica de Pontos Fracos:** O sistema sabe onde erras! Se falhares perguntas sobre "Ruminantes", o próximo quiz terá mais perguntas sobre isso.
*   **Estudo Focado:** Podes escolher estudar "Tudo" ou apenas um tópico específico para o teste de amanhã.

### 🎮 Gamificação (Aprender a Brincar)
Estudar não tem de ser chato. No Super Study, cada resposta certa conta!
*   **XP (Pontos de Experiência):** Ganha XP por cada resposta certa. Acumula pontos para subir de nível!
*   **Títulos Evolutivos:** Começas como "Estudante Curiosa" 🌱 e evoluis até "Cientista Lendária" 🚀 à medida que ganhas XP.
*   **Mascote:** O nosso **Super Mocho** acompanha-te em toda a jornada!

### 📈 Sistema de Progressão (Níveis de Dificuldade)
Para garantir uma aprendizagem sólida, o acesso aos modos de quiz é desbloqueado progressivamente, baseando-se na **Taxonomia de Bloom**:

| Nível | Modo de Quiz | Foco Pedagógico | Requisito |
| :--- | :--- | :--- | :--- |
| **Iniciante** 🟢 | Escolha Múltipla | **Compreensão & Conhecimento.** Aprender os conceitos básicos sem pressão. Erros comuns explicados. | Desbloqueado |
| **Intermédio** 🟡 | Resposta Curta | **Aplicação & Construção de Frase.** O aluno tem de escrever uma frase simples (Sujeito + Verbo) factual. | 300 XP |
| **Avançado** 🟣 | Resposta Aberta | **Análise & Avaliação.** Perguntas profundas ("Porquê?", "Explica...", "Na tua opinião..."). | 900 XP |

---

## 🛠️ Arquitetura Técnica

O projeto segue uma arquitetura moderna e separada (Frontend + Backend), comunicando via REST API.

### 🎨 Frontend (`/frontend`)
*   **Framework:** React (Vite)
*   **Estilo:** Tailwind CSS (Design System personalizado "Duolingo-style": vibrante, arredondado, animado).
*   **UX:** Feedback em tempo real, validações visuais, animações `framer-motion` suave.

### 🧠 Backend (`/backend`)
*   **API:** FastAPI (Python).
*   **Database:** SQLite (SQLAlchemy) para gestão de alunos, progresso e analítica.
*   **AI Engine:** OpenAI GPT-4o-mini (Optimizado com estratégias de prompt engineering complexas).
*   **Segurança:** Autenticação com Hashing de Passwords (`bcrypt`) e Rate Limiting (`slowapi`) para proteção contra brute-force.

---

## 🚀 Como Começar (Instalação)

### Pré-requisitos
*   **Node.js** (v16+)
*   **Python** (v3.9+)
*   **OpenAI API Key**

### 1. Configurar o Backend
```bash
cd backend

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Mac/Linux
# .\venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Configurar Variáveis de Ambiente
# Cria um ficheiro .env na pasta backend/ com:
# OPENAI_API_KEY=sk-....
```

Para iniciar o servidor:
```bash
python -m uvicorn main:app --reload --port 8000
```

### 2. Configurar o Frontend
Num novo terminal:
```bash
cd frontend

# Instalar pacotes
npm install

# Iniciar aplicação
npm run dev
```

Acede a `http://localhost:5173` e começa a estudar!

---

## 📚 Estrutura do Projeto

```
/
├── backend/
│   ├── routers/         # Endpoints da API (Auth, Study, Gamification)
│   ├── services/        # Lógica de Negócio (AI, Analytics, Quiz Strategies)
│   ├── models.py        # Modelos de Base de Dados (SQLAlchemy)
│   └── main.py          # Entry point
│
└── frontend/
    ├── src/
    │   ├── components/  # Componentes UI Reutilizáveis
    │   ├── pages/       # Páginas Principais (Login, Intro, Quiz)
    │   ├── services/    # Comunicação com API (Axios)
    │   ├── hooks/       # Lógica de Estado (Custom Hooks)
    │   └── assets/      # Imagens e Sons
    └── public/          # Assets estáticos
```

---
Desenvolvido por **Fábio Oliveira** & **Google DeepMind Antigravity** 🤖✨
