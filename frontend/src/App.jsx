import React from 'react';
import { useGamification } from './hooks/useGamification';
import { useQuiz } from './hooks/useQuiz';
import { useStudent } from './hooks/useStudent';
import { useMaterial } from './hooks/useMaterial';
import { useTTS } from './hooks/useTTS';

import IntroScreen from './components/IntroScreen';
import ResultsScreen from './components/ResultsScreen';
import LoadingOverlay from './components/LoadingOverlay';
import StudentLogin from './components/StudentLogin';
import QuizPage from './components/Quiz/QuizPage';

export default function App() {
    // --- Custom Hooks (SRP) ---
    const { student, setStudent, logout } = useStudent();

    const {
        file, savedMaterial, availableTopics, selectedTopic, isAnalyzing, errorMsg,
        setSelectedTopic, handleFileChange, analyzeFile, detectTopics, clearMaterial
    } = useMaterial(student?.id);

    const {
        highScore, totalXP, selectedAvatar, changeAvatar, addXP, updateHighScore, level, nextLevel, LEVELS
    } = useGamification();

    const {
        questions, loading, errorMsg: quizError, quizType, gameState, setGameState,
        currentQuestionIndex, score, streak, userAnswers, openEndedEvaluations, isEvaluating,
        startQuiz, handleAnswer, handleEvaluation, nextQuestion, exitQuiz, getOpenEndedAverage,
        showFeedback, missedIndices, startReviewMode
    } = useQuiz(student);

    const { speakingPart, handleSpeak } = useTTS();

    const handleLogout = () => {
        logout();
        setGameState('intro');
    };

    const handleStart = (type) => startQuiz(type, selectedTopic);

    // --- Render ---

    if (loading) return <LoadingOverlay />;

    if (!student) {
        return <StudentLogin onLogin={setStudent} />;
    }

    if (gameState === 'intro') {
        return (
            <IntroScreen
                student={student}
                onLogout={handleLogout}
                file={file}
                handleFileChange={handleFileChange}
                analyzeFile={analyzeFile}
                isAnalyzing={isAnalyzing}
                savedMaterial={savedMaterial}
                clearMaterial={clearMaterial}
                availableTopics={availableTopics}
                selectedTopic={selectedTopic}
                setSelectedTopic={setSelectedTopic}
                detectTopics={detectTopics}
                errorMsg={errorMsg || quizError}
                loading={loading}
                startQuiz={handleStart}
                changeAvatar={changeAvatar}
                selectedAvatar={selectedAvatar}
                level={level}
                totalXP={totalXP}
                highScore={highScore}
                nextLevel={nextLevel}
                LEVELS={LEVELS}
            />
        );
    }

    if (gameState === 'playing') {
        return (
            <QuizPage
                questions={questions}
                currentQuestionIndex={currentQuestionIndex}
                quizType={quizType}
                userAnswers={userAnswers}
                openEndedEvaluations={openEndedEvaluations}
                isEvaluating={isEvaluating}
                onAnswer={handleAnswer}
                onEvaluate={handleEvaluation}
                onNext={() => nextQuestion(updateHighScore)}
                onExit={exitQuiz}
                handleSpeak={handleSpeak}
                speakingPart={speakingPart}
                showFeedback={showFeedback}
                addXP={addXP}
            />
        );
    }

    if (gameState === 'results') {
        return (
            <ResultsScreen
                score={score}
                totalQuestions={questions.length}
                xpEarned={0}
                streak={streak}
                quizType={quizType}
                getOpenEndedAverage={getOpenEndedAverage}
                exitQuiz={exitQuiz}
                onRestart={() => startQuiz(quizType, selectedTopic)}
                numMissed={missedIndices ? missedIndices.length : 0}
                onReview={startReviewMode}
            />
        );
    }

    return null;
}
