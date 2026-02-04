import { renderHook, act, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { useQuiz } from './useQuiz';
import { studyService } from '../services/studyService';

vi.mock('../services/studyService', () => ({
    studyService: {
        generateQuiz: vi.fn(),
        evaluateAnswer: vi.fn(),
        submitQuizResult: vi.fn()
    }
}));

describe('useQuiz', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('submits average score for open-ended quizzes', async () => {
        const questions = [
            { question: 'Q1', concepts: ['C1'] },
            { question: 'Q2', concepts: ['C2'] }
        ];

        studyService.generateQuiz.mockResolvedValue(questions);
        studyService.evaluateAnswer
            .mockResolvedValueOnce({ score: 80 })
            .mockResolvedValueOnce({ score: 60 });
        studyService.submitQuizResult.mockResolvedValue({});

        const { result } = renderHook(() => useQuiz({ id: 1 }, 10));

        await act(async () => {
            await result.current.startQuiz('open-ended', 'all');
        });

        await act(async () => {
            await result.current.handleEvaluation('Answer 1', () => {});
        });
        await act(async () => {
            await result.current.nextQuestion();
        });

        await act(async () => {
            await result.current.handleEvaluation('Answer 2', () => {});
        });
        await act(async () => {
            await result.current.nextQuestion();
        });

        await waitFor(() => {
            expect(studyService.submitQuizResult).toHaveBeenCalled();
        });

        const call = studyService.submitQuizResult.mock.calls[0];
        expect(call[0]).toBe(70);
    });

    it('submits raw correct count for multiple-choice quizzes', async () => {
        const questions = [
            { question: 'Q1', correctIndex: 0, concepts: ['C1'] },
            { question: 'Q2', correctIndex: 1, concepts: ['C2'] }
        ];

        studyService.generateQuiz.mockResolvedValue(questions);
        studyService.submitQuizResult.mockResolvedValue({});

        const { result } = renderHook(() => useQuiz({ id: 1 }, 10));

        await act(async () => {
            await result.current.startQuiz('multiple-choice', 'all');
        });

        act(() => {
            result.current.handleAnswer(0, 0, () => {});
            result.current.handleAnswer(1, 1, () => {});
        });

        await act(async () => {
            await result.current.nextQuestion();
        });
        await act(async () => {
            await result.current.nextQuestion();
        });

        await waitFor(() => {
            expect(studyService.submitQuizResult).toHaveBeenCalled();
        });

        const call = studyService.submitQuizResult.mock.calls[0];
        expect(call[0]).toBe(2);
    });

    it('submits results even when concepts are missing', async () => {
        const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
        try {
            const questions = [
                { question: 'Q1', correctIndex: 0 },
                { question: 'Q2', correctIndex: 1 }
            ];

            studyService.generateQuiz.mockResolvedValue(questions);
            studyService.submitQuizResult.mockResolvedValue({});

            const { result } = renderHook(() => useQuiz({ id: 1 }, 10));

            await act(async () => {
                await result.current.startQuiz('multiple-choice', 'all');
            });

            act(() => {
                result.current.handleAnswer(0, 0, () => {});
                result.current.handleAnswer(1, 1, () => {});
            });

            await act(async () => {
                await result.current.nextQuestion();
            });
            await act(async () => {
                await result.current.nextQuestion();
            });

            await waitFor(() => {
                expect(studyService.submitQuizResult).toHaveBeenCalled();
            });
        } finally {
            consoleSpy.mockRestore();
        }
    });
});
