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

    it('does not enter playing state when generated quiz is empty', async () => {
        const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
        try {
            studyService.generateQuiz.mockResolvedValue([]);

            const { result } = renderHook(() => useQuiz({ id: 1 }, 10));

            await act(async () => {
                await result.current.startQuiz('multiple-choice', 'all');
            });

            expect(result.current.gameState).toBe('intro');
            expect(result.current.quizType).toBe(null);
            expect(result.current.errorMsg).toContain('Não foi possível gerar perguntas');
        } finally {
            consoleSpy.mockRestore();
        }
    });

    it('keeps combo streak at 10 for 10 consecutive correct MCQ answers', async () => {
        const questions = Array.from({ length: 10 }, (_, idx) => ({
            question: `Q${idx + 1}`,
            correctIndex: idx % 4,
            concepts: [`C${idx + 1}`]
        }));

        studyService.generateQuiz.mockResolvedValue(questions);
        studyService.submitQuizResult.mockResolvedValue({});

        const { result } = renderHook(() => useQuiz({ id: 1 }, 10));

        await act(async () => {
            await result.current.startQuiz('multiple-choice', 'all');
        });

        for (let i = 0; i < questions.length; i += 1) {
            act(() => {
                result.current.handleAnswer(i, questions[i].correctIndex, () => {});
            });

            await act(async () => {
                await result.current.nextQuestion();
            });
        }

        expect(result.current.gameState).toBe('results');
        expect(result.current.score).toBe(10);
        expect(result.current.streak).toBe(10);

        await waitFor(() => {
            expect(studyService.submitQuizResult).toHaveBeenCalled();
        });

        const call = studyService.submitQuizResult.mock.calls[0];
        expect(call[0]).toBe(10);
    });

    it('updates combo streak for open-ended evaluations and resets on low score', async () => {
        const questions = [
            { question: 'Q1', concepts: ['C1'] },
            { question: 'Q2', concepts: ['C2'] },
            { question: 'Q3', concepts: ['C3'] }
        ];

        studyService.generateQuiz.mockResolvedValue(questions);
        studyService.evaluateAnswer
            .mockResolvedValueOnce({ score: 85 })
            .mockResolvedValueOnce({ score: 70 })
            .mockResolvedValueOnce({ score: 40 });
        studyService.submitQuizResult.mockResolvedValue({});

        const { result } = renderHook(() => useQuiz({ id: 1 }, 10));

        await act(async () => {
            await result.current.startQuiz('open-ended', 'all');
        });

        await act(async () => {
            await result.current.handleEvaluation('A1', () => {});
        });
        expect(result.current.streak).toBe(1);

        await act(async () => {
            await result.current.nextQuestion();
            await result.current.handleEvaluation('A2', () => {});
        });
        expect(result.current.streak).toBe(2);

        await act(async () => {
            await result.current.nextQuestion();
            await result.current.handleEvaluation('A3', () => {});
        });
        expect(result.current.streak).toBe(0);
    });

    it('updates combo streak for short-answer evaluations', async () => {
        const questions = [
            { question: 'Q1', concepts: ['C1'] }
        ];

        studyService.generateQuiz.mockResolvedValue(questions);
        studyService.evaluateAnswer.mockResolvedValue({ score: 60 });

        const { result } = renderHook(() => useQuiz({ id: 1 }, 10));

        await act(async () => {
            await result.current.startQuiz('short_answer', 'all');
        });

        await act(async () => {
            await result.current.handleShortAnswer('Resposta', () => {});
        });

        expect(studyService.evaluateAnswer).toHaveBeenCalledWith('Q1', 'Resposta', 'short_answer');
        expect(result.current.streak).toBe(1);
    });

    it('forwards quiz_session_token when submitting quiz result', async () => {
        const questions = [
            { question: 'Q1', correctIndex: 0, concepts: ['C1'] },
            { question: 'Q2', correctIndex: 1, concepts: ['C2'] },
            { question: 'Q3', correctIndex: 0, concepts: ['C3'] },
            { question: 'Q4', correctIndex: 1, concepts: ['C4'] },
            { question: 'Q5', correctIndex: 0, concepts: ['C5'] }
        ];

        studyService.generateQuiz.mockResolvedValue({
            questions,
            quiz_session_token: 'session-123'
        });
        studyService.submitQuizResult.mockResolvedValue({});

        const { result } = renderHook(() => useQuiz({ id: 1 }, 10));

        await act(async () => {
            await result.current.startQuiz('multiple-choice', 'all');
        });

        for (let i = 0; i < questions.length; i += 1) {
            act(() => {
                result.current.handleAnswer(i, questions[i].correctIndex, () => {});
            });
            await act(async () => {
                await result.current.nextQuestion();
            });
        }

        await waitFor(() => {
            expect(studyService.submitQuizResult).toHaveBeenCalled();
        });

        const call = studyService.submitQuizResult.mock.calls[0];
        expect(call[8]).toBe('session-123');
    });

    it('marks challenge session as eligible when MCQ has 10 completed answers', async () => {
        const questions = Array.from({ length: 10 }, (_, idx) => ({
            question: `Q${idx + 1}`,
            correctIndex: idx % 4,
            concepts: [`C${idx + 1}`]
        }));

        studyService.generateQuiz.mockResolvedValue({ questions, quiz_session_token: 'session-xyz' });
        studyService.submitQuizResult.mockResolvedValue({});

        const { result } = renderHook(() => useQuiz({ id: 1 }, 10));

        await act(async () => {
            await result.current.startQuiz('multiple-choice', 'all');
        });

        for (let i = 0; i < questions.length; i += 1) {
            act(() => {
                result.current.handleAnswer(i, questions[i].correctIndex, () => {});
            });
            await act(async () => {
                await result.current.nextQuestion();
            });
        }

        expect(result.current.challengeSessionFeedback.eligible).toBe(true);
        expect(result.current.challengeSessionFeedback.reason).toBe('valid_session');
        expect(result.current.challengeSessionFeedback.estimatedXp).toBe(20);
    });

    it('marks challenge session as invalid_question_count when MCQ does not have 10 questions', async () => {
        const questions = [
            { question: 'Q1', correctIndex: 0, concepts: ['C1'] },
            { question: 'Q2', correctIndex: 1, concepts: ['C2'] },
            { question: 'Q3', correctIndex: 0, concepts: ['C3'] },
            { question: 'Q4', correctIndex: 1, concepts: ['C4'] },
            { question: 'Q5', correctIndex: 0, concepts: ['C5'] }
        ];

        studyService.generateQuiz.mockResolvedValue({ questions, quiz_session_token: 'session-abc' });
        studyService.submitQuizResult.mockResolvedValue({});

        const { result } = renderHook(() => useQuiz({ id: 1 }, 10));

        await act(async () => {
            await result.current.startQuiz('multiple-choice', 'all');
        });

        for (let i = 0; i < questions.length; i += 1) {
            act(() => {
                result.current.handleAnswer(i, questions[i].correctIndex, () => {});
            });
            await act(async () => {
                await result.current.nextQuestion();
            });
        }

        await waitFor(() => {
            expect(result.current.challengeSessionFeedback.eligible).toBe(false);
            expect(result.current.challengeSessionFeedback.reason).toBe('invalid_question_count');
            expect(result.current.challengeSessionFeedback.estimatedXp).toBe(0);
        });
    });

    it('refreshes challenge status immediately after a valid quiz submission', async () => {
        const questions = Array.from({ length: 10 }, (_, idx) => ({
            question: `Q${idx + 1}`,
            correctIndex: idx % 4,
            concepts: [`C${idx + 1}`]
        }));
        const refreshChallengeStatus = vi.fn().mockResolvedValue({});

        studyService.generateQuiz.mockResolvedValue({ questions, quiz_session_token: 'session-refresh' });
        studyService.submitQuizResult.mockResolvedValue({});

        const { result } = renderHook(() => useQuiz({ id: 1 }, 10, { refreshChallengeStatus }));

        await act(async () => {
            await result.current.startQuiz('multiple-choice', 'all');
        });

        for (let i = 0; i < questions.length; i += 1) {
            act(() => {
                result.current.handleAnswer(i, questions[i].correctIndex, () => {});
            });
            await act(async () => {
                await result.current.nextQuestion();
            });
        }

        await waitFor(() => {
            expect(studyService.submitQuizResult).toHaveBeenCalledTimes(1);
            expect(refreshChallengeStatus).toHaveBeenCalled();
        });
    });
});
