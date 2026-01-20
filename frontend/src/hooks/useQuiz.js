import { useState } from 'react';
import { studyService } from '../services/studyService';
import { useQuizEngine } from './useQuizEngine';

export function useQuiz(student) {
    const {
        questions, gameState, currentQuestionIndex, score, streak, userAnswers,
        openEndedEvaluations, missedIndices, showFeedback, isEvaluating,
        setGameState, setIsEvaluating, initQuiz, recordAnswer, recordEvaluation, advanceQuestion,
        setQuestions
    } = useQuizEngine();

    const [loading, setLoading] = useState(false);
    const [errorMsg, setErrorMsg] = useState("");
    const [quizType, setQuizType] = useState(null);

    const startQuiz = async (type, topic) => {
        setLoading(true);
        setErrorMsg("");
        setQuizType(type);

        try {
            const qs = await studyService.generateQuiz(topic, type, student?.id);
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

        if (result === 'correct') {
            addXPCallback(10);
        } else {
            addXPCallback(2);
        }
    };

    const handleEvaluation = async (userText, addXPCallback) => {
        if (!userText.trim()) return;
        setIsEvaluating(true);
        const currentQ = questions[currentQuestionIndex];

        try {
            const evalData = await studyService.evaluateAnswer(currentQ.question, userText, student?.id);
            recordEvaluation(currentQuestionIndex, evalData, userText);

            // XP Logic
            const xpEarned = 5 + (evalData.score >= 50 ? 5 : 0) + (evalData.score >= 80 ? 5 : 0);
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
            // Submit Analytics
            const detailedResults = questions.map((q, idx) => {
                const ua = userAnswers[idx];
                let correct = false;

                if (quizType === 'multiple') {
                    correct = (ua !== undefined && ua === q.correctIndex);
                } else {
                    const evalData = openEndedEvaluations[idx];
                    correct = evalData && evalData.score >= 50;
                }

                return {
                    topic: q.topic || "Geral",
                    is_correct: correct
                };
            });

            try {
                if (student?.id) {
                    await studyService.submitQuizResult(score, questions.length, quizType, detailedResults, student.id);
                }
            } catch (err) {
                console.error("Failed to submit analytics", err);
            }

            if (quizType === 'multiple' && updateHighScoreCallback) {
                updateHighScoreCallback(score);
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
        missedIndices,
        startQuiz, handleAnswer, handleEvaluation, nextQuestion, exitQuiz, getOpenEndedAverage, startReviewMode
    };
}
