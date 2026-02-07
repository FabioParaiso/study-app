# Relatório Final v3: Desafio das Cientistas (Cooperativo First)

**Data:** 7 de fevereiro de 2026
**Versão:** 3.9 (v3.8 + hardening do rollout do quiz_session_token)
**Estado:** Final para implementação
**Escopo inicial:** 2 utilizadoras (filha + BFF)
**Direção de produto:** simplicidade máxima para criança + proteção social

---

## 1. Decisão Final

A fase inicial deve ser **cooperativa**, não competitiva.

Decisões fechadas:

- manter apenas **um tipo de XP** no produto: `XP do Desafio`
- usar `XP do Desafio` para a missão semanal colaborativa
- manter títulos temáticos (`Estudante Curiosa`, etc.) baseados no mesmo `XP do Desafio`
- remover da UX principal qualquer noção de múltiplos XPs (pessoal vs duelo)
- evitar ranking direto 1v1 na fase inicial
- `XP do Desafio` é **por aluna** (não por material) — o modelo diário de +20/+5 é material-agnostic

## 2. Princípios de Design

1. A criança deve perceber o sistema em menos de 30 segundos.
2. O sistema deve reforçar "estudar juntas", não "ganhar da amiga".
3. Não pode premiar grind de volume no mesmo dia.
4. O XP precisa de estar ligado a qualidade mínima de aprendizagem.
5. A experiência deve preservar progresso de longo prazo.

## 3. Modelo de UX (Simples)

No ecrã principal da criança aparecem apenas:

- `XP do Desafio` da semana (equipa)
- progresso da missão semanal (barra)
- estado da missão (`Em progresso`, `Concluída`)
- título atual da criança (ex.: `Exploradora da Natureza`)

Não mostrar na UX principal:

- ranking
- múltiplos contadores de XP
- métricas analíticas avançadas

As métricas de aprendizagem detalhadas ficam numa área secundária (pais/admin).

## 4. Mecânica da Missão Semanal (Cooperativa)

### 4.1 Sessão válida

Uma sessão conta para XP se:

- `active_seconds >= 180`
- `total_questions >= 5`
- sessão concluída e persistida

### 4.2 Geração de XP do Desafio

Por utilizadora, por dia:

- primeira sessão válida do dia: `+20 XP`
- bónus de qualidade do dia: `+5 XP` se `best_score_pct >= 80`
- sessões extra no mesmo dia: `+0 XP` para evitar grind
- sessões extra podem atualizar `best_score_pct`

### 4.3 Normalização de `best_score_pct`

O score é normalizado para percentagem (0-100) independentemente do tipo de quiz:

- multiple-choice: `(score / total_questions) * 100`
- short_answer: score já é 0-100 (avaliação AI)
- open-ended: score já é 0-100 (avaliação AI)

`best_score_pct = max(score_percentage)` de todas as sessões válidas desse dia.

**Nota de implementação:** Para MCQ, o denominador deve ser `QuizResult.total_questions` (o valor recebido do frontend). Em `repository.py`, a variável `effective_total = len(analytics_data)` pode divergir de `total_questions` se houver perguntas sem resposta. O `calculator.py` deve normalizar usando `QuizResult.score / QuizResult.total_questions * 100`, validando que `total_questions > 0`.

### 4.4 Meta semanal da equipa (MVP)

Modelo de meta em 2 níveis:

- `Missão Base`: ambas com `>=3 dias ativos` (XP equipa >=120 é consequência automática dos 3 dias × 20 XP × 2 alunas; threshold de XP mantido como guardrail técnico)
- `Missão Qualidade`: ambas com `>=3 dias ativos` E `XP equipa >= 150` E `quality_days_team >= 4` (pelo menos 4 dias com `best_score_pct >= 80` entre as duas)

Recompensas:

- Cooperativa (Missão Base): badge semanal + confetti de conclusão + selo no histórico
- Cooperativa (Missão Qualidade): badge especial + confetti premium + moldura visual temporária

Bónus cooperativo avançado (ativação: Sprint 4):

- se ambas tiverem `>=5 dias ativos` e `XP da equipa >= 180`, desbloqueia recompensa visual permanente (ex.: avatar)
- nota: esta regra é definida aqui para completude do modelo de produto, mas só é implementada no Sprint 4 para permitir calibrar primeiro as mecânicas base

### 4.5 Anti-free-rider

**Análise matemática:** Com `>=3 dias ativos` obrigatórios e `+20 XP/dia`, cada aluna acumula no mínimo 60 XP. O threshold original de 30 XP nunca filtra nada. Da mesma forma, 2 × 60 = 120, logo a Missão Base (>=120 team XP) é automaticamente atingida se ambas cumprirem os 3 dias.

**Decisão:** A Missão Base é simplificada para `ambas com >=3 dias ativos` como condição principal. O threshold de XP da equipa (120/150) serve como guardrail contra edge cases futuros (ex.: se o modelo de XP mudar). O anti-free-rider explícito é removido — os 3 dias obrigatórios já cumprem essa função.

Regra simplificada:

- Missão Base: ambas com `>=3 dias ativos` (o >=120 XP team é consequência automática)
- Missão Qualidade: ambas com `>=3 dias ativos` E `XP equipa >= 150` E `quality_days_team >= 4` (pelo menos 4 dias com bónus de qualidade entre as duas)
- anti-free-rider: implícito nos `>=3 dias ativos` por aluna

**Cálculo de `quality_days_team`:** Soma dos dias com qualidade de ambas as alunas. Se A tem 2 dias com `best_score_pct >= 80` e B tem 2 dias, `quality_days_team = 4`. Ambas podem ter qualidade no mesmo dia — cada uma conta separadamente. Máximo teórico: 14 por semana (7 dias × 2 alunas).

```sql
SELECT COUNT(*) as quality_days_team
FROM challenge_day_activity cda
JOIN challenge_week cw ON cda.challenge_week_id = cw.id
WHERE cw.week_id = :week_id
AND cw.student_id IN (:student_id, :partner_id)
AND cda.best_score_pct >= 80
```

**Justificação da condição de qualidade:** Sem o requisito de `quality_days_team >= 4`, a Missão Qualidade pode ser atingida apenas com mais dias ativos (ex.: 4+4 × 20 = 160 XP) sem nenhum bónus de qualidade. Com a condição, são necessários pelo menos 4 dias (combinados) com `best_score_pct >= 80`, o que garante que o nome "Qualidade" corresponde à realidade. O valor 4 é calibrável (secção 7.7).

**Cenários mínimos viáveis:**
- 3+3 dias, todos 6 com qualidade: 6 × 20 + 6 × 5 = 150 XP, quality_days=6 — atinge, mas exige 100% de qualidade
- 4+3 dias, 4 com qualidade: 7 × 20 + 4 × 5 = 160 XP, quality_days=4 — atinge com margem
- 3+3 dias, 4 com qualidade: 6 × 20 + 4 × 5 = 140 XP — **não atinge** (precisa de mais dias ou mais qualidade)

A Missão Qualidade é intencionalmente mais exigente do que aparenta — requer ou mais dias ou alta consistência de qualidade.

### 4.6 Resiliência quando a parceira falha

Para evitar frustração por ausência da parceira:

- existe `Modo Pausa` (férias/doença), ativável via script CLI (controlo parental)
- no modo pausa, a semana muda para `Missão de Continuidade` (solo)
- `Missão de Continuidade`: `XP individual >= 75` e `>=3 dias ativos`
- esta semana não atribui recompensa cooperativa, mas ativa recompensa de `Continuidade` (badge menor)
- semana de `Continuidade` conta para hábito e títulos
- se `partner_id IS NULL` (sem parceira configurada), aplica automaticamente o mesmo modo `Continuidade` (sem recompensa cooperativa)

**Persistência do Modo Pausa:**

A pausa vive na tabela `challenge_pause` (criada no Sprint 3):

```sql
CREATE TABLE challenge_pause (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL REFERENCES students(id),
    start_week_id VARCHAR(10) NOT NULL,    -- "2026W08" — primeira semana em pausa
    end_week_id VARCHAR(10) NOT NULL,      -- fim obrigatório (evita pausa indefinida)
    reason VARCHAR(50) NOT NULL,           -- 'ferias', 'doenca', 'outro'
    is_exception BOOLEAN DEFAULT FALSE,     -- true apenas para extensão manual excecional
    activated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deactivated_at TIMESTAMP,              -- NULL enquanto ativa
    UNIQUE(student_id, start_week_id)
);
```

Regras:

- pausa ativa é definida como `deactivated_at IS NULL AND current_week <= end_week_id`
- uma aluna pode ter no máximo 1 pausa ativa, garantido por check no `ChallengeService.activate_pause()` + índice parcial único em PostgreSQL (secção 10.2)
- pausa aplica-se a partir da semana indicada em `start_week_id` (não retroactiva)
- `ChallengeService` consulta se a parceira está em pausa para decidir modo cooperativo vs continuidade
- duração standard da pausa: 1-2 semanas (`end_week_id` obrigatório e <= `start_week_id + 1`)
- extensão excecional: até 4 semanas apenas com `reason='doenca'` e `is_exception=true`
- cooldown de 1 semana após fim de pausa antes de nova ativação (exceto extensão médica)
- auto-close: se `current_week > end_week_id` e `deactivated_at IS NULL`, o serviço fecha automaticamente a pausa (`deactivated_at=now`) e volta ao modo cooperativo
- desativação antecipada define `deactivated_at` como timestamp atual
- se ambas estiverem em pausa na mesma semana, nenhuma missão cooperativa é criada. A semana é neutra para métricas/recompensas cooperativas, mas `XP do Desafio` individual e títulos continuam a acumular se a criança estudar. O endpoint retorna `"status": "all_paused"` com mensagem amigável (secção 12)

