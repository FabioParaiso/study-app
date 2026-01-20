import React, { useState, useEffect } from 'react';
import { useGamification } from './hooks/useGamification';
import { useQuiz } from './hooks/useQuiz';
import { studyService } from './services/api';
import IntroScreen from './components/IntroScreen';
import QuestionCard from './components/QuestionCard';
import OpenEndedCard from './components/OpenEndedCard';
import ResultsScreen from './components/ResultsScreen';
import LoadingOverlay from './components/LoadingOverlay';
import StudentLogin from './components/StudentLogin';
import { X } from 'lucide-react';

// Helper for TTS
const cleanTextForSpeech = (text) => {
    return text
        .replace(/->/g, "dá origem a")
        .replace(/\*/g, "")
        .replace(/_/g, "");
};

export default function App() {
    // --- User State ---
    const [student, setStudent] = useState(() => {
        const saved = localStorage.getItem('study_student');
        return saved ? JSON.parse(saved) : null;
    });

    useEffect(() => {
        if (student) {
            localStorage.setItem('study_student', JSON.stringify(student));
        } else {
            localStorage.removeItem('study_student');
        }
    }, [student]);

    // --- Hooks ---
    const {
        highScore, totalXP, selectedAvatar, changeAvatar, addXP, updateHighScore, level, nextLevel, LEVELS
    } = useGamification();

    const {
        questions, loading, errorMsg, setErrorMsg, quizType, gameState, setGameState,
        currentQuestionIndex, score, streak, userAnswers, openEndedEvaluations, isEvaluating,
        startQuiz, handleAnswer, handleEvaluation, nextQuestion, exitQuiz, getOpenEndedAverage,
        showFeedback, missedIndices, startReviewMode
    } = useQuiz(student);

    // --- Local UI State (Intro Logic) ---
    const [file, setFile] = useState(null);
    const [savedMaterial, setSavedMaterial] = useState(null);
    const [availableTopics, setAvailableTopics] = useState([]);
    const [selectedTopic, setSelectedTopic] = useState("all");
    const [isAnalyzing, setIsAnalyzing] = useState(false);

    // TTS State
    const [speakingPart, setSpeakingPart] = useState(null);

    // --- Effects ---
    useEffect(() => {
        if (student) {
            checkSavedMaterial();
        } else {
            setSavedMaterial(null);
            setAvailableTopics([]);
        }
    }, [student]);

    useEffect(() => {
        window.speechSynthesis.cancel();
        setSpeakingPart(null);
        return () => window.speechSynthesis.cancel();
    }, [currentQuestionIndex, gameState]);

    // --- Setup Facade ---
    const checkSavedMaterial = async () => {
        if (!student) return;
        try {
            const data = await studyService.checkMaterial(student.id);
            if (data.has_material) {
                setSavedMaterial(data);
                setAvailableTopics(data.topics || []);
            } else {
                setSavedMaterial(null);
            }
        } catch (err) {
            console.error(err);
        }
    };

    const handleFileChange = (e) => setFile(e.target.files[0]);

    const analyzeFile = async () => {
        if (!file) return;
        setIsAnalyzing(true);
        setErrorMsg('');
        try {
            await studyService.uploadFile(file, student.id);
            await checkSavedMaterial();
        } catch (err) {
            console.error(err);
            setErrorMsg("Falha ao analisar o ficheiro.");
        } finally {
            setIsAnalyzing(false);
        }
    };

    const detectTopics = async () => {
        setIsAnalyzing(true);
        setErrorMsg('');
        try {
            const data = await studyService.analyzeTopics(student.id);
            setAvailableTopics(data.topics);
            await checkSavedMaterial();
        } catch (err) {
            console.error(err);
            setErrorMsg("Falha ao detetar tópicos.");
        } finally {
            setIsAnalyzing(false);
        }
    };

    const clearMaterial = async () => {
        if (!student) return;
        try {
            await studyService.clearMaterial(student.id);
            setSavedMaterial(null);
            setGameState('intro');
        } catch (err) {
            console.error(err);
        }
    };

    const handleStart = (type) => startQuiz(type, selectedTopic);

    const handleSpeak = (text, part) => {
        if (speakingPart === part) {
            window.speechSynthesis.cancel();
            setSpeakingPart(null);
            return;
        }
        window.speechSynthesis.cancel();
        const cleanText = cleanTextForSpeech(text);
        const utterance = new SpeechSynthesisUtterance(cleanText);
        utterance.lang = 'pt-PT';
        setSpeakingPart(part);
        utterance.onend = () => setSpeakingPart(null);
        window.speechSynthesis.speak(utterance);
    };

    const handleLogout = () => {
        setStudent(null);
        setGameState('intro');
    };

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
                errorMsg={errorMsg}
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
        const currentQ = questions[currentQuestionIndex];

        return (
            <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-6 relative">
                {/* Header for Quiz Mode */}
                <div className="absolute top-0 left-0 w-full p-6 flex justify-between items-center z-50">
                    <button
                        onClick={() => {
                            if (window.confirm("Tens a certeza que queres sair? Vais perder o progresso atual.")) {
                                exitQuiz();
                            }
                        }}
                        className="p-3 rounded-2xl bg-white border-b-4 border-gray-200 text-gray-400 hover:bg-gray-50 hover:text-red-500 hover:border-red-200 transition-all active:border-b-0 active:translate-y-1"
                        aria-label="Sair"
                    >
                        <X size={24} strokeWidth={3} />
                    </button>

                    {/* Progress Bar Placeholder could go here if we wanted to move it out of cards */}
                </div>

                {quizType === 'multiple' ? (
                    <QuestionCard
                        key={currentQuestionIndex}
                        question={currentQ}
                        index={currentQuestionIndex}
                        total={questions.length}
                        onAnswer={(qId, oId) => handleAnswer(qId, oId, addXP)}
                        userAnswer={userAnswers[currentQuestionIndex] !== undefined ? userAnswers[currentQuestionIndex] : null}
                        onNext={() => nextQuestion(updateHighScore)}
                        handleSpeak={handleSpeak}
                        speakingPart={speakingPart}
                        showFeedback={showFeedback}
                    />
                ) : (
                    <OpenEndedCard
                        key={currentQuestionIndex}
                        question={currentQ}
                        index={currentQuestionIndex}
                        total={questions.length}
                        onEvaluate={(text) => handleEvaluation(text, addXP)}
                        evaluation={openEndedEvaluations[currentQuestionIndex]}
                        isEvaluating={isEvaluating}
                        onNext={() => nextQuestion(updateHighScore)}
                        handleSpeak={handleSpeak}
                        speakingPart={speakingPart}
                    />
                )}
            </div>
        );
    }

    const handleRestart = () => startQuiz(quizType, selectedTopic);

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
                onRestart={handleRestart}
                numMissed={missedIndices ? missedIndices.length : 0}
                onReview={startReviewMode}
            />
        );
    }

    return null;
}
