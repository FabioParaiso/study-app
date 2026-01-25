export const normalizeConcepts = (concepts) => {
    if (!Array.isArray(concepts)) return [];

    const cleaned = concepts
        .filter((concept) => typeof concept === 'string')
        .map((concept) => concept.trim())
        .filter((concept) => concept.length > 0);

    const seen = new Set();
    const unique = [];
    cleaned.forEach((concept) => {
        const key = concept.toLowerCase();
        if (seen.has(key)) return;
        seen.add(key);
        unique.push(concept);
    });

    return unique;
};

export const buildDetailedResults = ({
    questions,
    userAnswers,
    openEndedEvaluations,
    quizType
}) => {
    const detailedResults = [];
    const errors = [];

    if (!Array.isArray(questions)) {
        errors.push({ index: null, reason: 'questions_not_array' });
        return { detailedResults, errors };
    }

    questions.forEach((q, idx) => {
        let correct = false;

        if (quizType === 'multiple-choice') {
            const ua = userAnswers?.[idx];
            correct = ua !== undefined && ua === q.correctIndex;
        } else {
            const evalData = openEndedEvaluations?.[idx];
            correct = !!(evalData && evalData.score >= 50);
        }

        const rawConcepts = q?.concepts;
        const concepts = normalizeConcepts(rawConcepts);
        if (concepts.length === 0) {
            const reason = Array.isArray(rawConcepts) ? 'empty_concepts' : 'invalid_concepts';
            errors.push({ index: idx, reason });
            return;
        }

        concepts.forEach((conceptName) => {
            detailedResults.push({
                topic: conceptName,
                is_correct: correct
            });
        });
    });

    return { detailedResults, errors };
};