### 4.7 Recompensa de contribuição individual (quando a equipa falha)

Para evitar punir quem estudou bem numa semana sem conclusão de missão:

- se a missão cooperativa falhar e a criança cumprir `XP individual >= 60` e `>=3 dias ativos`
- recebe recompensa de `Contribuição` (selo individual de esforço)
- esta recompensa tem valor menor que `Cooperativa` e não desbloqueia item permanente
- objetivo: justiça e retenção sem substituir o foco da equipa

### 4.8 Semana zero

Se o lançamento ocorrer fora de segunda-feira:

- semana atual vira `Semana de Treino`
- conta para hábitos e onboarding
- não conta para histórico oficial de conclusão de missão
- primeira semana oficial começa na segunda seguinte

## 5. Títulos Mantidos com XP do Desafio

Os títulos continuam e passam a ser alimentados pelo mesmo `XP do Desafio` (acumulado histórico por criança).

Regra de simplicidade:

- é o mesmo tipo de XP
- muda apenas a janela de leitura: semanal para missão e acumulada para título

Thresholds oficiais de títulos (congelados, source: `useGamification.js` linhas 4-11):

| XP Mínimo | Título | Ícone |
|-----------|--------|-------|
| 0 | Estudante Curiosa | Sprout |
| 100 | Exploradora da Natureza | Compass |
| 300 | Assistente de Laboratório | Microscope |
| 600 | Bióloga Júnior | Dna |
| 1000 | Mestre das Ciências | FlaskConical |
| 2000 | Cientista Lendária | Rocket |

UX:

- mostrar título atual + progresso para próximo título
- não mostrar múltiplos rótulos de XP na mesma vista

## 6. Guardrails Contra Competição Perversa

1. Sem leaderboard pública global.
2. Grupos fechados apenas (dupla, turma, amigos).
3. Recompensa principal é de equipa.
4. Cap diário implícito por regra de "1 sessão com XP por dia".
5. Objetivo exige contribuição mínima das duas.
6. `Modo Pausa` é temporário, com duração máxima e cooldown (não pode virar modo solo permanente).

## 7. Métricas de Produto (Avaliar se está a resultar)

### 7.1 Métricas principais de sucesso

- `Mission Base Completion Rate`: % de semanas em que a dupla conclui a `Missão Base`
- `Mission Quality Completion Rate`: % de semanas em que a dupla conclui a `Missão Qualidade`
- `Continuity Reward Rate`: % de semanas em que a recompensa de `Continuidade` é atribuída
- `Contribution Reward Rate`: % de semanas em que a recompensa de `Contribuição` é atribuída
- `Dual Active Rate`: % de semanas com ambas ativas >=3 dias
- `Weekly Retention`: % de utilizadoras que regressam na semana seguinte

Nota de denominador: semanas com `status="all_paused"` são neutras e ficam fora do denominador das métricas **cooperativas** semanais (`Mission Base Completion Rate`, `Mission Quality Completion Rate`, `Dual Active Rate`, `Contribution Reward Rate`, `Partner Block Rate`, etc.). Métricas individuais de hábito/aprendizagem continuam a contar com base na atividade real da criança.

### 7.2 Métricas de hábito

- média de dias ativos por utilizadora/semana
- % de utilizadoras com >=3 dias ativos
- tempo médio ativo por sessão válida

### 7.3 Métricas de qualidade de aprendizagem (guardrail)

- `Quality Day Rate`: % de dias com `best_score_pct >= 80`
- evolução de conceitos para estado `building/established` (estados do codebase: `not_seen` → `exploring` → `building` → `established`, ver `calculator.py`)
- variação de precisão média semanal

### 7.4 Métricas de risco social

- `Contribution Imbalance`: % de semanas em que uma utilizadora faz >70% do XP da equipa
- abandono após semanas falhadas consecutivas
- taxa de conclusão da missão após "quase conseguida" (ex.: atingiu 80-99% da meta)
- `Partner Block Rate`: % de semanas falhadas por ausência total de uma parceira
- taxa de ativação de `Modo Pausa` (férias/doença)
- `Pause Weeks Rate`: % de semanas em pausa sobre total de semanas ativas
- `Pause Reactivation Rate`: % de reativações de pausa dentro de 2 semanas após término

### 7.5 Métricas de simplicidade da experiência

- taxa de conclusão do onboarding
- nº médio de aberturas de "rever regras" por semana
- tempo até primeira sessão válida após login

### 7.6 Métricas de fairness por material (nova)

- `Quality Bonus Rate por material`: % de dias com bónus de qualidade, agrupado por material
- se materiais fáceis tiverem `Quality Bonus Rate` sistematicamente superior (>20pp acima da média), considerar ajuste de threshold por dificuldade estimada do material
- decisão: monitorizar nas primeiras 6 semanas, não bloquear lançamento

### 7.7 Quadro de decisão (métricas -> ação)

**Nota para N=1 dupla:** As taxas abaixo assumem N >= 5 duplas. Com 1 dupla, usar contagens absolutas em janelas de 3+ semanas. Ex.: "missão base falhada 3 semanas consecutivas" em vez de "rate < 40%". Converter para taxas quando o sistema escalar para turmas. Semanas `all_paused` ficam fora do denominador das taxas cooperativas.

Se `Mission Base Completion Rate < 40%` por 3 semanas (ou 3 falhas consecutivas com N=1):

- reduzir dias mínimos da `Missão Base` (ex.: 3 -> 2 dias) ou reduzir metas da `Missão Qualidade` (ex.: quality_days 4 -> 3, XP 150 -> 140)

Se `Contribution Imbalance > 50%` das semanas:

- aumentar dias mínimos obrigatórios (ex.: 3 -> 4 dias) ou adicionar condição de qualidade mínima individual

Se `Quality Day Rate < 45%` por 4 semanas:

- subir peso de qualidade no feedback (não necessariamente no XP)
- rever dificuldade/perguntas

Se `Weekly Retention < 60%`:

- simplificar onboarding e reforçar celebração de progresso

Se `Mission Base Completion Rate > 75%` por 4 semanas, `Mission Quality Completion Rate > 55%` e retenção estável:

- considerar metas por grupo maior (turma) e desafios opcionais

Se `Partner Block Rate > 20%` por 4 semanas:

- relaxar regras de `Modo Pausa` e melhorar comunicação desta funcionalidade

Se `Pause Weeks Rate > 35%` por 6 semanas ou `Pause Reactivation Rate > 25%`:

- apertar regras de pausa (reduzir duração máxima ou aumentar cooldown) e rever dependência de parceria

Se `Contribution Reward Rate > 45%` por 4 semanas:

- revisar metas cooperativas (dias mínimos, quality_days, XP) ou critérios de fallback para evitar normalizar falha de equipa

Se `Quality Bonus Rate` de um material > `Quality Bonus Rate` média + 20pp por 4 semanas:

- sinalizar material como potencialmente demasiado fácil (informativo, sem ação automática)

## 8. Evolução Futura (turma/grupo de amigos)

Fase futura recomendada:

- manter modelo cooperativo por grupo
- objetivos semanais por equipa (não por indivíduo)
- ranking opcional apenas entre equipas equivalentes e em contexto fechado
- sempre com guardrails de contribuição mínima por membro

---

## 9. Decisões Técnicas Pré-Implementação

Esta secção documenta decisões de engenharia que o plano de produto não cobria e que foram identificadas durante a auditoria técnica ao codebase.

### 9.1 XP por Aluna vs por Material

**Decisão:** `XP do Desafio` é por aluna (campo `challenge_xp` na tabela `students`).

**Justificação:**

- o modelo de Challenge XP (+20 sessão válida, +5 qualidade) é material-agnostic — recompensa consistência, não volume
- o cap diário (max 25 XP/dia) neutraliza a vantagem de materiais fáceis no eixo de frequência
- o único ponto de risco é o bónus de qualidade (+5 se `best_score >= 80%`), que pode ser mais fácil com materiais simples — mas representa max 25% do XP diário
- monitorizar com `Quality Bonus Rate por material` (secção 7.6) e rever após 6 semanas

**Impacto no código existente:**

- `StudyMaterial.total_xp` deixa de participar em regras de unlock quando `COOP_CHALLENGE_ENABLED=true`; unlock passa a depender apenas da lógica pedagógica já existente (readiness/conceitos)
- `Student.total_xp` existente não é reutilizado para UX nem progressão principal; campo novo `Student.challenge_xp` é a source of truth
- `StudyMaterial.total_xp` e `Student.total_xp` podem manter atualização técnica temporária por compatibilidade, mas sem impacto na experiência da criança
- frontend passa de `stats.total_xp` (per-material, via `savedMaterial`) para `student.challenge_xp` (per-student, via endpoint `/me` ou `/challenge/weekly-status`) quando feature flag está ativa
- critério de migração: com `COOP_CHALLENGE_ENABLED=true`, a UX e os desbloqueios não dependem de XP legacy

