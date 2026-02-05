import { describe, it, expect } from 'vitest';
import { normalizeConcepts, buildDetailedResults } from './quizAnalytics';

describe('normalizeConcepts', () => {
    it('trims, filters invalid values, and dedupes case-insensitive', () => {
        const input = [' Cell ', 'cell', '', '  ', null, 42, 'Nucleus'];
        const result = normalizeConcepts(input);
        expect(result).toEqual(['Cell', 'Nucleus']);
    });

    it('returns empty array for non-array inputs', () => {
        expect(normalizeConcepts(null)).toEqual([]);
        expect(normalizeConcepts('Cell')).toEqual([]);
    });
});

describe('buildDetailedResults', () => {
    it('builds one analytics entry per unique concept in multiple choice', () => {
        const questions = [
            { correctIndex: 1, concepts: ['A', 'B', 'a'] },
            { correctIndex: 0, concepts: ['C'] }
        ];
        const userAnswers = { 0: 1, 1: 1 };

        const { detailedResults, errors } = buildDetailedResults({
            questions,
            userAnswers,
            openEndedEvaluations: {},
            quizType: 'multiple-choice'
        });

        expect(errors).toEqual([]);
        expect(detailedResults).toEqual([
            { topic: 'A', is_correct: true },
            { topic: 'B', is_correct: true },
            { topic: 'C', is_correct: false }
        ]);
    });

    it('uses evaluation scores for open-ended correctness', () => {
        const questions = [
            { concepts: ['Concept'] },
            { concepts: ['Second'] }
        ];
        const openEndedEvaluations = {
            0: { score: 50 },
            1: { score: 40 }
        };

        const { detailedResults, errors } = buildDetailedResults({
            questions,
            userAnswers: {},
            openEndedEvaluations,
            quizType: 'open-ended'
        });

        expect(errors).toEqual([]);
        expect(detailedResults).toEqual([
            { topic: 'Concept', is_correct: true },
            { topic: 'Second', is_correct: false }
        ]);
    });

    it('returns errors when concepts are missing or invalid', () => {
        const questions = [
            { correctIndex: 0, concepts: [] },
            { correctIndex: 0 },
            { correctIndex: 0, concepts: ['  ', 42] }
        ];

        const { detailedResults, errors } = buildDetailedResults({
            questions,
            userAnswers: { 0: 0, 1: 0, 2: 0 },
            openEndedEvaluations: {},
            quizType: 'multiple-choice'
        });

        expect(detailedResults).toEqual([]);
        expect(errors.map((err) => err.index)).toEqual([0, 1, 2]);
    });

    it('includes question_topic to disambiguate duplicate concept names', () => {
        const questions = [
            { topic: 'Saúde da Pele', correctIndex: 0, concepts: ['Cuidados Específicos'] }
        ];

        const { detailedResults, errors } = buildDetailedResults({
            questions,
            userAnswers: { 0: 0 },
            openEndedEvaluations: {},
            quizType: 'multiple-choice'
        });

        expect(errors).toEqual([]);
        expect(detailedResults).toEqual([
            {
                topic: 'Cuidados Específicos',
                question_topic: 'Saúde da Pele',
                is_correct: true
            }
        ]);
    });
});
