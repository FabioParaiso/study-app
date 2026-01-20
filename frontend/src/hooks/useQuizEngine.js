import { useState, useCallback } from 'react';

export const useQuizEngine = (initialQuestions = []) => {
    const [questions, setQuestions] = useState(initialQuestions);
    const [gameState, setGameState] = useState('intro'); // 'intro', 'playing', 'results'
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [score, setScore] = useState(0);
    const [streak, setStreak] = useState(0);
    const [userAnswers, setUserAnswers] = useState({});
    const [openEndedEvaluations, setOpenEndedEvaluations] = useState({});
    const [missedIndices, setMissedIndices] = useState([]);
    const [showFeedback, setShowFeedback] = useState(false);
    const [isEvaluating, setIsEvaluating] = useState(false);

    const resetGame = useCallback(() => {
        setScore(0);
        setStreak(0);
        setCurrentQuestionIndex(0);
        setUserAnswers({});
        setOpenEndedEvaluations({});
        setShowFeedback(false);
        setMissedIndices([]);
    }, []);

    const initQuiz = useCallback((newQuestions) => {
        setQuestions(newQuestions);
        resetGame();
        setGameState('playing');
    }, [resetGame]);

    const recordAnswer = useCallback((qIndex, oIndex, isCorrect) => {
        setUserAnswers(prev => ({ ...prev, [qIndex]: oIndex }));
        setShowFeedback(true);

        if (isCorrect) {
            setScore(prev => prev + 1);
            setStreak(prev => prev + 1);
            return 'correct';
        } else {
            setStreak(0);
            setMissedIndices(prev => {
                if (!prev.includes(qIndex)) return [...prev, qIndex];
                return prev;
            });
            return 'incorrect';
        }
    }, []);

    const recordEvaluation = useCallback((qIndex, evalData, userText) => {
        setOpenEndedEvaluations(prev => ({
            ...prev,
            [qIndex]: { ...evalData, userText }
        }));
    }, []);

    const advanceQuestion = useCallback(() => {
        setShowFeedback(false);
        if (currentQuestionIndex < questions.length - 1) {
            setCurrentQuestionIndex(prev => prev + 1);
            return false; // Not finished
        } else {
            setGameState('results');
            return true; // Finished
        }
    }, [currentQuestionIndex, questions.length]);

    return {
        questions,
        gameState,
        currentQuestionIndex,
        score,
        streak,
        userAnswers,
        openEndedEvaluations,
        missedIndices,
        showFeedback,
        isEvaluating,
        setGameState,
        setIsEvaluating,
        initQuiz,
        recordAnswer,
        recordEvaluation,
        advanceQuestion,
        setQuestions // Exposed for review mode
    };
};
