import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import {
    BookOpen, CheckCircle, XCircle, RefreshCw, Award, BrainCircuit,
    ChevronRight, ArrowRight, Volume2, StopCircle, Play, Filter,
    AlertCircle, Star, PenTool, Send, MessageSquare, Flame, User, Trophy, Zap, Upload, FileText
} from 'lucide-react';
import Confetti from './Confetti';

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// --- Leveling System Config ---
const LEVELS = [
    { min: 0, title: "Estudante Curiosa", emoji: "🌱" },
    { min: 100, title: "Exploradora da Natureza", emoji: "🦋" },
    { min: 300, title: "Assistente de Laboratório", emoji: "🔬" },
    { min: 600, title: "Bióloga Júnior", emoji: "🧬" },
    { min: 1000, title: "Mestre das Ciências", emoji: "👩‍🔬" },
    { min: 2000, title: "Cientista Lendária", emoji: "🚀" },
];

const getLevelInfo = (xp) => {
    let level = LEVELS[0];
    let nextLevel = LEVELS[1];
    for (let i = 0; i < LEVELS.length; i++) {
        if (xp >= LEVELS[i].min) {
            level = LEVELS[i];
            nextLevel = LEVELS[i + 1] || null;
        }
    }
    return { level, nextLevel };
};

const cleanTextForSpeech = (text) => {
    return text
        .replace(/->/g, "dá origem a")
        .replace(/\*/g, "")
        .replace(/_/g, "");
};

// --- Sub-components ---