### 9.2 Estratégia de Migração de XP

**Problema:** Alunas existentes perdem títulos se `challenge_xp` começar em 0.

**Solução:** Script de backfill que recalcula `challenge_xp` a partir do histórico de `QuizResult`:

```
Para cada aluna:
  tz_offset = student.expected_tz_offset (definido no seed, ex.: 0 para Portugal WET)
  Converter cada quiz_result.created_at (UTC) para local_date usando tz_offset
  Agrupar quiz_results por local_date
  Para cada dia com sessão válida (active_seconds >= 180 AND total_questions >= 5):
    challenge_xp += 20
    Se max(score_percentage) do dia >= 80:
      challenge_xp += 5
  student.challenge_xp = challenge_xp
```

**Timezone histórico:** Como não existia `tz_offset` guardado por sessão, o backfill usa o `expected_tz_offset` da aluna (configurado no seed). Para utilizadoras em Portugal (WET/WEST), usar offset 0 (UTC) para sessões de inverno e 60 para sessões de verão (verificar `created_at` contra datas de mudança de hora). Para MVP com 2 alunas no mesmo fuso, simplificar com offset fixo de 0 — o erro máximo é 1h, que só afecta sessões feitas entre 23:00-00:00 UTC (~0.5% dos casos estimados).

Executar como último passo do Sprint 1A (backend), antes de avançar para Sprint 1B. Verificar manualmente que os títulos resultantes correspondem ao esperado.

### 9.3 Hook de Sessão Completa

**Problema:** O fluxo atual `POST /quiz/result → SaveQuizResultUseCase → recorder.record()` termina sem notificar outros módulos.

**Decisão:** Hook síncrono no `SaveQuizResultUseCase.execute()`, após `recorder.record()`, com política **best-effort + idempotente**.

**Pré-requisito de código:** Hoje `recorder.record()` retorna `None` e `record_quiz_result()` retorna `bool`. Para o hook funcionar, é necessário:

1. `record_quiz_result()` passa a retornar `int` (o `quiz_result_id`) em vez de `bool` — o `result.id` já existe após `db.flush()` em `repository.py:38`
2. `recorder.record()` passa a retornar `int` (propaga o id do repositório)
3. `QuizResultRecorderPort` e `QuizResultPersistencePort` em `ports.py` atualizam assinatura de retorno
4. O check `if not success` em `recorder.py:44` muda para `if not quiz_result_id`

```python
# Em SaveQuizResultUseCase.execute()
quiz_result_id = self.recorder.record(  # antes: retornava None
    user_id=user_id,
    score=result.score,
    ...
)
if feature_flags.is_challenge_enabled():
    try:
        challenge_service.process_session(
            quiz_result_id=quiz_result_id,
            student_id=user_id,
            score=result.score,
            total_questions=result.total_questions,
            active_seconds=result.active_seconds,
            material_id=material_id
        )
    except Exception:
        log.exception("Challenge processing failed — quiz result preserved")
        # Não propagar: /quiz/result responde 200 mesmo se challenge falhar
```

**Política transacional:**

1. **Best-effort:** Falha no challenge **não** falha o `/quiz/result`. O quiz result é a operação primária; o challenge XP é secundário. Evita que um bug no challenge module quebre o fluxo de estudo.
2. **Idempotência por `quiz_result_id`:** `process_session()` verifica se já processou este `quiz_result_id` antes de atribuir XP. Garante que retries ou reprocessamentos (incluindo fora de ordem) não duplicam XP nem contagens secundárias. Implementado via tabela dedicada com UNIQUE constraint:

```python
def process_session(self, quiz_result_id: int, ...):
    # Tudo numa transação: check + consume_jti + XP + mark
    with self.repo.transaction():
        # 1. Check: já processado por quiz_result_id?
        if self.repo.is_processed(quiz_result_id):
            return  # skip — já processado

        # 2. Anti-replay: consumir jti do quiz_session_token (uso único)
        consumed = self.repo.consume_quiz_session_jti(jti, student_id)
        if not consumed:
            return  # token replay -> não atribui Challenge XP

        # 3. Process: aplicar lógica de XP
        self._apply_challenge_xp(quiz_result_id, ...)

        # 4. Mark: registar como processado (no fim, dentro da transação)
        self.repo.mark_processed(quiz_result_id)
        # Se qualquer passo falhar, transação faz rollback —
        # jti não fica consumido, quiz não fica marcado e pode reprocessar no retry
```

A ordem é crítica: **consume_jti + process + mark** na mesma transação. Se falhar entre estes passos, o rollback reverte tudo e o retry continua possível. Isto evita o cenário de "token consumido mas XP não atribuído".

3. **Tabela de tracking** (com UNIQUE constraint para dedupe robusto):

```sql
CREATE TABLE challenge_processed_quiz (
    quiz_result_id INTEGER PRIMARY KEY REFERENCES quiz_results(id),
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

A combinação de `is_processed` + `consume_quiz_session_jti` + `mark_processed` dentro da mesma transação garante idempotência e anti-replay sem risco de perda de XP em falhas transitórias.

**Nota sobre transações:** O quiz result é comitado em `repository.py` (`db.commit()`) antes do hook correr. O `process_session()` opera na mesma sessão SQLAlchemy (via FastAPI `Depends(get_db)`). O `self.repo.transaction()` deve usar `db.begin_nested()` (SAVEPOINT semantics) em vez de transação top-level, para não interferir com a sessão já comitada. Se o SAVEPOINT falhar, apenas as operações do challenge são revertidas.

**Trade-offs aceites:**

- +20-40ms de latência no `POST /quiz/result` (aceitável)
- acoplamento quiz→challenges via import (mitigado por feature flag guard + try/except)
- se necessário no futuro, migrar para task queue async

### 9.4 Feature Flags

**Problema:** Não existe sistema de feature flags no codebase. Apenas `TEST_MODE` e `REGISTER_ENABLED` como env vars.

**Decisão:** Manter padrão existente de env vars (simplicidade):

Backend (`feature_flags.py`):
- `COOP_CHALLENGE_ENABLED` — toggle global do desafio
- `COOP_PAUSE_MODE_ENABLED` — toggle do modo pausa (Sprint 3)

Frontend (`import.meta.env`):
- `VITE_COOP_CHALLENGE_ENABLED` — condiciona rendering do card de challenge

Para MVP com 2 utilizadoras, flags globais são suficientes. Per-student flags ficam para fase de grupos maiores.

**Estratégia de rollout (decisão fechada):**

1. Sprint 1A: deploy backend com `COOP_CHALLENGE_ENABLED=false`.
2. Sprint 1B: deploy frontend com envio de `quiz_session_token` e UI do desafio protegida por `VITE_COOP_CHALLENGE_ENABLED`.
3. Ativação: ligar `COOP_CHALLENGE_ENABLED` apenas após smoke test E2E completo backend+frontend.
4. Janela de ativação recomendada: segunda-feira 00:00 local, para evitar semanas partidas.
5. Rollback: desligar flag (sem rollback de schema).

### 9.5 Emparelhamento (Pairing)

**Problema:** Não existe conceito de equipa/grupo no codebase. Toda a informação é per-student.

**Decisão para MVP:**

- adicionar `partner_id` (FK nullable para `students.id`) na tabela `students`
- seed script manual para definir o par inicial
- se `partner_id IS NULL`, aluna entra automaticamente em `Missão de Continuidade` (modo solo sem recompensa cooperativa)

**Operações admin no MVP:** Usar scripts CLI (`python -m scripts.pair_students`, `python -m scripts.activate_pause --start_week ... --end_week ... --reason ...`) em vez de endpoints HTTP. Não existe RBAC no codebase e adicioná-lo para MVP de 2 utilizadoras é over-engineering. Scripts correm apenas com acesso ao servidor/DB, o que é suficiente como controlo de acesso. Migrar para endpoints admin com RBAC quando expandir para turmas (secção 16).

**Regra de simetria obrigatória:** Se A.partner_id = B, então B.partner_id = A. Garantida por:

1. O script CLI `python -m scripts.pair_students --a <id> --b <id>` faz ambos os updates numa transação:

```python
# scripts/pair_students.py
def pair_students(db, student_a_id: int, student_b_id: int):
    a = db.query(Student).get(student_a_id)
    b = db.query(Student).get(student_b_id)
    a.partner_id = student_b_id
    b.partner_id = student_a_id
    db.commit()
```

2. O seed script inicial usa a mesma função.
3. O `ChallengeService` valida simetria no primeiro request da semana:

```python
def _validate_pair(self, student, partner):
    if partner.partner_id != student.id:
        raise ChallengeConfigError("Pair symmetry broken")
