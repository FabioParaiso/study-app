# Logica do Backend - Super Study

Este documento explica o que o backend faz e como tudo se liga, numa linguagem simples.

## 1) Visao geral
- O backend e o "cerebro" da app: recebe pedidos, guarda dados e devolve respostas.
- Ele transforma ficheiros em texto, pede ajuda a IA para criar quizzes e guarda resultados.
- Tudo o que o aluno faz passa por aqui: login, upload de material, quizzes, analitica e gamificacao.

## 2) Dados que ficam guardados
Em termos simples, a base de dados guarda:
- Aluno: nome, password cifrada, XP total, avatar atual, melhor pontuacao.
- Material de estudo: texto, origem do ficheiro, topicos e conceitos, estatisticas, e qual esta ativo.
- Topicos e conceitos: organizam a materia em partes mais pequenas.
- Resultado de quiz: pontuacao, numero de perguntas, tipo de quiz, data.
- Analitica por pergunta: se foi correta e a que conceito pertence.

## 3) Como o servidor arranca
- Quando o servidor liga, ele cria as tabelas da base de dados se nao existirem.
- Ativa regras de seguranca basica nos pedidos e permite acesso do frontend (CORS).
- Regista os principais caminhos da API: autenticacao, materiais, quizzes, analitica, gamificacao.

## 4) Login e seguranca
- Registo: valida a password, cria a password cifrada e guarda o aluno.
- Login: compara a password com a versao cifrada guardada.
- Se o login/registo for valido, o backend devolve um token (uma chave temporaria).
- Quase todos os pedidos importantes exigem esse token.
- Existe um limite de tentativas por minuto para evitar abuso.

## 5) Upload e gestao de materiais
Quando o aluno envia um ficheiro:
- O backend valida o tamanho (maximo 10MB).
- Deteta o tipo (PDF ou texto) e extrai o conteudo.
- Pede a IA para identificar topicos e conceitos.
- Guarda o material e marca-o como "ativo".

Outras operacoes:
- Listar materiais antigos.
- Ativar um material antigo (so 1 fica ativo de cada vez).
- Limpar o material ativo (fica sem ativo).
- Apagar material: apaga resultados de quizzes ligados e ajusta XP se necessario.

## 6) IA para topicos e conceitos
- O backend envia o texto para a IA.
- A IA devolve 3 a 6 topicos e 3 a 6 conceitos por topico.
- O backend limpa repeticoes e padroniza nomes (ex: "Outros" vira "Conceitos Gerais").

## 7) Geracao de quizzes
Para gerar um quiz:
- O backend precisa de um material ativo e de uma chave de IA.
- Escolhe os topicos: os pedidos pelo aluno ou os recomendados pela analitica.
- Verifica se o aluno ja tem XP suficiente para desbloquear o nivel.
  - Iniciante: escolha multipla (0 XP).
  - Intermedio: resposta curta (300 XP).
  - Avancado: resposta aberta (900 XP).
- Limita o vocabulario ao que existe no material (lista de conceitos).
- Envia as instrucoes para a IA criar as perguntas.
- No caso de escolhas multiplas, baralha as opcoes para evitar vicios.

## 8) Avaliacao de respostas
- Resposta curta e aberta: a IA avalia e devolve nota e feedback.
- Escolha multipla: a validacao pode ser direta (nao precisa de IA).

## 9) Guardar resultados e estatisticas
Depois de um quiz:
- O frontend envia a pontuacao e o detalhe de cada pergunta.
- O backend guarda o resultado geral do quiz.
- Para cada pergunta, guarda se o aluno acertou.
- Tenta ligar cada pergunta a um conceito do material.
- Atualiza estatisticas do material (total de perguntas, certas, XP do material, melhor pontuacao).

## 10) Analitica (pontos fracos)
- O backend junta todos os dados de perguntas e conceitos.
- Calcula a taxa de sucesso por conceito.
- Devolve uma lista com o que o aluno domina e o que precisa reforcar.
- Estes dados ajudam a criar quizzes mais adaptados.

## 11) Gamificacao
- Endpoints para somar XP total do aluno.
- Permite mudar o avatar do aluno.
- Atualiza a melhor pontuacao do aluno.
- Tudo e associado ao aluno autenticado.

## 12) Quando algo corre mal
- Se nao existir material ativo, o backend recusa gerar quiz.
- Se nao houver chave de IA, as funcoes de IA nao funcionam.
- Se um pedido tiver dados invalidos, o backend devolve erro explicativo.

## 13) Resumo simples
- O backend guarda dados, organiza materia, chama a IA e mede progresso.
- A cada quiz, aprende com os erros e ajusta o proximo.
- O resultado final e uma experiencia de estudo personalizada e gamificada.