const QuestionCard = ({ question, index, total, onAnswer, userAnswer, onNext, handleSpeak, speakingPart }) => {
    const isAnswered = userAnswer !== null;

    return (
        <div className="w-full max-w-2xl mx-auto animate-fade-in">
            <div className="bg-white rounded-3xl shadow-xl p-8 border-b-8 border-indigo-100 relative overflow-hidden">
                <div className="absolute top-0 left-0 w-full h-2 bg-gray-100">
                    <div className="h-full bg-indigo-500 transition-all duration-500" style={{ width: `${((index + 1) / total) * 100}%` }}></div>
                </div>

                <div className="flex justify-between items-center mb-6 mt-2">
                    <span className="text-xs font-bold tracking-wider text-indigo-400 uppercase">Pergunta {index + 1} de {total}</span>
                    <span className="px-3 py-1 bg-indigo-50 text-indigo-600 rounded-full text-xs font-bold border border-indigo-100">
                        {question.topic || "Geral"}
                    </span>
                </div>

                <div className="flex items-start gap-4 mb-8">
                    <h2 className="text-2xl font-bold text-gray-800 leading-tight flex-1">{question.question}</h2>
                    <button
                        onClick={() => handleSpeak(question.question, 'question')}
                        aria-label={speakingPart === 'question' ? "Parar leitura da pergunta" : "Ler pergunta"}
                        className={`p-3 rounded-full transition-all duration-200 flex-shrink-0 shadow-sm ${speakingPart === 'question'
                            ? 'bg-blue-100 text-blue-600 ring-2 ring-blue-300'
                            : 'bg-gray-100 text-gray-500 hover:bg-blue-50 hover:text-blue-600'
                            }`}
                    >
                        {speakingPart === 'question' ? <StopCircle size={24} /> : <Volume2 size={24} />}
                    </button>
                </div>

                <div className="space-y-4">
                    {question.options.map((option, optIndex) => {
                        let btnClass = "w-full text-left p-5 rounded-xl border-2 transition-all duration-200 flex items-center justify-between group relative overflow-hidden ";
                        if (isAnswered) {
                            if (optIndex === question.correctIndex) btnClass += "bg-green-100 border-green-500 text-green-900 font-medium shadow-sm ring-1 ring-green-300";
                            else if (optIndex === userAnswer && userAnswer !== question.correctIndex) btnClass += "bg-red-50 border-red-300 text-red-800 opacity-90";
                            else btnClass += "bg-gray-50 border-gray-100 text-gray-400 opacity-60";
                        } else {
                            btnClass += "bg-white border-gray-200 hover:border-indigo-400 hover:bg-indigo-50 text-gray-700 hover:shadow-md cursor-pointer hover:scale-[1.01]";
                        }

                        return (
                            <button key={optIndex} onClick={() => !isAnswered && onAnswer(index, optIndex)} disabled={isAnswered} className={btnClass}>
                                <div className="flex items-center">
                                    <span className={`w-8 h-8 rounded-full flex items-center justify-center mr-4 text-sm font-bold shadow-sm transition-colors ${isAnswered && optIndex === question.correctIndex ? 'bg-green-500 text-white' :
                                        isAnswered && optIndex === userAnswer ? 'bg-red-500 text-white' :
                                            'bg-gray-100 text-gray-500 group-hover:bg-indigo-200 group-hover:text-indigo-700'
                                        }`}>
                                        {['A', 'B', 'C', 'D'][optIndex]}
                                    </span>
                                    {option}
                                </div>
                                {isAnswered && optIndex === question.correctIndex && <CheckCircle className="text-green-600" size={24} />}
                                {isAnswered && optIndex === userAnswer && userAnswer !== question.correctIndex && <XCircle className="text-red-500" size={24} />}
                            </button>
                        );
                    })}
                </div>

                {isAnswered && (
                    <div className="mt-8 animate-slide-up">
                        <div className={`p-5 rounded-xl border mb-6 shadow-sm ${userAnswer === question.correctIndex ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}`}>
                            <div className="flex items-start gap-3">
                                <BrainCircuit className={`mt-1 flex-shrink-0 ${userAnswer === question.correctIndex ? 'text-green-600' : 'text-red-500'}`} size={24} />
                                <div className="flex-1">
                                    <p className={`font-bold mb-2 ${userAnswer === question.correctIndex ? 'text-green-800' : 'text-red-800'}`}>
                                        {userAnswer === question.correctIndex ? 'Muito bem! 🎉' : 'Não foi desta... Vê a explicação: 👇'}
                                    </p>
                                    <div className="flex justify-between items-start">
                                        <p className="text-gray-700 text-sm leading-relaxed">{question.explanation}</p>
                                        <button
                                            onClick={() => handleSpeak(question.explanation, 'explanation')}
                                            aria-label={speakingPart === 'explanation' ? "Parar leitura da explicação" : "Ler explicação"}
                                            className={`p-2 rounded-full transition-all duration-200 flex-shrink-0 ml-2 ${speakingPart === 'explanation' ? 'bg-indigo-200 text-indigo-700' : 'bg-white/50 text-indigo-400 hover:text-indigo-600'
                                                }`}
                                        >
                                            {speakingPart === 'explanation' ? <StopCircle size={18} /> : <Volume2 size={18} />}
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div className="flex justify-end">
                            <button onClick={onNext} className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 px-8 rounded-full shadow-lg hover:shadow-xl transform transition hover:-translate-y-1 flex items-center text-lg">
                                {index < total - 1 ? 'Próxima' : 'Ver Nota'} <ArrowRight className="ml-2" size={20} />
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

const OpenEndedCard = ({ question, index, total, onEvaluate, evaluation, isEvaluating, evaluationError, onNext, handleSpeak, speakingPart }) => {
    const [userText, setUserText] = useState("");

    return (
        <div className="w-full max-w-2xl mx-auto animate-fade-in">
            <div className="bg-white rounded-3xl shadow-xl p-8 border-b-8 border-purple-100 relative overflow-hidden">
                <div className="absolute top-0 left-0 w-full h-2 bg-gray-100">
                    <div className="h-full bg-purple-500 transition-all duration-500" style={{ width: `${((index + 1) / total) * 100}%` }}></div>
                </div>

                <div className="flex justify-between items-center mb-6 mt-2">
                    <span className="text-xs font-bold tracking-wider text-purple-400 uppercase">Pergunta Objetiva {index + 1} de {total}</span>
                    <span className="px-3 py-1 bg-purple-50 text-purple-600 rounded-full text-xs font-bold border border-purple-100">
                        {question.topic || "Geral"}
                    </span>
                </div>

                <div className="flex items-start gap-4 mb-6">
                    <p className="text-gray-800 text-xl font-medium leading-relaxed flex-grow">{question.question}</p>
                    <button
                        onClick={() => handleSpeak(question.question, 'question')}
                        aria-label={speakingPart === 'question' ? "Parar leitura da pergunta" : "Ler pergunta"}
                        className={`p-3 rounded-full transition-all duration-200 flex-shrink-0 shadow-sm ${speakingPart === 'question'
                            ? 'bg-purple-100 text-purple-600 ring-2 ring-purple-300'
                            : 'bg-gray-100 text-gray-500 hover:bg-purple-50 hover:text-purple-600'
                            }`}
                    >
                        {speakingPart === 'question' ? <StopCircle size={24} /> : <Volume2 size={24} />}
                    </button>
                </div>

                {!evaluation ? (
                    <div className="space-y-4">
                        <textarea
                            className="w-full p-4 border-2 border-gray-200 rounded-xl focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition-all text-gray-700 min-h-[120px] resize-y"
                            placeholder="Escreve a tua resposta aqui..."
                            value={userText}
                            onChange={(e) => setUserText(e.target.value)}
                            disabled={isEvaluating}
                        />
                        <div className="flex justify-end items-center gap-4">
                            {evaluationError && (
                                <p className="text-red-500 text-sm font-bold flex items-center gap-1 animate-shake">
                                    <AlertCircle size={16} /> {evaluationError}
                                </p>
                            )}
                            <button
                                onClick={() => onEvaluate(userText)}
                                disabled={isEvaluating || userText.trim().length === 0}
                                className={`font-bold py-3 px-8 rounded-full shadow-lg flex items-center text-lg transition-all ${isEvaluating || userText.trim().length === 0 ? 'bg-gray-300 text-gray-500 cursor-not-allowed' : 'bg-purple-600 hover:bg-purple-700 text-white hover:shadow-xl hover:-translate-y-1'}`}
                            >
                                {isEvaluating ? (
                                    <>
                                        <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-white mr-2"></div>
                                        A corrigir...
                                    </>
                                ) : (
                                    <>
                                        Enviar Resposta <Send className="ml-2" size={20} />
                                    </>
                                )}
                            </button>
                        </div>
                    </div>
                ) : (
                    <div className="animate-slide-up">
                        <div className="bg-gray-50 p-4 rounded-lg mb-6 border border-gray-200">
                            <p className="text-gray-500 text-xs font-bold uppercase mb-1">A tua resposta:</p>
                            <p className="text-gray-700 italic">"{userText}"</p>
                        </div>

                        <div className={`p-5 rounded-xl border mb-6 shadow-sm ${evaluation.score >= 50 ? 'bg-green-50 border-green-200' : 'bg-orange-50 border-orange-200'}`}>
                            <div className="flex items-start gap-4">
                                <div className={`flex flex-col items-center justify-center p-3 rounded-full w-16 h-16 flex-shrink-0 ${evaluation.score >= 50 ? 'bg-green-100 text-green-700' : 'bg-orange-100 text-orange-700'}`}>
                                    <span className="text-xl font-black">{evaluation.score}</span>
                                    <span className="text-[10px] font-bold uppercase">Nota</span>
                                </div>
                                <div className="flex-grow">
                                    <div className="flex justify-between items-start">
                                        <p className="font-bold mb-2 text-gray-800">Avaliação da Professora:</p>
                                        <button
                                            onClick={() => handleSpeak(evaluation.feedback, 'feedback')}
                                            aria-label={speakingPart === 'feedback' ? "Parar leitura do feedback" : "Ler feedback"}
                                            className={`p-2 rounded-full transition-all duration-200 flex-shrink-0 ${speakingPart === 'feedback'
                                                ? 'bg-blue-200 text-blue-700 ring-2 ring-blue-400'
                                                : 'bg-white/50 text-blue-400 hover:bg-white hover:text-blue-600'
                                                }`}
                                        >
                                            {speakingPart === 'feedback' ? <StopCircle size={20} /> : <Volume2 size={20} />}
                                        </button>
                                    </div>
                                    <p className="text-gray-700 text-md leading-relaxed">{evaluation.feedback}</p>
                                </div>
                            </div>
                        </div>

                        <div className="flex justify-end">
                            <button onClick={onNext} className="bg-purple-600 hover:bg-purple-700 text-white font-bold py-3 px-8 rounded-full shadow-lg hover:shadow-xl transform transition hover:-translate-y-1 flex items-center text-lg">
                                {index < total - 1 ? 'Próxima' : 'Ver Nota'} <ArrowRight className="ml-2" size={20} />
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

const LoadingOverlay = () => (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex flex-col items-center justify-center animate-fade-in">
        <div className="bg-white p-8 rounded-3xl shadow-2xl flex flex-col items-center text-center max-w-sm mx-4">
            <div className="w-16 h-16 border-4 border-indigo-200 border-t-indigo-600 rounded-full animate-spin mb-6"></div>
            <h3 className="text-xl font-bold text-gray-800 mb-2">A preparar o teu Quiz...</h3>
            <p className="text-gray-500 text-sm">A nossa IA está a ler a matéria e a criar perguntas desafiantes! 🧠✨</p>
        </div>
    </div>
);


export default function App() {
    // --- States ---
    const [file, setFile] = useState(null);
    const [savedMaterial, setSavedMaterial] = useState(null);
    const [availableTopics, setAvailableTopics] = useState([]);
    const [selectedTopic, setSelectedTopic] = useState("all");
    const [isAnalyzing, setIsAnalyzing] = useState(false);

    // Quiz States
    const [questions, setQuestions] = useState([]);
    const [loading, setLoading] = useState(false);
    const [isEvaluating, setIsEvaluating] = useState(false);
    const [evaluationError, setEvaluationError] = useState("");
    const [errorMsg, setErrorMsg] = useState("");

    const [quizType, setQuizType] = useState(null); // 'multiple' | 'open-ended' | null
    const [gameState, setGameState] = useState('intro'); // 'intro', 'playing', 'results'
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [score, setScore] = useState(0);
    const [streak, setStreak] = useState(0);

    const [userAnswers, setUserAnswers] = useState({});
    const [openEndedEvaluations, setOpenEndedEvaluations] = useState({});

    // TTS
    const [speakingPart, setSpeakingPart] = useState(null);

    // Gamification Persisted
    const [highScore, setHighScore] = useState(0);
    const [totalXP, setTotalXP] = useState(0);
    const [selectedAvatar, setSelectedAvatar] = useState('👩‍🎓');

    useEffect(() => {
        checkSavedMaterial();
        const savedScore = localStorage.getItem('scienceQuizHighScore');
        if (savedScore) setHighScore(parseInt(savedScore, 10));

        const savedXP = localStorage.getItem('scienceQuizTotalXP');
        if (savedXP) setTotalXP(parseInt(savedXP, 10));

        const savedAvatar = localStorage.getItem('scienceQuizAvatar');
        if (savedAvatar) setSelectedAvatar(savedAvatar);
    }, []);

    // Stop TTS on unmount or question change
    useEffect(() => {
        window.speechSynthesis.cancel();
        setSpeakingPart(null);
        return () => window.speechSynthesis.cancel();
    }, [currentQuestionIndex, gameState]);

    const changeAvatar = (emoji) => {
        setSelectedAvatar(emoji);
        localStorage.setItem('scienceQuizAvatar', emoji);
    };

    const addXP = (amount) => {
        const newXP = totalXP + amount;
        setTotalXP(newXP);
        localStorage.setItem('scienceQuizTotalXP', newXP.toString());
    };

    const { level, nextLevel } = getLevelInfo(totalXP);

    const checkSavedMaterial = async () => {
        try {
            const res = await axios.get(`${API_URL}/current-material`);
            if (res.data.has_material) {
                setSavedMaterial(res.data);
                setAvailableTopics(res.data.topics || []);
            } else {
                setSavedMaterial(null);
            }
        } catch (err) {
            console.error(err);
        }
    };

    // --- Actions ---

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
    };

    const analyzeFile = async () => {
        if (!file) return;
        setIsAnalyzing(true);
        setErrorMsg('');

        const formData = new FormData();
        formData.append("file", file);

        try {
            await axios.post(`${API_URL}/upload`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            await checkSavedMaterial();
            setIsAnalyzing(false);
        } catch (err) {
            console.error(err);
            setErrorMsg("Falha ao analisar o ficheiro.");
            setIsAnalyzing(false);
        }
    };

    const detectTopics = async () => {
        setIsAnalyzing(true);
        setErrorMsg('');
        try {
            const res = await axios.post(`${API_URL}/analyze-topics`, {});
            setAvailableTopics(res.data.topics);
            await checkSavedMaterial();
            setIsAnalyzing(false);
        } catch (err) {
            console.error(err);
            const msg = err.response?.data?.detail || "Falha ao detetar tópicos.";
            setErrorMsg(msg);
            setIsAnalyzing(false);
        }
    };

    const clearMaterial = async () => {
        try {
            await axios.post(`${API_URL}/clear-material`);
            setSavedMaterial(null);
            setQuestions([]);
            setGameState('intro');
        } catch (err) {
            console.error(err);
        }
    };

    const startQuiz = async (type) => {
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
            const payload = {
                topics: selectedTopic === 'all' ? [] : [selectedTopic],
                quiz_type: type === 'open-ended' ? 'open-ended' : 'multiple'
            };

            const res = await axios.post(`${API_URL}/generate-quiz`, payload);
            setQuestions(res.data.questions);
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

    const handleMultipleChoiceAnswer = (qIndex, oIndex) => {
        setUserAnswers(prev => ({ ...prev, [qIndex]: oIndex }));
        const correct = questions[qIndex].correctIndex;
        if (oIndex === correct) {
            setScore(prev => prev + 1);
            setStreak(prev => prev + 1);
            addXP(10);
        } else {
            setStreak(0);
            addXP(2); // Effort
        }
    };

    const handleOpenEndedEvaluation = async (userText) => {
        if (!userText.trim()) return;
        setIsEvaluating(true);
        setEvaluationError("");
        const currentQ = questions[currentQuestionIndex];

        try {
            const res = await axios.post(`${API_URL}/evaluate-answer`, {
                question: currentQ.question,
                user_answer: userText
            });

            const evalData = res.data;
            setOpenEndedEvaluations(prev => ({
                ...prev,
                [currentQuestionIndex]: { ...evalData, userText }
            }));

            // XP Logic
            const xpEarned = 5 + (evalData.score >= 50 ? 5 : 0) + (evalData.score >= 80 ? 5 : 0);
            addXP(xpEarned);

        } catch (err) {
            console.error(err);
            setEvaluationError("Erro ao avaliar. Tenta novamente.");
        } finally {
            setIsEvaluating(false);
        }
    };

    const nextQuestion = () => {
        if (currentQuestionIndex < questions.length - 1) {
            setCurrentQuestionIndex(prev => prev + 1);
        } else {
            finishQuiz();
        }
    };

    const finishQuiz = () => {
        if (quizType === 'multiple') {
            if (score > highScore) {
                setHighScore(score);
                localStorage.setItem('scienceQuizHighScore', score.toString());
            }
        }
        setGameState('results');
    };

    const exitQuiz = () => {
        if (confirm("Tens a certeza que queres sair? Vais perder o progresso atual.")) {
            setGameState('intro');
            setQuestions([]);
        }
    };

    // TTS Helper
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

    const getOpenEndedAverage = () => {
        const evals = Object.values(openEndedEvaluations);
        if (evals.length === 0) return 0;
        const total = evals.reduce((acc, curr) => acc + curr.score, 0);
        return Math.round(total / evals.length);
    };

    // --- Renders ---



    // ... inside App component ...
    // 1. Loading State (Global)
    if (loading) {
        return <LoadingOverlay />;
    }

    // 2. Intro Screen (if not loading)
    if (gameState === 'intro') {
        return (
            <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-purple-100 p-6 font-sans text-gray-800">
                <div className="max-w-4xl mx-auto">
                    {/* Header Profile */}
                    <div className="flex justify-between items-center mb-8 bg-white p-4 rounded-2xl shadow-sm border border-indigo-50">
                        <div className="flex items-center gap-4">
                            <button onClick={() => changeAvatar(selectedAvatar === '👩‍🎓' ? '🧑‍🎓' : '👩‍🎓')} className="text-4xl bg-indigo-50 p-2 rounded-full border-2 border-indigo-100 hover:scale-110 transition-transform cursor-pointer">
                                {selectedAvatar}
                            </button>
                            <div>
                                <h1 className="text-xl font-bold text-gray-800 flex items-center gap-2">
                                    {level.emoji} {level.title}
                                </h1>
                                <div className="text-sm text-gray-500 font-medium flex items-center gap-2">
                                    <span className="text-indigo-600 font-bold">{totalXP} XP</span>
                                    <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
                                        <div className="h-full bg-indigo-500" style={{ width: nextLevel ? `${((totalXP - level.min) / (nextLevel.min - level.min)) * 100}%` : '100%' }}></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div className="bg-yellow-50 px-4 py-2 rounded-xl border border-yellow-200 flex items-center gap-2 text-yellow-700 font-bold">
                            <Trophy size={20} /> Recorde: {highScore}
                        </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-start">
                        {/* Left: Material */}
                        <div className="bg-white rounded-3xl shadow-xl p-8 border border-white/50 backdrop-blur-sm">
                            <div className="flex items-center mb-6">
                                <div className="bg-indigo-100 p-3 rounded-full mr-4 text-indigo-600">
                                    <BookOpen size={24} />
                                </div>
                                <h2 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-600 to-purple-600">Estudar</h2>
                            </div>

                            {!savedMaterial ? (
                                <>
                                    <div className="border-3 border-dashed border-indigo-200 rounded-2xl p-8 text-center hover:bg-indigo-50 transition-colors cursor-pointer group relative">
                                        <Upload className="mx-auto text-indigo-300 mb-4 group-hover:scale-110 transition-transform" size={48} />
                                        <p className="text-gray-500 font-medium mb-4">Carrega os teus apontamentos (PDF ou TXT)</p>
                                        <p className="text-xs text-indigo-400 font-bold">{file ? `Selecionado: ${file.name}` : "Clica ou arrasta para aqui"}</p>
                                        <input
                                            type="file"
                                            accept=".pdf,.txt"
                                            onChange={handleFileChange}
                                            aria-label="Carregar apontamentos (PDF ou TXT)"
                                            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                                        />
                                    </div>
                                    <div className="mt-4">
                                        <button
                                            onClick={analyzeFile}
                                            disabled={!file || isAnalyzing}
                                            className={`w-full px-6 py-4 rounded-xl font-bold shadow-md transition-all flex items-center justify-center gap-2 ${file ? 'bg-indigo-600 text-white hover:bg-indigo-700 hover:shadow-lg transform hover:-translate-y-1' : 'bg-gray-200 text-gray-400 cursor-not-allowed'
                                                }`}
                                        >
                                            {isAnalyzing ? (
                                                <>
                                                    <RefreshCw className="animate-spin" size={20} /> A Analisar...
                                                </>
                                            ) : (
                                                <>
                                                    Carregar e Analisar <ArrowRight size={20} />
                                                </>
                                            )}
                                        </button>
                                    </div>
                                </>
                            ) : (
                                <div>
                                    <div className="bg-indigo-50 rounded-xl p-4 mb-6 border border-indigo-100 flex items-center justify-between">
                                        <div className="flex items-center gap-3 overflow-hidden">
                                            <FileText className="text-indigo-500 flex-shrink-0" size={24} />
                                            <div className="min-w-0">
                                                <p className="font-bold text-gray-800 truncate">{savedMaterial.source}</p>
                                                <p className="text-xs text-indigo-600 font-medium">Material Pronto</p>
                                            </div>
                                        </div>
                                        <button
                                            onClick={clearMaterial}
                                            aria-label="Remover apontamentos"
                                            className="text-gray-400 hover:text-red-500 p-2"
                                        >
                                            <XCircle size={20} />
                                        </button>
                                    </div>

                                    {/* Topic Selection */}
                                    <div className="mb-6">
                                        <h3 className="font-bold text-gray-700 mb-3 flex items-center gap-2">
                                            <Filter size={18} /> Filtrar por Tópico
                                        </h3>
                                        {availableTopics.length > 0 ? (
                                            <select
                                                value={selectedTopic}
                                                onChange={(e) => setSelectedTopic(e.target.value)}
                                                aria-label="Filtrar por tópico"
                                                className="w-full p-3 rounded-xl border-2 border-gray-200 bg-white focus:border-indigo-500 focus:ring-4 focus:ring-indigo-100 transition-all font-medium text-gray-700"
                                            >
                                                <option value="all">📚 Todos os Tópicos</option>
                                                {availableTopics.map((t, i) => (
                                                    <option key={i} value={t}>{t}</option>
                                                ))}
                                            </select>
                                        ) : (
                                            <div className="text-center p-4 bg-yellow-50 rounded-xl border border-yellow-100">
                                                <p className="text-sm text-yellow-700 font-medium mb-2">Sem tópicos detetados.</p>
                                                <button
                                                    onClick={detectTopics}
                                                    disabled={isAnalyzing}
                                                    className="text-xs bg-yellow-100 hover:bg-yellow-200 text-yellow-800 px-3 py-1 rounded-full font-bold transition-colors"
                                                >
                                                    Identificar Tópicos
                                                </button>
                                            </div>
                                        )}
                                    </div>

                                    {errorMsg && (
                                        <div className="bg-red-50 text-red-600 p-3 rounded-xl text-sm font-medium mb-4 flex items-center gap-2">
                                            <AlertCircle size={16} /> {errorMsg}
                                        </div>
                                    )}

                                    {/* Action Buttons */}
                                    <div className="grid grid-cols-2 gap-4">
                                        <button
                                            onClick={() => startQuiz('multiple')}
                                            disabled={loading}
                                            className="bg-gradient-to-r from-blue-500 to-indigo-600 text-white p-4 rounded-xl shadow-lg hover:shadow-xl hover:-translate-y-1 transition-all group text-left relative overflow-hidden"
                                        >
                                            <div className="relative z-10">
                                                <p className="text-xs font-bold uppercase opacity-80 mb-1">Modo Clássico</p>
                                                <h3 className="text-lg font-bold flex items-center">
                                                    Escolha Múltipla <ChevronRight className="ml-auto opacity-0 group-hover:opacity-100 transition-opacity" />
                                                </h3>
                                            </div>
                                        </button>

                                        <button
                                            onClick={() => startQuiz('open-ended')}
                                            disabled={loading}
                                            className="bg-gradient-to-r from-purple-500 to-pink-600 text-white p-4 rounded-xl shadow-lg hover:shadow-xl hover:-translate-y-1 transition-all group text-left relative overflow-hidden"
                                        >
                                            <div className="relative z-10">
                                                <p className="text-xs font-bold uppercase opacity-80 mb-1">Modo Escrita</p>
                                                <h3 className="text-lg font-bold flex items-center">
                                                    Resposta Aberta <PenTool size={16} className="ml-2" />
                                                </h3>
                                            </div>
                                        </button>
                                    </div>
                                    {loading && <p className="text-center text-indigo-600 font-bold mt-4 animate-pulse">A preparar o teste... 🤖</p>}
                                </div>
                            )}
                        </div>

                        {/* Right: Stats/Info */}
                        <div className="space-y-6">
                            <div className="bg-gradient-to-br from-indigo-600 to-purple-700 rounded-3xl p-8 text-white shadow-xl relative overflow-hidden">
                                <div className="absolute top-0 right-0 p-32 bg-white opacity-5 rounded-full blur-3xl transform translate-x-10 -translate-y-10"></div>
                                <h3 className="text-xl font-bold mb-4 opacity-90">Progresso Atual</h3>
                                <div className="grid grid-cols-2 gap-4">
                                    <div className="bg-white/10 rounded-2xl p-4 backdrop-blur-sm">
                                        <p className="text-2xl font-black">{totalXP}</p>
                                        <p className="text-xs font-medium uppercase opacity-70">XP Total</p>
                                    </div>
                                    <div className="bg-white/10 rounded-2xl p-4 backdrop-blur-sm">
                                        <p className="text-2xl font-black">{LEVELS.indexOf(level) + 1}</p>
                                        <p className="text-xs font-medium uppercase opacity-70">Nível</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    // 3. Playing State
    if (gameState === 'playing') {
        const currentQ = questions[currentQuestionIndex];
        return (
            <div className="min-h-screen bg-gray-50 p-6 flex flex-col font-sans">
                <div className="max-w-4xl mx-auto w-full flex justify-between items-center mb-6">
                    <button
                        onClick={exitQuiz}
                        aria-label="Sair do Quiz"
                        className="flex items-center gap-2 text-gray-500 hover:text-red-600 transition-colors font-bold bg-white px-4 py-2 rounded-full shadow-sm hover:shadow-md"
                    >
                        <XCircle size={24} /> Sair
                    </button>
                    <div className="flex items-center gap-2 bg-white px-4 py-2 rounded-full shadow-sm text-indigo-600 font-bold border border-indigo-50">
                        <Flame size={20} className={streak > 2 ? "text-orange-500 animate-pulse" : "text-gray-300"} />
                        <span>{streak}</span>
                    </div>
                </div>

                {quizType === 'multiple' ? (
                    <QuestionCard
                        question={currentQ}
                        index={currentQuestionIndex}
                        total={questions.length}
                        onAnswer={handleMultipleChoiceAnswer}
                        userAnswer={userAnswers[currentQuestionIndex] ?? null}
                        onNext={nextQuestion}
                        handleSpeak={handleSpeak}
                        speakingPart={speakingPart}
                    />
                ) : (
                    <OpenEndedCard
                        question={currentQ}
                        index={currentQuestionIndex}
                        total={questions.length}
                        onEvaluate={handleOpenEndedEvaluation}
                        evaluation={openEndedEvaluations[currentQuestionIndex]}
                        isEvaluating={isEvaluating}
                        evaluationError={evaluationError}
                        onNext={nextQuestion}
                        handleSpeak={handleSpeak}
                        speakingPart={speakingPart}
                    />
                )}
            </div>
        );
    }

    // 4. Results State
    if (gameState === 'results') {
        const isWin = score > 0; // Encouraging win condition
        return (
            <div className="min-h-screen bg-gradient-to-br from-indigo-600 to-purple-700 flex items-center justify-center p-6 relative overflow-hidden font-sans">
                {isWin && <Confetti />}
                <div className="bg-white rounded-3xl shadow-2xl p-8 max-w-lg w-full text-center relative z-10 animate-fade-in">
                    <div className="absolute -top-12 left-1/2 transform -translate-x-1/2 bg-yellow-400 p-4 rounded-full border-4 border-white shadow-xl">
                        <Trophy size={48} className="text-white" />
                    </div>

                    <h2 className="text-3xl font-black text-gray-800 mt-8 mb-2">
                        {quizType === 'multiple' ? 'Quiz Concluído!' : 'Treino Terminado!'}
                    </h2>
                    <p className="text-gray-500 mb-8">Fantástico esforço! 🌟</p>

                    <div className="grid grid-cols-2 gap-4 mb-8">
                        <div className="bg-indigo-50 p-4 rounded-2xl border border-indigo-100">
                            <p className="text-3xl font-black text-indigo-600">{score}</p>
                            <p className="text-xs font-bold uppercase text-indigo-400">Pontos</p>
                        </div>
                        <div className="bg-purple-50 p-4 rounded-2xl border border-purple-100">
                            <p className="text-3xl font-black text-purple-600">+{score * 5} XP</p>
                            <p className="text-xs font-bold uppercase text-purple-400">Ganhos</p>
                        </div>
                    </div>

                    <button
                        onClick={() => setGameState('intro')}
                        className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-4 rounded-xl shadow-lg hover:shadow-xl transform transition hover:-translate-y-1 flex items-center justify-center gap-2"
                    >
                        <RefreshCw size={20} /> Voltar ao Início
                    </button>
                </div>
            </div>
        );
    }

    return null;
}
