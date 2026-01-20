import { useState } from 'react';
import { studyService } from '../services/api';

export function useQuiz(student) {
    const [questions, setQuestions] = useState([]);
    const [loading, setLoading] = useState(false);
    const [errorMsg, setErrorMsg] = useState("");
    const [quizType, setQuizType] = useState(null);
    const [gameState, setGameState] = useState('intro'); // 'intro', 'playing', 'results'
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [score, setScore] = useState(0);
    const [streak, setStreak] = useState(0);
    const [userAnswers, setUserAnswers] = useState({});
    const [openEndedEvaluations, setOpenEndedEvaluations] = useState({});
    const [missedIndices, setMissedIndices] = useState([]);
    const [isReviewMode, setIsReviewMode] = useState(false);

    // Evaluation state
    const [isEvaluating, setIsEvaluating] = useState(false);

    const startQuiz = async (type, topic) => {
        setLoading(true);
        setErrorMsg("");
        setQuizType(type);
        setQuestions([]);
        setUserAnswers({});
        setOpenEndedEvaluations({});
        setScore(0);
        setStreak(0);
        setCurrentQuestionIndex(0);

        try {
            const qs = await studyService.generateQuiz(topic, type);
            setQuestions(qs);
            setGameState('playing');
        } catch (err) {
            console.error(err);
            const msg = err.response?.data?.detail || "Erro ao gerar o teste.";
            setErrorMsg(msg);
            setQuizType(null);
        } finally {
            setLoading(false);
        }
    };

    // Feedback State
    const [showFeedback, setShowFeedback] = useState(false);

    const handleAnswer = (qIndex, oIndex, addXPCallback) => {
        if (userAnswers[qIndex] !== undefined) return;

        setUserAnswers(prev => ({ ...prev, [qIndex]: oIndex }));
        const correct = questions[qIndex].correctIndex;

        setShowFeedback(true); // Show immediate feedback

        if (oIndex === correct) {
            setScore(prev => prev + 1);
            setStreak(prev => prev + 1);
            addXPCallback(10);
            playSound('correct');
        } else {
            setStreak(0);
            addXPCallback(2); // Effort
            playSound('incorrect');

            // Track missed question for Review Mode (if not already in review?)
            // Actually, keep tracking mistakes even in review to loop them? 
            // For now, just track.
            setMissedIndices(prev => {
                if (!prev.includes(qIndex)) return [...prev, qIndex];
                return prev;
            });
        }
    };

    const playSound = (type) => {
        // Placeholder for sound logic if we add it later
        // const audio = new Audio(type === 'correct' ? '/sounds/correct.mp3' : '/sounds/wrong.mp3');
        // audio.play().catch(e => console.log("Audio play failed", e));
    };

    const handleEvaluation = async (userText, addXPCallback) => {
        if (!userText.trim()) return;
        setIsEvaluating(true);
        const currentQ = questions[currentQuestionIndex];

        try {
            const evalData = await studyService.evaluateAnswer(currentQ.question, userText);
            setOpenEndedEvaluations(prev => ({
                ...prev,
                [currentQuestionIndex]: { ...evalData, userText }
            }));

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
        setShowFeedback(false);
        if (currentQuestionIndex < questions.length - 1) {
            setCurrentQuestionIndex(prev => prev + 1);
        } else {
            // Quiz Finished

            // 1. Prepare Analytics Data
            const detailedResults = questions.map((q, idx) => {
                const ua = userAnswers[idx];
                const isCorrect = (ua !== undefined && ua === q.correctIndex);
                // For open ended, we might need different logic, but assuming multiple choice for now for auto-analytics
                // Open ended analytics is harder without "correct" boolean from AI immediately.
                // Let's focus analytics on Multiple Choice for now or use score > 50 as correct.

                let correct = isCorrect;
                if (quizType === 'open-ended') {
                    const evalData = openEndedEvaluations[idx];
                    correct = evalData && evalData.score >= 50;
                }

                return {
                    topic: q.topic || "Geral",
                    is_correct: correct
                };
            });

            // 2. Submit to Backend
            try {
                if (student?.id) {
                    await studyService.submitQuizResult(score, questions.length, quizType, detailedResults, student.id);
                }
            } catch (err) {
                console.error("Failed to submit analytics", err);
            }

            // 3. Update High Score (Local)
            if (quizType === 'multiple' && updateHighScoreCallback) {
                updateHighScoreCallback(score);
            }
            setGameState('results');
        }
    };

    const exitQuiz = () => {
        if (confirm("Tens a certeza que queres sair? Vais perder o progresso atual.")) {
            setGameState('intro');
            setQuestions([]);
        }
    };

    const getOpenEndedAverage = () => {
        const evals = Object.values(openEndedEvaluations);
        if (evals.length === 0) return 0;
        const total = evals.reduce((acc, curr) => acc + curr.score, 0);
        return Math.round(total / evals.length);
    };

    const startReviewMode = () => {
        if (missedIndices.length === 0) return;

        // Filter questions to only missed ones
        const reviewQuestions = questions.filter((_, idx) => missedIndices.includes(idx));

        setQuestions(reviewQuestions);
        setMissedIndices([]); // Reset for the review session
        setUserAnswers({});
        setScore(0);
        setStreak(0);
        setCurrentQuestionIndex(0);
        setIsReviewMode(true);
        setGameState('playing');
        setShowFeedback(false);
    };

    return {
        questions, loading, errorMsg, setErrorMsg, quizType, gameState, setGameState,
        currentQuestionIndex, score, streak, userAnswers, openEndedEvaluations, isEvaluating, showFeedback,
        missedIndices, isReviewMode,
        startQuiz, handleAnswer, handleEvaluation, nextQuestion, exitQuiz, getOpenEndedAverage, startReviewMode
    };
}
