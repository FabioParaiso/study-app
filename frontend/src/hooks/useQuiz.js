import { useState, useRef, useEffect, useCallback } from 'react';
import { studyService } from '../services/studyService';
import { useQuizEngine } from './useQuizEngine';
import { calculateXPFromScore } from '../utils/xpCalculator';
import { buildDetailedResults } from '../utils/quizAnalytics';

const IDLE_THRESHOLD_MS = 60 * 1000;
const EXPECTED_QUESTIONS_BY_TYPE = {
    'multiple-choice': 10,
    short_answer: 8,
    'open-ended': 5
};

function getChallengeSessionFeedback(quizType, questionsCount, detailedResultsCount, activeSeconds) {
    const expectedCount = EXPECTED_QUESTIONS_BY_TYPE[quizType];
    const baseFeedback = {
        eligible: false,
        estimatedXp: 0,
        reason: 'unknown_quiz_type',
        activeSeconds,
        totalQuestions: questionsCount
    };

    if (!expectedCount) {
        return baseFeedback;
    }

    if (questionsCount !== expectedCount) {
        return {
            ...baseFeedback,
            reason: 'invalid_question_count'
        };
    }

    if (detailedResultsCount !== questionsCount) {
        return {
            ...baseFeedback,
            reason: 'incomplete_submission'
        };
    }

    return {
        ...baseFeedback,
        eligible: true,
        estimatedXp: 20,
        reason: 'valid_session'
    };
}