```

4. Desfazer par também é transacional — limpa ambos os `partner_id` antes de atribuir novos.

Não criar tabela `teams` — complexidade desnecessária para 2 utilizadoras. Migrar para `teams` many-to-many quando expandir para turmas.

### 9.6 Timezone

**Problema:** `local_day` e `week_id` dependem do fuso horário da aluna.

**Decisão:** Replicar padrão existente do módulo analytics — `tz_offset_minutes` enviado pelo frontend em cada request relevante.

- frontend envia `new Date().getTimezoneOffset() * -1` (nota: `getTimezoneOffset()` retorna inverso)
- backend calcula `local_now = utc_now + timedelta(minutes=tz_offset_minutes)`
- `week_id = local_now.isocalendar()` → formato `"2026W06"`

**Validação anti-manipulação de timezone:**

```python
# Em calendar.py — validar offset antes de usar
VALID_TZ_RANGE = (-720, 840)  # UTC-12 a UTC+14 (extremos reais do planeta)

def validate_tz_offset(tz_offset_minutes: int) -> int:
    if not VALID_TZ_RANGE[0] <= tz_offset_minutes <= VALID_TZ_RANGE[1]:
        return 0  # fallback para UTC
    return tz_offset_minutes
```

Para MVP com 2 utilizadoras em Portugal (UTC+0/UTC+1), guardar `expected_tz_offset` na tabela `students` (ex.: 0 ou 60). Se o offset recebido divergir mais de 120 minutos do esperado, logar warning e usar o esperado:

```python
if abs(received_offset - student.expected_tz_offset) > 120:
    log.warning(f"Unexpected tz_offset {received_offset} for student {student_id}")
    return student.expected_tz_offset
return received_offset
```

Não guardar timezone dinâmico no `Student` — apenas o `expected_tz_offset` como guardrail.

### 9.7 Validação Server-Side de `active_seconds`

**Problema:** `active_seconds` e `duration_seconds` são ambos calculados no frontend. Com XP dependente de sessão válida, há incentivo a manipular ambos.

**Decisão:** Validação em 3 camadas:

**Camada 1 — Estimativa server-side (source of truth para challenge XP):**

O backend calcula `server_estimated_duration` a partir de dados que controla:

```python
# O backend valida token assinado emitido no /generate-quiz
# e usa o issued_at do token como origem de tempo
server_estimated_duration = result_submitted_at - quiz_session.issued_at
```

**Abordagem escolhida (robusta):** No `POST /generate-quiz`, o backend emite `quiz_session_token` assinado (HMAC/JWT) com:

- `student_id`
- `issued_at` (UTC)
- `material_id`
- `quiz_type`
- `jti` (identificador único da sessão de quiz)
- `exp` (ex.: 4h)

No `POST /quiz/result`, o frontend envia o token e o backend:

1. valida assinatura e expiração
2. valida `student_id` do token contra utilizador autenticado
3. valida anti-replay: `jti` deve ser de uso único (consume-once)
4. calcula `server_estimated_duration` com base no `issued_at` do token

O cliente pode transportar o token, mas não consegue forjar o conteúdo sem quebrar assinatura. A validação `jti` de uso único evita replay do mesmo token para múltiplos submits.

**Política de compatibilidade de rollout (Sprint 1A -> 1B):**

- enquanto `COOP_CHALLENGE_ENABLED=false` (Sprint 1A), ausência de `quiz_session_token` **não** falha `POST /quiz/result`; o resultado do quiz é persistido normalmente e apenas não há processamento de Challenge XP
- após ativação da flag (depois do Sprint 1B), `quiz_session_token` passa a ser obrigatório para elegibilidade de Challenge XP
- token ausente/inválido/expirado/reutilizado nunca quebra o fluxo principal do quiz; apenas torna a sessão inelegível para Challenge XP (com log de motivo)

**Política de replay:** Se o token for inválido/expirado/reutilizado, o quiz result pode ser persistido para não quebrar o loop principal, mas a sessão fica inelegível para Challenge XP (log de segurança + motivo no response interno/observabilidade).

**Compatibilidade com retries legítimos:** Reutilização maliciosa do mesmo token é bloqueada por `jti` já consumido. Já retries por falha técnica durante o processamento não perdem XP, porque o consumo de `jti` e o `mark_processed` só persistem se a transação completar.

**Implementação:** Camadas 1+2 são obrigatórias no **Sprint 1A** (não adiadas para Estabilidade), porque impactam diretamente a integridade do XP.

**Camada 2 — Sanity check de `active_seconds` contra estimativa server-side:**

```python
# active_seconds não pode exceder o tempo real entre geração e submissão
max_plausible = server_estimated_duration.total_seconds() * 1.1  # 10% margem
active_seconds = min(active_seconds, max_plausible)
active_seconds = max(active_seconds, 0)
```

**Camada 3 — Heurística de questões (guardrail adicional):**

```python
# Um quiz de 10 questões com <60s de active_time é suspeito
min_plausible = total_questions * 6  # ~6s mínimo por questão
if active_seconds < min_plausible and active_seconds >= 180:
    log.warning(f"Suspiciously fast session: {active_seconds}s for {total_questions}q")
    # Não bloquear, apenas logar — pode ser aluna rápida
```

No Go-Live, as 3 camadas devem estar ativas: Camadas 1+2 como validação forte, Camada 3 como guardrail adicional de anomalias.

### 9.8 Week Rollover e Concorrência

**Team XP é derivado, não armazenado.** Não existe coluna `team_xp` — é sempre `SUM(individual_xp)` das duas alunas (secção 10.3). Cada aluna só escreve no seu próprio registo `challenge_week`, eliminando race conditions de escrita concorrente.

**Filosofia de derivação vs armazenamento:**

| Campo | Tipo | Justificação |
|-------|------|--------------|
| `team_xp` | Derivado (`SUM(individual_xp)`) | Span múltiplas alunas — evita race conditions |
| `individual_xp` | Armazenado (atómico) | Per-student, update concorrente de uma só aluna — sem race condition |
| `active_days_count` | Armazenado (atómico) | Per-student, incrementado quando novo dia é criado |
| `daily_xp` | Armazenado | Detalhe per-day — é o valor fonte para `individual_xp` |

**`individual_xp` é autoritativo.** `SUM(daily_xp)` deve igualar `individual_xp` em condições normais. Se houver suspeita de drift, query de reconciliação:

```sql
SELECT cw.id, cw.individual_xp, COALESCE(SUM(cda.daily_xp), 0) as sum_daily
FROM challenge_week cw
LEFT JOIN challenge_day_activity cda ON cda.challenge_week_id = cw.id
GROUP BY cw.id
HAVING cw.individual_xp != COALESCE(SUM(cda.daily_xp), 0)
```

**Update de `individual_xp` é atómico** para evitar read-modify-write:

```python
UPDATE challenge_week SET individual_xp = individual_xp + :xp WHERE id = :id
```

**Update de `active_days_count`** no `process_session()`:

```python
# Quando first_valid_session de um novo dia é criada:
UPDATE challenge_week SET active_days_count = active_days_count + 1 WHERE id = :id
```

**Sessão no limite de semana:** Usar `QuizResult.created_at` (UTC) convertido para hora local da aluna para determinar o dia/semana da sessão, não o momento de processamento.

**Criação de `challenge_week`:** Lazy creation — quando a aluna completa a primeira sessão da semana, criar o registo se não existir.

### 9.9 Training Week

**Decisão:** Configuração global `CHALLENGE_LAUNCH_DATE` (env var, formato `YYYY-MM-DD`).

Qualquer sessão antes da segunda-feira seguinte a `CHALLENGE_LAUNCH_DATE` pertence à Semana de Treino:

- `is_training_week = True`
- conta XP para títulos
- não conta para histórico oficial de missões
- não aparece no endpoint `/challenge/weekly-status` como semana concluída/falhada

---

## 10. Modelo de Dados

### 10.1 Alterações a tabelas existentes

```sql
-- students (adicionar)
ALTER TABLE students ADD COLUMN challenge_xp INTEGER DEFAULT 0;
ALTER TABLE students ADD COLUMN partner_id INTEGER REFERENCES students(id);
ALTER TABLE students ADD COLUMN expected_tz_offset INTEGER DEFAULT 0;  -- guardrail timezone (ex.: 0 para WET, 60 para WEST)
```

### 10.2 Novas tabelas

```sql
CREATE TABLE challenge_week (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    week_id VARCHAR(10) NOT NULL,           -- "2026W06"
    student_id INTEGER NOT NULL REFERENCES students(id),
    is_training_week BOOLEAN DEFAULT FALSE,
    individual_xp INTEGER DEFAULT 0,
    active_days_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(week_id, student_id)
);

CREATE TABLE challenge_day_activity (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    challenge_week_id INTEGER NOT NULL REFERENCES challenge_week(id) ON DELETE CASCADE,
    local_date DATE NOT NULL,
    first_valid_session BOOLEAN DEFAULT FALSE,
    best_score_pct INTEGER DEFAULT 0,       -- 0-100, normalizado
    best_score_material_id INTEGER REFERENCES study_materials(id),  -- material que deu o best_score (para métrica 7.6)
    daily_xp INTEGER DEFAULT 0,             -- Max 25 (20 base + 5 qualidade)
    session_count INTEGER DEFAULT 0,
    total_active_seconds INTEGER DEFAULT 0,
    UNIQUE(challenge_week_id, local_date)
);

