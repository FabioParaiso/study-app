import { renderHook, act } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { useQuizEngine } from './useQuizEngine';

describe('useQuizEngine', () => {
    const sampleQuestions = [
        { question: "Q1", options: ["A", "B"], correctIndex: 0, topic: "Math" },
        { question: "Q2", options: ["C", "D"], correctIndex: 1, topic: "Science" },
        { question: "Q3", options: ["E", "F"], correctIndex: 0, topic: "History" }
    ];

    it('initializes with default state', () => {
        const { result } = renderHook(() => useQuizEngine());

        expect(result.current.gameState).toBe('intro');
        expect(result.current.score).toBe(0);
        expect(result.current.streak).toBe(0);
        expect(result.current.currentQuestionIndex).toBe(0);
        expect(result.current.questions).toEqual([]);
        expect(result.current.userAnswers).toEqual({});
    });

    it('initQuiz sets questions and switches to playing state', () => {
        const { result } = renderHook(() => useQuizEngine());

        act(() => {
            result.current.initQuiz(sampleQuestions);
        });

        expect(result.current.gameState).toBe('playing');
        expect(result.current.questions).toEqual(sampleQuestions);
        expect(result.current.currentQuestionIndex).toBe(0);
    });

    it('recordAnswer increments score and streak on correct answer', () => {
        const { result } = renderHook(() => useQuizEngine());

        act(() => {
            result.current.initQuiz(sampleQuestions);
        });

        act(() => {
            const returnValue = result.current.recordAnswer(0, 0, true);
            expect(returnValue).toBe('correct');
        });

        expect(result.current.score).toBe(1);
        expect(result.current.streak).toBe(1);
        expect(result.current.showFeedback).toBe(true);
        expect(result.current.userAnswers[0]).toBe(0);
    });

    it('recordAnswer resets streak on incorrect answer', () => {
        const { result } = renderHook(() => useQuizEngine());

        act(() => {
            result.current.initQuiz(sampleQuestions);
        });

        // Correct answer first to build streak
        act(() => {
            result.current.recordAnswer(0, 0, true);
        });

        expect(result.current.streak).toBe(1);

        // Incorrect answer resets streak
        act(() => {
            const returnValue = result.current.recordAnswer(1, 0, false);
            expect(returnValue).toBe('incorrect');
        });

        expect(result.current.streak).toBe(0);
        expect(result.current.score).toBe(1); // Score unchanged
    });

    it('recordAnswer tracks missed indices on incorrect', () => {
        const { result } = renderHook(() => useQuizEngine());

        act(() => {
            result.current.initQuiz(sampleQuestions);
        });

        act(() => {
            result.current.recordAnswer(0, 1, false);
        });

        expect(result.current.missedIndices).toContain(0);
        expect(result.current.missedIndices.length).toBe(1);
    });

    it('recordAnswer does not duplicate missed indices', () => {
        const { result } = renderHook(() => useQuizEngine());

        act(() => {
            result.current.initQuiz(sampleQuestions);
        });

        act(() => {
            result.current.recordAnswer(0, 1, false);
            result.current.recordAnswer(0, 1, false); // Duplicate
        });

        expect(result.current.missedIndices.filter(i => i === 0).length).toBe(1);
    });

    it('advanceQuestion moves to next question', () => {
        const { result } = renderHook(() => useQuizEngine());

        act(() => {
            result.current.initQuiz(sampleQuestions);
        });

        act(() => {
            const finished = result.current.advanceQuestion();
            expect(finished).toBe(false);
        });

        expect(result.current.currentQuestionIndex).toBe(1);
        expect(result.current.showFeedback).toBe(false);
    });

    it('advanceQuestion transitions to results on last question', () => {
        const { result } = renderHook(() => useQuizEngine());

        act(() => {
            result.current.initQuiz(sampleQuestions);
        });

        // Advance to last question
        act(() => {
            result.current.advanceQuestion();
            result.current.advanceQuestion();
        });

        expect(result.current.currentQuestionIndex).toBe(2);

        // Advance from last question
        act(() => {
            const finished = result.current.advanceQuestion();
            expect(finished).toBe(true);
        });

        expect(result.current.gameState).toBe('results');
    });

    it('recordEvaluation stores open-ended evaluation data', () => {
        const { result } = renderHook(() => useQuizEngine());

        act(() => {
            result.current.initQuiz(sampleQuestions);
        });

        const evalData = { score: 85, feedback: "Great!" };

        act(() => {
            result.current.recordEvaluation(0, evalData, "User's text");
        });

        expect(result.current.openEndedEvaluations[0]).toEqual({
            ...evalData,
            userText: "User's text"
        });
    });

    it('maintains streak across multiple correct answers', () => {
        const { result } = renderHook(() => useQuizEngine());

        act(() => {
            result.current.initQuiz(sampleQuestions);
        });

        act(() => {
            result.current.recordAnswer(0, 0, true);
            result.current.recordAnswer(1, 1, true);
            result.current.recordAnswer(2, 0, true);
        });

        expect(result.current.streak).toBe(3);
        expect(result.current.score).toBe(3);
    });
});