export function useQuiz(student, materialId, options = {}) {
    const {
        questions, gameState, currentQuestionIndex, score, streak, userAnswers,
        openEndedEvaluations, missedIndices, showFeedback, isEvaluating,
        setGameState, setIsEvaluating, initQuiz, recordAnswer, recordEvaluation, advanceQuestion
    } = useQuizEngine();

    const [loading, setLoading] = useState(false);
    const [errorMsg, setErrorMsg] = useState("");
    const [quizType, setQuizType] = useState(null);
    const [quizSessionToken, setQuizSessionToken] = useState(null);
    const [challengeSessionFeedback, setChallengeSessionFeedback] = useState({
        eligible: false,
        estimatedXp: 0,
        reason: null,
        activeSeconds: 0,
        totalQuestions: 0
    });

    const [sessionXP, setSessionXP] = useState(0);
    const timingRef = useRef({
        activeSeconds: 0,
        durationSeconds: 0,
        lastInputAt: 0,
        lastTickAt: 0,
        intervalId: null
    });
    const refreshRetryTimerRef = useRef(null);
    const isEvaluatingRef = useRef(false);
    const { refreshChallengeStatus } = options;

    const markActivity = useCallback(() => {
        timingRef.current.lastInputAt = Date.now();
    }, []);

    const resetTiming = useCallback(() => {
        const now = Date.now();
        timingRef.current.activeSeconds = 0;
        timingRef.current.durationSeconds = 0;
        timingRef.current.lastInputAt = now;
        timingRef.current.lastTickAt = now;
    }, []);

    const startTiming = useCallback(() => {
        if (timingRef.current.intervalId) return;
        resetTiming();

        const tick = () => {
            const now = Date.now();
            const lastTickAt = timingRef.current.lastTickAt || now;
            const deltaSeconds = Math.max(0, (now - lastTickAt) / 1000);
            timingRef.current.durationSeconds += deltaSeconds;

            const hasDocument = typeof document !== 'undefined';
            const isVisible = !hasDocument || document.visibilityState === 'visible';
            const hasFocus = !hasDocument || (typeof document.hasFocus === 'function' ? document.hasFocus() : true);
            const isActive = isVisible && hasFocus && (
                isEvaluatingRef.current || (now - timingRef.current.lastInputAt) <= IDLE_THRESHOLD_MS
            );

            if (isActive) {
                timingRef.current.activeSeconds += deltaSeconds;
            }
            timingRef.current.lastTickAt = now;
        };

        timingRef.current.intervalId = setInterval(tick, 1000);

        if (typeof window !== 'undefined') {
            window.addEventListener('mousemove', markActivity);
            window.addEventListener('mousedown', markActivity);
            window.addEventListener('keydown', markActivity);
            window.addEventListener('touchstart', markActivity);
            window.addEventListener('scroll', markActivity, { passive: true });
        }
    }, [markActivity, resetTiming]);

    const stopTiming = useCallback(() => {
        if (timingRef.current.intervalId) {
            clearInterval(timingRef.current.intervalId);
            timingRef.current.intervalId = null;
        }
        if (typeof window !== 'undefined') {
            window.removeEventListener('mousemove', markActivity);
            window.removeEventListener('mousedown', markActivity);
            window.removeEventListener('keydown', markActivity);
            window.removeEventListener('touchstart', markActivity);
            window.removeEventListener('scroll', markActivity);
        }
    }, [markActivity]);

    const getTimingSnapshot = useCallback(() => {
        const durationSeconds = Math.max(0, Math.round(timingRef.current.durationSeconds));
        const activeSeconds = Math.max(0, Math.round(Math.min(timingRef.current.activeSeconds, durationSeconds)));
        return { durationSeconds, activeSeconds };
    }, []);

    useEffect(() => {
        isEvaluatingRef.current = isEvaluating;
    }, [isEvaluating]);

    useEffect(() => {
        if (gameState === 'playing') {
            startTiming();
        } else {
            stopTiming();
        }
        return () => stopTiming();
    }, [gameState, startTiming, stopTiming]);

    useEffect(() => () => {
        if (refreshRetryTimerRef.current) {
            clearTimeout(refreshRetryTimerRef.current);
            refreshRetryTimerRef.current = null;
        }
    }, []);

    const triggerChallengeRefresh = useCallback(async () => {
        if (typeof refreshChallengeStatus !== 'function') return;
        try {
            await refreshChallengeStatus();
        } catch (err) {
            console.error('Failed to refresh challenge status', err);
        }
    }, [refreshChallengeStatus]);

    const scheduleChallengeRefreshRetry = useCallback(() => {
        if (typeof refreshChallengeStatus !== 'function') return;
        if (refreshRetryTimerRef.current) {
            clearTimeout(refreshRetryTimerRef.current);
        }
        refreshRetryTimerRef.current = setTimeout(() => {
            triggerChallengeRefresh();
            refreshRetryTimerRef.current = null;
        }, 600);
    }, [refreshChallengeStatus, triggerChallengeRefresh]);

    const startQuiz = async (type, topic) => {
        setLoading(true);
        setErrorMsg("");
        setQuizType(type);
        setQuizSessionToken(null);
        setSessionXP(0); // Reset session XP
        setChallengeSessionFeedback({
            eligible: false,
            estimatedXp: 0,
            reason: null,
            activeSeconds: 0,
            totalQuestions: 0
        });

        try {
            const payload = await studyService.generateQuiz(topic, type);
            const qs = Array.isArray(payload) ? payload : payload?.questions;
            const token = Array.isArray(payload) ? null : (payload?.quiz_session_token || null);
            if (!Array.isArray(qs) || qs.length === 0) {
                throw new Error("Não foi possível gerar perguntas para este tópico. Tenta 'Todos' ou outro tópico.");
            }
            setQuizSessionToken(token);
            initQuiz(qs);
        } catch (err) {
            console.error(err);
            const msg = err.response?.data?.detail || err.message || "Erro ao gerar o teste.";
            setErrorMsg(msg);
            setQuizType(null);
        } finally {
            setLoading(false);
        }
    };

    const handleAnswer = (qIndex, oIndex, addXPCallback) => {
        if (userAnswers[qIndex] !== undefined) return;

        const correct = questions[qIndex].correctIndex;
        const result = recordAnswer(qIndex, oIndex, oIndex === correct);

        let xp = 0;
        if (result === 'correct') {
            xp = 10;
        } else {
            xp = 2;
        }

        setSessionXP(prev => prev + xp);
        addXPCallback(xp);
    };

    const submitEvaluatedAnswer = async (userText, addXPCallback, evaluationType = 'open-ended') => {
        if (!userText.trim()) return;
        setIsEvaluating(true);
        const currentQ = questions[currentQuestionIndex];

        try {
            const rawEval = await studyService.evaluateAnswer(currentQ.question, userText, evaluationType);
            const evalData = {
                ...rawEval,
                is_correct: rawEval.score >= 50
            };
            recordEvaluation(currentQuestionIndex, evalData, userText);

            const xpEarned = calculateXPFromScore(evalData.score);
            setSessionXP(prev => prev + xpEarned);
            addXPCallback(xpEarned);
        } catch (err) {
            console.error(err);
            alert("Erro ao avaliar. Tenta novamente.");
        } finally {
            setIsEvaluating(false);
        }
    };

    const handleEvaluation = async (userText, addXPCallback) => {
        await submitEvaluatedAnswer(userText, addXPCallback, 'open-ended');
    };

    const handleShortAnswer = async (userText, addXPCallback) => {
        await submitEvaluatedAnswer(userText, addXPCallback, 'short_answer');
    };

    const nextQuestion = async (updateHighScoreCallback) => {
        const finished = advanceQuestion();

        if (finished) {
            const { detailedResults, errors } = buildDetailedResults({
                questions,
                userAnswers,
                openEndedEvaluations,
                quizType
            });

            if (errors.length > 0) {
                console.error('CRITICAL: Questions missing valid concepts.', errors);
                alert("Ocorreu um erro ao registar os conceitos das perguntas. Tenta gerar um novo teste.");
            }

            const submissionScore = quizType === 'multiple-choice'
                ? score
                : getOpenEndedAverage();

            // Optimistic Completion: Update UI immediately, send data in background.
            if (quizType === 'multiple-choice' && updateHighScoreCallback) {
                updateHighScoreCallback(score);
            }

            // Submit Analytics in background
            if (student?.id) {
                const { durationSeconds, activeSeconds } = getTimingSnapshot();
                const sessionFeedback = getChallengeSessionFeedback(
                    quizType,
                    questions.length,
                    detailedResults.length,
                    activeSeconds
                );
                setChallengeSessionFeedback(sessionFeedback);
                studyService.submitQuizResult(
                    submissionScore,
                    questions.length,
                    quizType,
                    detailedResults,
                    sessionXP,
                    materialId,
                    durationSeconds,
                    activeSeconds,
                    quizSessionToken
                )
                    .then(() => {
                        if (sessionFeedback.reason === 'valid_session') {
                            triggerChallengeRefresh();
                            scheduleChallengeRefreshRetry();
                        }
                    })
                    .catch(err => console.error("Failed to submit analytics", err));
            }
        }
    };

    const exitQuiz = () => {
        setGameState('intro');
    };

    const getOpenEndedAverage = () => {
        const evals = Object.values(openEndedEvaluations);
        if (evals.length === 0) return 0;
        const total = evals.reduce((acc, curr) => acc + curr.score, 0);
        return Math.round(total / evals.length);
    };

    const startReviewMode = () => {
        if (missedIndices.length === 0) return;
        const reviewQuestions = questions.filter((_, idx) => missedIndices.includes(idx));
        initQuiz(reviewQuestions);
    };

    return {
        questions, loading, errorMsg, setErrorMsg, quizType, gameState, setGameState,
        currentQuestionIndex, score, streak, userAnswers, openEndedEvaluations, isEvaluating, showFeedback,
        missedIndices, sessionXP, challengeSessionFeedback,
        startQuiz, handleAnswer, handleEvaluation, handleShortAnswer, nextQuestion, exitQuiz, getOpenEndedAverage, startReviewMode
    };
}
