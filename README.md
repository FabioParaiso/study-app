# 📚 Estudo Divertido - App para o 6º Ano

Bem-vindo à app **Estudo Divertido**! Esta aplicação transforma apontamentos escolares (PDF ou ficheiros de texto) em questionários de escolha múltipla interativos, utilizando inteligência artificial.

**Nota:** Esta é a nova versão da aplicação, dividida em Backend (API) e Frontend (Interface Web). A versão antiga (Streamlit) encontra-se na pasta `legacy/`.

## ✨ Funcionalidades

*   **Upload de Apontamentos:** Suporta ficheiros PDF e TXT.
*   **Geração de Perguntas:** Cria perguntas de escolha múltipla adaptadas ao 6º ano.
*   **Modo de Jogo:** Responde às perguntas e ganha pontos!
*   **Identificação de Tópicos:** A IA identifica automaticamente os tópicos principais dos teus apontamentos.
*   **Persistência:** Podes fechar a página e voltar mais tarde (os dados são guardados localmente).

## 🛠️ Arquitetura

O projeto está dividido em duas partes:

*   **Backend (`/backend`):** Servidor Python com FastAPI. Trata do processamento de ficheiros e comunicação com a OpenAI.
*   **Frontend (`/frontend`):** Interface Web construída com React e Vite.

## 📋 Pré-requisitos

*   **Python** (versão 3.8 ou superior)
*   **Node.js** (para correr o frontend)
*   **OpenAI API Key** (necessária para gerar as perguntas)

## 🚀 Instalação e Execução

Para a aplicação funcionar, precisas de correr o **Backend** e o **Frontend** em terminais separados.

### 1. Configurar o Backend

1.  Abre um terminal e entra na pasta `backend`:
    ```bash
    cd backend
    ```

2.  (Recomendado) Cria e ativa um ambiente virtual:
    ```bash
    python -m venv venv
    # Windows:
    .\venv\Scripts\activate
    # Mac/Linux:
    source venv/bin/activate
    ```

3.  Instala as dependências:
    ```bash
    pip install -r requirements.txt
    ```

4.  Configura a chave da OpenAI:
    *   Cria um ficheiro `.env` na pasta `backend/`.
    *   Adiciona a tua chave:
        ```text
        OPENAI_API_KEY=sk-proj-xxxxxxxx...
        ```

5.  Inicia o servidor:
    ```bash
    uvicorn main:app --reload
    ```
    O servidor ficará a correr em `http://localhost:8000`.

### 2. Configurar o Frontend

1.  Abre um **novo terminal** e entra na pasta `frontend`:
    ```bash
    cd frontend
    ```

2.  Instala as dependências (apenas na primeira vez):
    ```bash
    npm install
    ```

3.  Inicia a aplicação:
    ```bash
    npm run dev
    ```
    O frontend ficará acessível (geralmente em `http://localhost:5173`).

## 🎮 Como Usar

1.  Abre o link do Frontend no teu navegador (ex: `http://localhost:5173`).
2.  Se não configuraste o `.env` no backend, podes inserir a tua API Key diretamente na interface.
3.  Carrega um ficheiro PDF ou TXT.
4.  Clica em "Carregar e Analisar".
5.  Escolhe um tópico (ou todos) e clica em "Gerar Quiz".
6.  Diverte-te a estudar!

---
Desenvolvido com ❤️ para ajudar no estudo!
