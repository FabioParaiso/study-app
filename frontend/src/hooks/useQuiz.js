import { useState } from 'react';
import { studyService } from '../services/studyService';
import { useQuizEngine } from './useQuizEngine';
import { calculateXPFromScore } from '../utils/xpCalculator';
import { buildDetailedResults } from '../utils/quizAnalytics';

export function useQuiz(student, materialId) {
    const {
        questions, gameState, currentQuestionIndex, score, streak, userAnswers,
        openEndedEvaluations, missedIndices, showFeedback, isEvaluating,
        setGameState, setIsEvaluating, initQuiz, recordAnswer, recordEvaluation, advanceQuestion,
        setQuestions
    } = useQuizEngine();

    const [loading, setLoading] = useState(false);
    const [errorMsg, setErrorMsg] = useState("");
    const [quizType, setQuizType] = useState(null);

    const [sessionXP, setSessionXP] = useState(0);

    const startQuiz = async (type, topic) => {
        setLoading(true);
        setErrorMsg("");
        setQuizType(type);
        setSessionXP(0); // Reset session XP

        try {
            const qs = await studyService.generateQuiz(topic, type);
            initQuiz(qs);
        } catch (err) {
            console.error(err);
            const msg = err.response?.data?.detail || "Erro ao gerar o teste.";
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

    const handleEvaluation = async (userText, addXPCallback) => {
        if (!userText.trim()) return;
        setIsEvaluating(true);
        const currentQ = questions[currentQuestionIndex];

        try {
            const evalData = await studyService.evaluateAnswer(currentQ.question, userText);
            recordEvaluation(currentQuestionIndex, evalData, userText);

            // XP Logic (centralized in utils/xpCalculator.js)
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

    /**
     * Handler for Short Answer mode - uses AI evaluation for simple sentences.
     */
    const handleShortAnswer = async (userText, addXPCallback) => {
        if (!userText.trim()) return;
        setIsEvaluating(true);
        const currentQ = questions[currentQuestionIndex];

        try {
            // Pass 'short_answer' as type to trigger the simple sentence prompt on backend
            const rawEval = await studyService.evaluateAnswer(currentQ.question, userText, 'short_answer');

            const evalData = {
                ...rawEval,
                is_correct: rawEval.score >= 50
            };

            recordEvaluation(currentQuestionIndex, evalData, userText);

            // XP Logic (centralized in utils/xpCalculator.js)
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
                return;
            }

            // Optimistic Completion: Update UI immediately, send data in background.
            if (quizType === 'multiple-choice' && updateHighScoreCallback) {
                updateHighScoreCallback(score);
            }

            // Submit Analytics in background
            if (student?.id) {
                studyService.submitQuizResult(
                    score,
                    questions.length,
                    quizType,
                    detailedResults,
                    sessionXP,
                    materialId
                ).catch(err => console.error("Failed to submit analytics", err));
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
        missedIndices, sessionXP,
        startQuiz, handleAnswer, handleEvaluation, handleShortAnswer, nextQuestion, exitQuiz, getOpenEndedAverage, startReviewMode
    };
}