-- Sprint 1A: idempotência do hook (secção 9.3)
CREATE TABLE challenge_processed_quiz (
    quiz_result_id INTEGER PRIMARY KEY REFERENCES quiz_results(id),
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sprint 1A: anti-replay do quiz_session_token (secção 9.7)
CREATE TABLE challenge_consumed_quiz_session (
    jti VARCHAR(64) PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id),
    consumed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sprint 3: adicionar
CREATE TABLE challenge_pause (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL REFERENCES students(id),
    start_week_id VARCHAR(10) NOT NULL,
    end_week_id VARCHAR(10) NOT NULL,
    reason VARCHAR(50) NOT NULL,
    is_exception BOOLEAN DEFAULT FALSE,
    activated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deactivated_at TIMESTAMP,
    UNIQUE(student_id, start_week_id)
);

-- Garantia de max 1 pausa ativa por aluna:
-- SQLite não suporta índice parcial com WHERE, mas a regra é garantida no serviço:
-- ChallengeService.activate_pause() verifica se já existe pausa ativa
-- (deactivated_at IS NULL AND current_week <= end_week_id) antes de inserir nova.
-- Se existir, retorna erro.
-- Além disso, valida duração máxima:
-- - standard: 1-2 semanas
-- - excecional (`is_exception=true` e `reason='doenca'`): até 4 semanas
-- e cooldown de 1 semana entre pausas.
-- Para PostgreSQL (futuro): CREATE UNIQUE INDEX idx_one_active_pause
--   ON challenge_pause(student_id) WHERE deactivated_at IS NULL;

-- Sprint 3: adicionar (nota: Sprints 1-2 calculam conclusão de missão on-the-fly
-- a partir de challenge_week + challenge_day_activity, sem registo persistente de outcome)
CREATE TABLE challenge_week_outcome (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    week_id VARCHAR(10) NOT NULL,
    student_a_id INTEGER NOT NULL REFERENCES students(id),
    student_b_id INTEGER REFERENCES students(id),   -- NULL se semana solo (continuidade)
    outcome_type VARCHAR(20) NOT NULL,      -- 'coop_base', 'coop_quality', 'coop_advanced', 'continuity', 'contribution', 'failed'
    team_xp_snapshot INTEGER,              -- snapshot histórico no momento de fecho da semana (NÃO usado para cálculo live — ver secção 10.3)
    student_a_xp_snapshot INTEGER,
    student_b_xp_snapshot INTEGER,
    badge_awarded VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(week_id, student_a_id)           -- 1 outcome por aluna por semana
);
-- Cardinalidade: cada aluna tem o seu próprio registo de outcome.
-- student_a_id é a aluna dona do registo, student_b_id é a parceira nessa semana.
-- Para uma dupla A+B, existem 2 registos por semana (um de cada perspectiva).

CREATE INDEX idx_outcome_student_a ON challenge_week_outcome(student_a_id);
CREATE INDEX idx_outcome_week ON challenge_week_outcome(week_id);

-- Indexes
CREATE INDEX idx_challenge_week_week_id ON challenge_week(week_id);
CREATE INDEX idx_challenge_week_student ON challenge_week(student_id);
CREATE INDEX idx_challenge_day_date ON challenge_day_activity(local_date);
```

### 10.3 Team XP (calculado, não armazenado)

O `team_xp` da semana é calculado on-the-fly:

```sql
SELECT SUM(individual_xp) as team_xp
FROM challenge_week
WHERE week_id = :week_id
AND student_id IN (:student_id, :partner_id)
```

Não duplicar em coluna — fonte de truth é a soma dos individuais.

## 11. Estrutura do Módulo Backend

```
backend/modules/challenges/
├── __init__.py
├── router.py              # GET /challenge/weekly-status
├── service.py             # ChallengeService
├── repository.py          # ChallengeRepository
├── models.py              # ChallengeWeek, ChallengeDayActivity, ChallengeWeekOutcome
├── ports.py               # ChallengeServicePort, ChallengeRepositoryPort
├── calculator.py          # Sessão válida, XP diário, normalização de score
├── calendar.py            # week_id, local_day, training week
└── constants.py           # MIN_ACTIVE_SECONDS=180, MIN_QUESTIONS=5, XP_BASE=20, etc.
```

Ficheiros existentes a modificar:

- `app_factory.py` — registar `challenges_router`
- `dependencies.py` — adicionar `get_challenge_service()` e injectá-lo em `get_save_quiz_result_use_case()`
- `modules/quizzes/use_cases.py` — `SaveQuizResultUseCase.__init__` ganha parâmetro opcional `challenge_service: ChallengeServicePort | None = None`; hook após `recorder.record()`
- `modules/quizzes/ports.py` — `QuizResultRecorderPort.record()` → `int`; `QuizResultPersistencePort.record_quiz_result()` → `int`
- `modules/quizzes/recorder.py` — `record()` retorna `int`; check `if not quiz_result_id`
- `modules/quizzes/repository.py` — `record_quiz_result()` retorna `result.id` (int) em vez de `True`
- `modules/quizzes/router.py` — `POST /generate-quiz` devolve `quiz_session_token` assinado
- `schemas/study.py` — `QuizResultCreate` inclui `quiz_session_token`
- `modules/quizzes/policies.py` — em modo `COOP_CHALLENGE_ENABLED`, desbloqueios não dependem de XP legacy
- `modules/auth/models.py` — adicionar `challenge_xp`, `partner_id` e `expected_tz_offset`
- `modules/auth/router.py` — incluir `challenge_xp` no response de `/me` (necessário para frontend condicionar source de XP)
- `modules/challenges/repository.py` — consumir `jti` com INSERT único em `challenge_consumed_quiz_session` (anti-replay)

Frontend:

```
frontend/src/components/Challenge/
├── WeeklyChallengeCard.jsx    # Card principal (equipa XP, barra, estado)
└── MissionProgressBar.jsx     # Barra de progresso reutilizável

frontend/src/hooks/
└── useChallengeStatus.js      # Hook para GET /challenge/weekly-status
```

Ficheiros existentes a modificar:

- `services/studyService.js` — adicionar `getChallengeStatus()`
- `services/studyService.js` — enviar `quiz_session_token` em `submitQuizResult()`
- `hooks/useGamification.js` — source de XP condicional (challenge_xp vs stats.total_xp)
- `hooks/useQuiz.js` — guardar `quiz_session_token` vindo de `generateQuiz()` e reenviar no `submitQuizResult()`
- `components/Intro/IntroHeader.jsx` — integrar challenge card ou XP do desafio
- `pages/ResultsPage.jsx` — mostrar contribuição da sessão para a missão

## 12. Endpoint: `GET /challenge/weekly-status`

```json
{
  "week_id": "2026W06",
  "is_training_week": false,
  "team": {
    "partner_name": "Maria",
    "team_xp": 145,
    "mission_base": {
      "target_days_each": 3,
      "completed": true
    },
    "mission_quality": {
      "target_xp": 150,
      "target_quality_days": 4,
      "current_quality_days": 3,
      "completed": false
    }
  },
  "individual": {
    "xp": 75,
    "active_days": 4,
    "daily_breakdown": [
      { "date": "2026-02-03", "xp": 20, "best_score_pct": 70, "quality_bonus": false },
      { "date": "2026-02-04", "xp": 25, "best_score_pct": 85, "quality_bonus": true }
    ]
  },
  "partner": {
    "xp": 70,
    "active_days": 3
  },
  "status": "in_progress",
  "title": {
    "current": "Assistente de Laboratório",
    "current_icon": "Microscope",
    "accumulated_xp": 342,
    "next_title": "Bióloga Júnior",
    "next_xp_threshold": 600
  }
}
```

**Variante: sem parceira (continuidade automática / `partner_id IS NULL`):**

```json
{
  "week_id": "2026W06",
  "is_training_week": false,
  "mode": "solo_continuity",
  "team": null,
  "continuity_mission": {
    "target_xp": 75,
    "target_days": 3,
    "completed": false
  },
  "individual": {
    "xp": 40,
    "active_days": 2,
    "daily_breakdown": [...]
  },
  "partner": null,
  "status": "continuity_in_progress",
  "title": { ... }
}
```

**Variante: ambas em pausa:**

```json
{
  "week_id": "2026W06",
  "is_training_week": false,
  "mode": "all_paused",
  "team": null,
  "individual": {
    "xp": 25,
    "active_days": 1,
    "daily_breakdown": [...]
  },
  "partner": null,
  "status": "all_paused",
  "cooperative_impact": "neutral",
  "message": "Semana de pausa — estuda ao teu ritmo!",
  "title": { ... }
}
```

Semântica de `all_paused`: semana neutra para missão/recompensas/métricas cooperativas. `XP do Desafio` individual e progresso de títulos continuam se houver estudo.

---

## 13. Planeamento Técnico Incremental (Sprints)

Premissas:

- feature flags disponíveis e inicialmente desligadas em produção
- sem quebrar fluxo atual de quiz
- rollout progressivo

Regra principal de execução:

- **cada sprint ativa apenas 1 bloco de complexidade**
- cada sprint tem um **checkpoint de calibração** (não um gate bloqueante)
- **checkpoint pass:** avançar para o sprint seguinte
- **checkpoint warn:** avançar mas priorizar calibração dos thresholds no sprint corrente em paralelo
- **checkpoint block:** só bloquear avanço quando há **regressão clara** (ex.: aluna abandona, bug crítico de XP) — não bloquear por falta de dados ou por fatores externos (férias, doença)
- com N=1 dupla e janelas de 3 semanas, os checkpoints podem alongar o roadmap; aceitar que factores externos (férias, doença) não são sinal de falha de produto
- objetivo de lançamento inicial (Go-Live): fim da **Sprint 3B**; Sprint 4 passa para V1.1 pós-lançamento

### Sprint 0: Fundação técnica (2-3 dias)

Objetivo:

- criar infraestrutura partilhada que todos os sprints precisam

Escopo:

- `feature_flags.py` com `COOP_CHALLENGE_ENABLED`
- `calendar.py` com `get_week_id()`, `get_local_date()`, `is_training_week()`
- testes unitários para edge cases de timezone e limites de semana
- script de backfill de `challenge_xp` a partir de `QuizResult` histórico (escrever e testar com dados de teste — execução contra dados de produção no Sprint 1A)
- seed script para definir par inicial (`partner_id`)
- configuração `CHALLENGE_LAUNCH_DATE`

Checkpoint:

- testes de calendário passam para vários fusos e edge cases (domingo 23:59, segunda 00:01)
- backfill produz valores coerentes com o histórico visível na app

### Sprint 1A: Backend do núcleo mínimo (1 semana)

Objetivo:

- backend funcional com XP diário e status semanal

Escopo funcional:

- modelos: `ChallengeWeek`, `ChallengeDayActivity`
- repositório e serviço com ports
- `calculator.py`: sessão válida, XP diário (+20 base, sem bónus de qualidade)
- hook em `SaveQuizResultUseCase` → `challenge_service.process_session()`
- `GET /challenge/weekly-status` (versão base, só Missão Base)
- migração: adicionar `challenge_xp`, `partner_id` e `expected_tz_offset` a `students` — usar padrão existente de `main.py` com `inspect()` + `ALTER TABLE` condicional (mesma abordagem de `ensure_quiz_result_time_columns`)
- seed: definir `expected_tz_offset` para as 2 alunas (ex.: 0 para WET Portugal)
- executar script de backfill de `challenge_xp` contra dados de produção (secção 9.2)
- desligar dependência de XP legacy no unlock (`QuizUnlockPolicy`) quando `COOP_CHALLENGE_ENABLED=true`
- anti-cheat obrigatório neste sprint: Camadas 1+2+3 de validação de `active_seconds`, com `quiz_session_token` assinado emitido em `/generate-quiz` e validado em `/quiz/result`
- rollout seguro: manter `COOP_CHALLENGE_ENABLED=false` durante toda a Sprint 1A
- compatibilidade obrigatória: backend aceita `quiz_session_token` ausente em 1A sem erro HTTP (graceful degradation para não quebrar frontend pré-1B)
- testes: unitários para calculator, integração para endpoint

Checkpoint:

- todos os testes passam
- endpoint retorna dados corretos para sessão simulada manualmente
- XP não é atribuído quando `active_seconds < 180` ou `total_questions < 5`
- segunda sessão no mesmo dia não gera XP
- sessão com token inválido/expirado não gera XP do desafio
- sessão sem token não gera erro HTTP em 1A (com flag off) e não gera XP do desafio
- replay do mesmo `quiz_session_token` (`jti` já consumido) não gera XP do desafio
- `active_seconds` acima do máximo plausível é capped server-side
- com `COOP_CHALLENGE_ENABLED=true`, unlock não depende de XP legacy

### Sprint 1B: Frontend do núcleo mínimo (1 semana)

Objetivo:

- criança vê o progresso da missão na interface

Escopo funcional:

- `useChallengeStatus.js` — fetch + polling do status
- `WeeklyChallengeCard.jsx` — card com XP equipa, barra de progresso, estado
- `studyService.js` — adicionar `getChallengeStatus()`
- `useGamification.js` — condicionar source de XP (challenge_xp quando flag ativa)
- `IntroHeader.jsx` — mostrar XP do desafio em vez de XP material
- `ResultsPage.jsx` — mostrar "+20 XP do Desafio" após sessão válida
- guard com `VITE_COOP_CHALLENGE_ENABLED`
- após deploy e smoke test E2E, ativar `COOP_CHALLENGE_ENABLED` no início de semana (segunda 00:00 local)
- após ativação da flag, validar smoke test com token obrigatório para elegibilidade de Challenge XP

Métricas obrigatórias (a partir daqui):

- missão base concluída (sim/não por semana)
- ambas ativas >=3 dias (sim/não por semana)
- ambas regressam na semana seguinte (sim/não)

Checkpoint para avançar (adaptado para N=1 dupla — rolling window de 3 semanas):

- nas primeiras 3 semanas, missão base concluída >=1 vez (sinal de viabilidade)
- nas primeiras 3 semanas, ambas ativas >=3 dias em >=2 semanas (sinal de hábito)
- nenhuma aluna abandona (0 semanas com 0 sessões), excluindo semanas `all_paused` do denominador
- sem erros críticos de cálculo de XP/semana
- criança consegue perceber o estado da missão sem ajuda (validação qualitativa)

Nota: com 1 dupla, métricas de taxa (%) são ruído — usar contagens absolutas em janelas de 3+ semanas. Converter para taxas quando N >= 5 duplas.

### Sprint 2: Camada de qualidade (1 semana)

Objetivo:

- adicionar aprendizagem/qualidade sem mudar estrutura mental da criança

Escopo funcional:

- bónus de qualidade `+5` com `best_score_pct >= 80` (normalizado)
- normalização de score por quiz type no `calculator.py`
- meta `Missão Qualidade`: ambas `>=3 dias` E `XP equipa >= 150` E `quality_days_team >= 4` (secção 4.4)
- endpoint atualizado de status com dois níveis de missão (incluindo `target_quality_days` e `current_quality_days`)
- UI: exibição dos 2 níveis (`Base` e `Qualidade`) com indicador de quality days
- `ResultsPage.jsx` — indicar quando bónus de qualidade foi atingido

Métricas obrigatórias do sprint:

- `Mission Quality Completion Rate`
- `Quality Day Rate`
- `Quality Bonus Rate por material` (nova, secção 7.6)
- `Weekly Retention`

Checkpoint para avançar (rolling window 3 semanas):

- missão qualidade concluída >=1 vez nas primeiras 3 semanas com bónus ativo
- bónus de qualidade obtido em >=30% dos dias ativos (contagem absoluta)
- nenhuma aluna reduz dias ativos vs Sprint 1 (sem regressão de hábito)

### Sprint 3: Resiliência de parceria — `Modo Pausa` (1 semana)

Objetivo:

- remover frustração quando uma parceira não pode participar

Escopo funcional:

- flag: `COOP_PAUSE_MODE_ENABLED`
- `Modo Pausa` ativável via script CLI (controlo parental, ex.: `python -m scripts.activate_pause --student_id 1 --start_week 2026W08 --end_week 2026W09 --reason ferias`)
- `Missão de Continuidade` (`XP individual >=75` + `>=3 dias`)
- recompensa de `Continuidade`
- tabela `challenge_week_outcome` para persistir resultados semanais
- estados visuais distintos para `Cooperativa` e `Continuidade`

Métricas obrigatórias do sprint:

- `Partner Block Rate`
- `Continuity Reward Rate`
- `Weekly Retention`

Checkpoint para avançar (observação de 3 semanas):

- se modo pausa ativado, aluna solo completa missão de continuidade >=1 vez
- aluna que usou modo pausa regressa à semana cooperativa seguinte
- missão cooperativa base continua a ser concluída nas semanas sem pausa

### Sprint 3B: Fallback de justiça individual — `Contribuição` (3-5 dias)

Objetivo:

- evitar punir quem teve bom esforço quando a missão de equipa falha

Escopo funcional:

- recompensa de `Contribuição` (`XP individual >=60` + `>=3 dias`, com missão cooperativa falhada)
- estado visual distinto para `Contribuição` (diferente de `Cooperativa` e `Continuidade`)
- histórico simples das últimas 4 semanas

Métricas obrigatórias do sprint:

- `Contribution Reward Rate`
- `Contribution Imbalance`
- `Weekly Retention`

Checkpoint para avançar (observação de 3 semanas):

- contribuição individual não se torna o outcome dominante (<=1 em 3 semanas)
- sem queda de missão cooperativa base (a existência do fallback não desmotiva cooperação)

### Sprint 4 (V1.1 pós-Go-Live): Onboarding e recompensa avançada (1 semana)

Objetivo:

- consolidar feedback emocional e facilitar entrada

Escopo funcional:

- onboarding de 3 ecrãs com `GET /challenge/rules`
- feedback visual imediato na conclusão da missão (confetti, badge)
- ativação da recompensa cooperativa avançada (`>=5 dias ativos` e `XP equipa >=180`)

Métricas recomendadas do sprint:

- onboarding completion rate
- tempo até primeira sessão válida
- `Weekly Retention`

Checkpoint para concluir V1.1:

- onboarding completion rate >= 80%
- sem regressão em métricas anteriores

### Sprint 5: Dashboard de métricas (1 semana, opcional para Go-Live)

Objetivo:

- visualização centralizada para decisões futuras

**Nota importante:** A coleta de dados para métricas (secção 7) é obrigatória e está distribuída nos sprints anteriores — `challenge_week`, `challenge_day_activity` e `challenge_week_outcome` já capturam todos os dados necessários. O que este sprint adiciona é o **dashboard de visualização** e os **alertas automáticos**, que são opcionais para Go-Live.

Critério Go-Live (secção 14, ponto 6) exige que as métricas sejam **consultáveis** (via queries SQL directas à base de dados), não que tenham dashboard visual. Este sprint transforma queries manuais em UI.

Escopo funcional:

- painel admin/parental com métricas da secção 7 (UI)
- alertas automáticos baseados nos quadros de decisão (secção 7.7)
- ajustes finos de thresholds por dados de 4-8 semanas

Saída final do ciclo:

- decisão documentada: manter MVP, calibrar regras, ou expandir para grupos maiores

### Sprint de Estabilidade (1 semana, pós-MVP)

Objetivo:

- hardening baseado em dados reais

Escopo:

- corrigir bugs dos primeiros 2-3 semanas de uso real
- hardening da validação anti-cheat (`active_seconds`) com tuning de margens/heurísticas baseado em dados reais
- performance do endpoint `/challenge/weekly-status` (target: <200ms)
- adicionar indexes em falta se necessário
- calibração de thresholds (dias mínimos, XP equipa 150, quality_days 4, XP avançado 180) baseada em dados reais
- documentar decisões de calibração

---

## 14. Critérios de Aceitação (Go-Live)

1. Go-Live inicial ocorre no fim da **Sprint 3B**.
2. UX principal mostra apenas 1 tipo de XP (`XP do Desafio`).
3. Missão cooperativa funcional: Base = ambas >=3 dias ativos; Qualidade = Base + XP equipa >=150 + quality_days_team >=4.
4. Sem ranking competitivo 1v1 na fase inicial.
5. Títulos mantidos usando o mesmo XP (sem novo sistema paralelo de pontos).
6. Dados para métricas da secção 7 são recolhidos e consultáveis (via SQL ou endpoint). Dashboard visual é desejável mas não bloqueante.
7. `Modo Pausa` ativo para casos reais de ausência da parceira.
8. `partner_id IS NULL` entra automaticamente em `Missão de Continuidade` (sem recompensa cooperativa).
9. Recompensas de fallback (`Continuidade` e `Contribuição`) implementadas e instrumentadas.
10. Script de backfill executado — títulos existentes preservados.
11. Validação server-side de `active_seconds` ativa no Go-Live com as 3 camadas (token assinado + sanity check + heurística).
12. Com `COOP_CHALLENGE_ENABLED=true`, UX e desbloqueios não dependem de XP legacy.
13. `Modo Pausa` com duração limitada e cooldown ativo (sem possibilidade de solo permanente por omissão).
14. Anti-replay ativo: `quiz_session_token.jti` de uso único (reutilização não gera XP do desafio).
15. `all_paused` tratado como semana neutra para missão/métricas cooperativas, sem bloquear XP individual e títulos.
16. Rollout de flags executado em 3 passos: 1A backend com flag off, 1B frontend completo, ativação só após smoke test E2E.
17. Em Sprint 1A, `quiz_session_token` é backward-compatible (ausência não quebra `POST /quiz/result`); após ativação da flag, token válido é obrigatório para Challenge XP.

Itens V1.1 (não bloqueiam Go-Live inicial):

- onboarding de 3 ecrãs em <=30 segundos
- recompensa cooperativa avançada (`>=5 dias` e `>=180 XP`)

## 15. Backlog Futuro: Recompensas Visuais

Objetivo:

- elevar valor percebido das recompensas sem aumentar complexidade das regras

Item de backlog (pós-MVP):

- `Reward Visual System v1`
- catálogo visual por tipo de recompensa:
  - `Cooperativa`: confetti premium, badge de equipa, animação de conquista dupla
  - `Continuidade`: badge menor e feedback de "consistência mantida"
  - `Contribuição`: selo individual de esforço
- variantes sazonais (ex.: tema escola/férias) sem alterar regras de jogo
- guideline de acessibilidade (cores, contraste, motion reduzido)
- teste A/B simples para medir impacto em retenção semanal e re-engagement pós-falha

## 16. Backlog Futuro: Evolução da Integração

Itens para considerar quando escalar para turmas:

- migrar hook síncrono para task queue async (Redis/arq)
- tabela `teams` many-to-many para substituir `partner_id`
- feature flags per-student (database-backed)
- scheduled jobs para week rollover automático (cron/celery)
- sistema de convites para emparelhamento via UI

---

## Changelog v1 → v2

| Secção | Mudança | Motivo |
|--------|---------|--------|
| 4.3 (nova) | Normalização de `best_score_pct` | Score varia entre quiz types |
| 7.6 (nova) | Métricas de fairness por material | Materiais fáceis podem distorcer bónus qualidade |
| 9 (nova) | Decisões técnicas pré-implementação | Lacunas críticas identificadas na auditoria |
| 10 (nova) | Modelo de dados completo | Schema SQL explícito com indexes |
| 11 (nova) | Estrutura do módulo backend | Ficheiros a criar e modificar |
| 12 (nova) | Schema do endpoint | JSON response definido |
| 13 (revista) | Sprints ajustados: 0+1A+1B+2+3+4+5+Estab | Sprint 1 dividido, 3+4 fundidos, Sprint 5 split |
| 14 (revista) | Critérios de aceitação: +2 novos | Backfill e validação server-side |
| 16 (nova) | Backlog de evolução técnica | Itens para escalar além de 2 utilizadoras |

## Changelog v2 → v3

| Issue | Severidade | Correção |
|-------|-----------|----------|
| team_xp armazenado vs calculado | Bloqueador | 9.8: removida referência a coluna `team_xp`, clarificado que é derivado; update atómico aplicado a `individual_xp` |
| challenge_week_outcome sem identidade | Bloqueador | 10.2: adicionados `student_a_id`, `student_b_id` com FKs e UNIQUE constraint |
| Gates estatísticos com N=1 | Bloqueador | 13 (todos os gates): substituídas percentagens por contagens absolutas em rolling windows de 3 semanas; nota sobre converter para taxas com N>=5 |
| Timezone manipulation | Bloqueador | 9.6: adicionada validação de range + `expected_tz_offset` como guardrail; 10.1: coluna adicionada |
| partner_id sem simetria | Alta | 9.5: adicionada regra de simetria, endpoint transacional, validação no ChallengeService |
| Backfill sem timezone histórico | Alta | 9.2: definido uso de `expected_tz_offset` fixo para backfill, com análise de erro máximo |
| active_seconds confia em duration_seconds | Alta | 9.7: validação em 3 camadas com estimativa server-side baseada em timestamps de geração/submissão |
| Go-Live vs Sprint 5 opcional | Alta | Sprint 5: clarificado que coleta é obrigatória (sprints anteriores), dashboard é opcional; critério 14.6 ajustado |
| Material fairness sem suporte no schema | Média | 10.2: adicionado `best_score_material_id` a `challenge_day_activity` |
| Sprint 3 mistura duas features | Média | 13: separado em Sprint 3 (Modo Pausa, 1 semana) e Sprint 3B (Contribuição, 3-5 dias) |
| Recompensa avançada definida cedo | Média | 4.4: adicionada nota "(ativação: Sprint 4)" e explicação da razão do adiamento |

## Changelog v3 → v3.1

| Issue | Severidade | Correção |
|-------|-----------|----------|
| Hook sem política transacional/idempotente | Bloqueador | 9.3: best-effort (try/except, não falha /quiz/result) + idempotência por `quiz_result_id` + coluna `last_quiz_result_id` em `challenge_day_activity` |
| Missão Base e anti-free-rider redundantes | Alta | 4.4+4.5: análise matemática explícita; Missão Base simplificada para "ambas >=3 dias"; anti-free-rider removido (implícito nos 3 dias); `anti_freeride_ok` removido do payload |
| team_xp em challenge_week_outcome contradição | Alta | 10.2: colunas renomeadas para `team_xp_snapshot`, `student_a_xp_snapshot`, `student_b_xp_snapshot` — clarificado como snapshot histórico |
| Gates bloqueiam demasiado com N=1 | Alta | 13: "Gate" renomeado para "Checkpoint"; regra de execução reformulada com 3 níveis (pass/warn/block); só bloqueia em regressão clara |
| expected_tz_offset em falta no Sprint 1A | Média | 13 Sprint 1A: adicionada migração de `expected_tz_offset` + seed |
| Payload de título inconsistente | Média | 12: corrigido exemplo (342 XP → Assistente de Laboratório); 5: tabela de thresholds oficiais congelada |
| Endpoints admin sem RBAC | Média | 9.5+Sprint 3: substituídos endpoints admin por scripts CLI; RBAC adiado para fase de turmas |

## Changelog v3.1 → v3.2

| Issue | Severidade | Correção |
|-------|-----------|----------|
| Missão Qualidade sem qualidade real | Alta | 4.4+4.5: adicionada condição `quality_days_team >= 4`; 12: endpoint inclui `target_quality_days` e `current_quality_days`; 14: critério Go-Live atualizado |
| Modo Pausa sem schema de persistência | Alta | 4.6: definida tabela `challenge_pause` com `start_week_id`, `end_week_id`, `reason`; regras de ativação/desativação; 10.2: tabela adicionada ao schema |
| Idempotência frágil com `last_quiz_result_id` | Média | 9.3: substituída coluna por tabela `challenge_processed_quiz` com `UNIQUE(quiz_result_id)`; INSERT OR IGNORE atómico; 10.2: tabela adicionada |
| Contradição CLI vs endpoint no pairing | Média | 9.5: removida referência a `POST /admin/pair-students`; mantido apenas script CLI |
| Quadro de decisão referencia threshold removido | Média | 7.7: substituída ação "30→40 XP" por "aumentar dias mínimos ou condição de qualidade" |
| Linguagem mista na Missão Base | Média | 4.4, 7.7, 14, Sprint Estab: normalizado — Base = critério de dias; XP 120 é guardrail técnico |

## Changelog v3.2 → v3.3

| Issue | Severidade | Correção |
|-------|-----------|----------|
| Hook usa `result.id` mas `recorder.record()` retorna None | Alta | 9.3: documentado pré-requisito — `record()` e `record_quiz_result()` devem retornar `quiz_result_id`; ports atualizados |
| Idempotência marca antes de processar (risco de perda) | Alta | 9.3: invertida ordem — process primeiro, mark depois, tudo na mesma transação |
| Sprint 2 com regra antiga da Missão Qualidade | Média | Sprint 2: atualizado escopo para incluir `quality_days_team >= 4` e campos no endpoint |
| Max 1 pausa ativa sem constraint de BD | Média | 10.2: documentada proteção no serviço + índice parcial único para PostgreSQL futuro |
| Missão Base com `target: 120` no payload | Média | 12: substituído por `target_days_each: 3` para consistência semântica |

## Changelog v3.3 → v3.4

| Issue | Severidade | Correção |
|-------|-----------|----------|
| `quiz_generated_at` sem mecanismo de armazenamento nem sprint scope | Alta | 9.7: abordagem definida (timestamp no response de /generate-quiz, frontend reenvia); implementação faseada — Camada 3 no Sprint 1A, Camadas 1+2 no Sprint de Estabilidade; Go-Live critério 12 atualizado |
| `SaveQuizResultUseCase` não recebe `challenge_service` — DI wiring omitido | Alta | 11: adicionadas todas as alterações a ficheiros existentes (construtor, ports, recorder, repository, dependencies.py, auth/router.py para /me) |
| Normalização de score: `total_questions` pode divergir de `len(analytics_data)` | Alta | 4.3: nota de implementação com denominador explícito e validação |
| `quality_days_team` sem definição de cálculo exacta | Média | 4.4: query SQL explícita + clarificação de contagem (soma de ambas, não dias únicos) |
| `individual_xp` vs `SUM(daily_xp)` sem política definida | Média | 9.8: tabela de filosofia derivação vs armazenamento; `individual_xp` é autoritativo com query de reconciliação |
| `active_days_count` redundante sem mecanismo de update | Média | 9.8: documentado update atómico no `process_session()` |
| Endpoint sem schema para solo mode (`partner_id IS NULL`) | Média | 12: adicionada variante solo com `"mode": "solo"`, `"team": null` |
| `challenge_week_outcome` criada no Sprint 3 mas referenciada desde Sprint 1 | Média | 10.2: nota explícita — Sprints 1-2 calculam on-the-fly, sem registo persistente |
| Frontend `/me` não retorna `challenge_xp` | Média | 11: `modules/auth/router.py` adicionado à lista de ficheiros a modificar |
| `Student.total_xp` vs `Student.challenge_xp` coexistência subdocumentada | Média | 9.1: nota de coexistência com plano de reconciliação futuro |
| `challenge_week_outcome` UNIQUE semantics ambígua | Média | 10.2: clarificada cardinalidade — 1 registo por aluna, `student_a_id` é dona |
| Estratégia de migração não documentada | Média | Sprint 1A: usar padrão existente `main.py` com `inspect()` + `ALTER TABLE` condicional |
| Terminologia `building/established` incompleta | Baixa | 7.3: adicionados todos os estados do codebase (`not_seen` → `exploring` → `building` → `established`) |
| Missão Qualidade mínimo viável mais restritivo do que aparenta | Baixa | 4.4: cenários mínimos com análise matemática |
| Endpoint response para "ambas em pausa" não definido | Baixa | 4.6 + 12: adicionado `"status": "all_paused"` com mensagem amigável |
| Sprint 0 "criar script" vs Sprint 1A "executar" pouco claro | Baixa | Sprint 0: clarificado "(escrever e testar)" vs Sprint 1A: "contra dados de produção" |
| Transação do `process_session()` após commit do quiz — scope | Baixa | 9.3: nota sobre `db.begin_nested()` (SAVEPOINT semantics) |

## Changelog v3.4 → v3.5

| Issue | Severidade | Correção |
|-------|-----------|----------|
| Anti-cheat fraco no Go-Live (`active_seconds`) | Alta | 9.7 + Sprint 1A + secção 14: Camadas 1+2+3 passam a obrigatórias no Go-Live; não ficam adiadas para Estabilidade |
| `quiz_generated_at` reenviado pelo cliente é frágil | Alta | 9.7: substituído por `quiz_session_token` assinado no `/generate-quiz`, validado no `/quiz/result` |
| "1 XP" em UX vs unlock legacy por XP | Média | 9.1 + Sprint 1A + secção 14: com `COOP_CHALLENGE_ENABLED=true`, desbloqueios deixam de depender de XP legacy |
| `Modo Pausa` podia virar bypass permanente | Média | 4.6 + 7.4 + 7.7 + 10.2 + Sprint 3 + secção 14: pausa com fim obrigatório, duração máxima, exceção médica controlada e cooldown |

## Changelog v3.5 → v3.6

| Issue | Severidade | Correção |
|-------|-----------|----------|
| `quiz_session_token` sem proteção de replay | Alta | 9.7 + 10.2 + Sprint 1A + secção 14: adicionado `jti` de uso único com tabela `challenge_consumed_quiz_session`; replay não gera Challenge XP |
| Estado de pausa ativa ambíguo após `end_week_id` | Média | 4.6 + 10.2: pausa ativa definida por `current_week <= end_week_id`; auto-close ao ultrapassar semana final |
| `all_paused` ambíguo para hábito/abandono | Média | 4.6 + 7.1 + 12 + secção 14: definido como semana neutra para métricas cooperativas (sem contar como falha) |

## Changelog v3.6 → v3.7

| Issue | Severidade | Correção |
|-------|-----------|----------|
| `jti` anti-replay podia bloquear retry legítimo em falha transitória | Alta | 9.3 + 9.7: definido fluxo atómico único (`is_processed` + `consume_jti` + `apply_xp` + `mark_processed`) com rollback total |
| Checkpoint Sprint 1B podia tratar `all_paused` como abandono | Média | Sprint 1B: checkpoint atualizado para excluir semanas `all_paused` do denominador |
| Regra de denominador `all_paused` incompleta (só retenção/abandono) | Média | 7.1 + 7.7: regra de denominador expandida para métricas semanais (refinada na v3.8 para escopo cooperativo) |

## Changelog v3.7 → v3.8

| Issue | Severidade | Correção |
|-------|-----------|----------|
| Ambiguidade de lançamento (Sprint 3B vs Sprint 4) | Alta | 13 + 14: Go-Live inicial fixado no fim da Sprint 3B; Sprint 4 passa para V1.1 pós-Go-Live |
| Rollout backend/frontend sem coreografia explícita de flags | Alta | 9.4 + Sprint 1A/1B + secção 14: definida sequência `1A backend off -> 1B frontend -> ativação após E2E`, com janela recomendada na segunda-feira |
| `partner_id IS NULL` sem regra funcional final | Média | 4.6 + 9.5 + 12 + secção 14: definido `solo_continuity` automático com missão de continuidade e sem recompensa cooperativa |
| `all_paused` bloqueava progresso individual | Média | 4.6 + 7.1 + 7.7 + 12 + secção 14: `all_paused` neutro só para missão/métricas cooperativas; XP individual e títulos continuam com estudo |

## Changelog v3.8 → v3.9

| Issue | Severidade | Correção |
|-------|-----------|----------|
| Risco de quebra no rollout 1A→1B por obrigatoriedade implícita de `quiz_session_token` | Alta | 9.7 + Sprint 1A/1B + secção 14: definida política de compatibilidade (token opcional com flag off) e obrigatoriedade de token válido para Challenge XP apenas após ativação da flag |
