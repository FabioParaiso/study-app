import React from 'react';
import { useGamification } from './hooks/useGamification';
import { useQuiz } from './hooks/useQuiz';
import { useStudent } from './hooks/useStudent';
import { useMaterial } from './hooks/useMaterial';
import { useTTS } from './hooks/useTTS';

import IntroPage from './pages/IntroPage';
import ResultsPage from './pages/ResultsPage';
import LoadingOverlay from './components/LoadingOverlay';
import LoginPage from './pages/LoginPage';
import QuizPage from './pages/QuizPage';

export default function App() {
    // --- Custom Hooks (SRP) ---
    const { student, setStudent, logout } = useStudent();

    const {
        file, savedMaterial, availableTopics, selectedTopic, isAnalyzing, errorMsg,
        setSelectedTopic, handleFileChange, analyzeFile, detectTopics, clearMaterial,
        materialsList, activateMaterial, refreshMaterial
    } = useMaterial(student?.id);

    const {
        highScore, totalXP, selectedAvatar, changeAvatar, addXP, updateHighScore, level, nextLevel, LEVELS
    } = useGamification(student, savedMaterial);

    const {
        questions, loading, errorMsg: quizError, quizType, gameState, setGameState,
        currentQuestionIndex, score, streak, userAnswers, openEndedEvaluations, isEvaluating,
        startQuiz, handleAnswer, handleEvaluation, handleShortAnswer, nextQuestion, exitQuiz, getOpenEndedAverage,
        showFeedback, missedIndices, startReviewMode, sessionXP
    } = useQuiz(student, savedMaterial?.id);

    const { speakingPart, handleSpeak } = useTTS();

    const handleLogout = () => {
        logout();
        setGameState('intro');
    };

    const handleStart = (type) => startQuiz(type, selectedTopic);

    // --- Render ---

    if (loading) return <LoadingOverlay />;

    if (!student) {
        return <LoginPage onLogin={setStudent} />;
    }

    if (gameState === 'intro') {
        return (
            <IntroPage
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
                materialsList={materialsList}
                activateMaterial={activateMaterial}
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
                onShortAnswer={handleShortAnswer}
                onNext={() => nextQuestion(updateHighScore)}
                onExit={exitQuiz}
                handleSpeak={handleSpeak}
                speakingPart={speakingPart}
                showFeedback={showFeedback}
                addXP={addXP}
                streak={streak}
            />
        );
    }

    if (gameState === 'results') {
        return (
            <ResultsPage
                score={score}
                totalQuestions={questions.length}
                xpEarned={sessionXP}
                streak={streak}
                quizType={quizType}
                getOpenEndedAverage={getOpenEndedAverage}
                exitQuiz={() => { refreshMaterial(); exitQuiz(); }}
                onRestart={() => startQuiz(quizType, selectedTopic)}
                numMissed={missedIndices ? missedIndices.length : 0}
                onReview={startReviewMode}
            />
        );
    }

    return null;
}
