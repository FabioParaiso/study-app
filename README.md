# 📚 Estudo Divertido - App para o 6º Ano

Bem-vindo à app **Estudo Divertido**! Esta aplicação foi criada para ajudar os alunos do 6º ano a estudar de uma forma mais interativa e divertida. Transformamos os teus apontamentos (PDF ou ficheiros de texto) em questionários de escolha múltipla utilizando inteligência artificial! 🚀

## ✨ O que é?

É uma ferramenta que lê os teus resumos da escola e cria perguntas para testares os teus conhecimentos. Perfeito para estudar para os testes!

## 🛠️ Pré-requisitos

Para correres esta aplicação no teu computador, precisas de ter instalado:

*   [Python](https://www.python.org/downloads/) (versão 3.8 ou superior)

## 📥 Instalação

1.  **Descarrega o código** (se ainda não o fizeste).
2.  **Instala as bibliotecas necessárias**:
    Abre o terminal (linha de comandos) na pasta do projeto e escreve:

    ```bash
    pip install -r requirements.txt
    ```

## 🔑 Configuração (OpenAI API)

Esta app usa a inteligência da OpenAI (GPT-4o-mini) para ler os teus apontamentos. Precisas de uma chave especial (API Key).

1.  Vai a [OpenAI Platform](https://platform.openai.com/api-keys) e cria uma API Key.
2.  Tens duas opções para configurar a chave:
    *   **Opção A (Mais fácil):** Cola a chave diretamente na aplicação quando a correres (há um campo para isso na barra lateral).
    *   **Opção B (Avançado):** Cria um ficheiro chamado `.env` na pasta do projeto e adiciona a seguinte linha:
        ```text
        OPENAI_API_KEY=a_tua_chave_aqui
        ```

## 🚀 Como Correr a Aplicação

No terminal, dentro da pasta do projeto, escreve:

```bash
streamlit run app.py
```

Isto vai abrir o teu navegador de internet com a aplicação a funcionar. Agora é só carregares os teus apontamentos e começares a estudar!

## 🧪 Como Correr os Testes

Se quiseres verificar se está tudo a funcionar corretamente no código, podes correr os testes automáticos:

```bash
pytest
```

---
Diverte-te a estudar! 🤓📖
