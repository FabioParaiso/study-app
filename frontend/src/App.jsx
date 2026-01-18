import React, { useState, useEffect } from 'react';
import { BookOpen, CheckCircle, XCircle, Brain, Sparkles, ArrowRight, RefreshCw, Trophy, Upload, FileText, Trash2, List, LogOut, ChevronDown, Search } from 'lucide-react';
import axios from 'axios';

// Backend URL
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export default function App() {
    const [gameState, setGameState] = useState('intro'); // intro, loading, playing, results, error
    const [questions, setQuestions] = useState([]);
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [score, setScore] = useState(0);
    const [selectedOption, setSelectedOption] = useState(null);
    const [showExplanation, setShowExplanation] = useState(false);
    const [errorMsg, setErrorMsg] = useState('');
    const [apiKey, setApiKey] = useState('');
    const [file, setFile] = useState(null);

    // Persistence & Topics state
    const [savedMaterial, setSavedMaterial] = useState(null);
    const [availableTopics, setAvailableTopics] = useState([]);
    const [selectedTopics, setSelectedTopics] = useState([]); // Array, but we might stick to single + all logic
    const [isAnalyzing, setIsAnalyzing] = useState(false);

    useEffect(() => {
        checkSavedMaterial();
    }, []);

    const checkSavedMaterial = async () => {
        try {
            const res = await axios.get(`${API_URL}/current-material`);
            if (res.data.has_material) {
                setSavedMaterial(res.data);
                setAvailableTopics(res.data.topics || []);
            } else {
                setSavedMaterial(null);
                setAvailableTopics([]);
            }
        } catch (e) {
            console.error("Error checking material", e);
        }
    };

    const clearMaterial = async () => {
        try {
            await axios.post(`${API_URL}/clear-material`);
            setSavedMaterial(null);
            setFile(null);
            setAvailableTopics([]);
            setSelectedTopics([]);
        } catch (e) {
            console.error("Error clearing material", e);
        }
    };

    const handleFileChange = (e) => {
        if (e.target.files && e.target.files[0]) {
            setFile(e.target.files[0]);
            // Reset previous analysis when new file picked
            setAvailableTopics([]);
            setSelectedTopics([]);
        }
    };

    const analyzeFile = async () => {
        if (!file) return;
        setIsAnalyzing(true);
        setErrorMsg('');

        const formData = new FormData();
        formData.append("file", file);
        if (apiKey) {
            formData.append("api_key", apiKey);
        }

        try {
            const res = await axios.post(`${API_URL}/upload`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            // Upload success, update state
            await checkSavedMaterial();
            setIsAnalyzing(false);
        } catch (err) {
            console.error(err);
            setErrorMsg("Falha ao analisar o ficheiro.");
            setIsAnalyzing(false);
        }
    };

    // Retroactive Analysis for existing material
    const detectTopics = async () => {
        setIsAnalyzing(true);
        setErrorMsg('');
        try {
            const res = await axios.post(`${API_URL}/analyze-topics`, {
                api_key: apiKey
            });
            setAvailableTopics(res.data.topics);
            // Refresh saved material to sync state
            await checkSavedMaterial();
            setIsAnalyzing(false);
        } catch (err) {
            console.error(err);
            setErrorMsg("Falha ao detetar tópicos. Verifica a API Key.");
            setIsAnalyzing(false);
        }
    };


    // Dropdown Logic
    const handleTopicChange = (e) => {
        const val = e.target.value;
        if (val === "ALL") {
            setSelectedTopics([]); // Empty means ALL in our logic
        } else {
            setSelectedTopics([val]);
        }
    };

    const generateQuiz = async () => {
        setGameState('loading');
        setErrorMsg('');

        try {
            // 2. Generate Quiz using saved material
            const quizRes = await axios.post(`${API_URL}/generate-quiz`, {
                use_saved: true,
                topics: selectedTopics,
                api_key: apiKey || null
            });

            const parsedQuestions = quizRes.data;

            if (!parsedQuestions || parsedQuestions.length === 0) {
                throw new Error("Nenhuma pergunta gerada.");
            }

            const adaptedQuestions = parsedQuestions.map(q => ({
                question: q.pergunta || q.question,
                options: q.opcoes || q.options,
                correctAnswer: q.resposta_correta !== undefined ? q.resposta_correta : q.correctAnswer,
                explanation: q.explicacao || q.explanation
            }));

            setQuestions(adaptedQuestions);
            setGameState('playing');
            setCurrentQuestionIndex(0);
            setScore(0);
            resetQuestionState();

        } catch (error) {
            console.error(error);
            setErrorMsg(error.response?.data?.detail || error.message || "Ups! Ocorreu um erro ao criar o quiz. Tenta novamente.");
            setGameState('error');
        }
    };

    const resetQuestionState = () => {
        setSelectedOption(null);
        setShowExplanation(false);
    };

    const handleOptionClick = (index) => {
        if (selectedOption !== null) return;
        setSelectedOption(index);
        setShowExplanation(true);

        if (index === questions[currentQuestionIndex].correctAnswer) {
            setScore(s => s + 1);
        }
    };

    const nextQuestion = () => {
        if (currentQuestionIndex < questions.length - 1) {
            setCurrentQuestionIndex(prev => prev + 1);
            resetQuestionState();
        } else {
            setGameState('results');
        }
    };

    const exitQuiz = () => {
        if (confirm("Tens a certeza que queres sair? Vais perder o progresso atual.")) {
            setGameState('intro');
            setQuestions([]);
            setScore(0);
        }
    };

    const restartGamePayload = () => {
        setGameState('intro');
        setQuestions([]);
        setScore(0);
    };

    // --- UI Components ---

    if (gameState === 'intro' || gameState === 'error') {
        return (
            <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-purple-100 p-6 flex items-center justify-center font-sans">
                <div className="max-w-2xl w-full bg-white rounded-3xl shadow-xl overflow-hidden border-4 border-indigo-100">
                    <div className="bg-gradient-to-r from-indigo-600 to-purple-600 p-8 text-white text-center">
                        <div className="flex justify-center mb-4">
                            <Brain size={64} className="text-yellow-300 animate-bounce" />
                        </div>
                        <h1 className="text-3xl font-bold mb-2">Quiz Mágico de Estudo</h1>
                        <p className="text-indigo-100">Transforma os teus apontamentos num jogo!</p>
                    </div>

                    <div className="p-8 space-y-6">

                        {/* API Key Input */}
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                OpenAI API Key (Opcional se já configurada no backend)
                            </label>
                            <input
                                type="password"
                                value={apiKey}
                                onChange={(e) => setApiKey(e.target.value)}
                                placeholder="sk-..."
                                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                            />
                        </div>

                        {/* ERROR DISPLAY */}
                        {errorMsg && (
                            <div className="mb-4 p-4 bg-red-100 text-red-700 rounded-xl flex items-center gap-2 animate-pulse">
                                <XCircle size={20} />
                                {errorMsg}
                            </div>
                        )}

                        {/* SAVED MATERIAL CARD */}
                        {savedMaterial ? (
                            <div className="bg-indigo-50 border-2 border-indigo-200 rounded-xl p-6 relative">
                                <div className="flex items-start gap-4">
                                    <div className="p-3 bg-white rounded-lg shadow-sm text-indigo-600 shrink-0">
                                        <FileText size={32} />
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        <h3 className="font-bold text-lg text-indigo-900 mb-1">Continuar Estudo</h3>
                                        <p className="text-sm text-indigo-600 font-medium mb-2 truncate">{savedMaterial.source}</p>
                                        <div className="text-xs text-gray-500 bg-white p-2 rounded border border-indigo-100 mb-4 truncate">
                                            {savedMaterial.preview}...
                                        </div>

                                        {/* Topic Selection Logic */}
                                        {availableTopics.length > 0 ? (
                                            <div className="mb-4">
                                                <label htmlFor="topic-select" className="text-sm font-bold text-indigo-800 mb-2 flex items-center gap-2">
                                                    <List size={16} /> Escolhe o Tópico:
                                                </label>
                                                <div className="relative">
                                                    <select
                                                        id="topic-select"
                                                        onChange={handleTopicChange}
                                                        className="w-full appearance-none bg-white border border-indigo-200 text-gray-700 py-3 px-4 rounded-xl leading-tight focus:outline-none focus:bg-white focus:border-indigo-500 cursor-pointer"
                                                        value={selectedTopics.length === 0 ? "ALL" : selectedTopics[0]}
                                                    >
                                                        <option value="ALL">🌟 Todos os Tópicos</option>
                                                        <hr />
                                                        {availableTopics.map((topic, idx) => (
                                                            <option key={idx} value={topic}>{topic}</option>
                                                        ))}
                                                    </select>
                                                    <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-4 text-indigo-500">
                                                        <ChevronDown size={20} />
                                                    </div>
                                                </div>
                                            </div>
                                        ) : (
                                            /* Button to Detect Topics if missing */
                                            <div className="mb-4">
                                                <label className="text-sm font-bold text-indigo-800 mb-2 flex items-center gap-2">
                                                    <List size={16} /> Tópicos não detetados
                                                </label>
                                                <button
                                                    onClick={detectTopics}
                                                    disabled={isAnalyzing}
                                                    className="w-full py-2 px-3 bg-indigo-50 text-indigo-600 border border-indigo-200 rounded-lg text-sm font-semibold flex items-center justify-center gap-2 hover:bg-indigo-100 transition-colors"
                                                >
                                                    {isAnalyzing ? <RefreshCw className="animate-spin" size={16} /> : <Search size={16} />}
                                                    {isAnalyzing ? "A analisar..." : "Identificar Tópicos Agora"}
                                                </button>
                                            </div>
                                        )}

                                        <div className="flex gap-3">
                                            <button
                                                onClick={generateQuiz}
                                                className="flex-1 py-3 bg-indigo-600 text-white rounded-lg font-bold hover:bg-indigo-700 transition-colors shadow-lg shadow-indigo-200 flex items-center justify-center gap-2"
                                            >
                                                <Sparkles size={18} />
                                                Gerar Quiz
                                            </button>
                                            <button
                                                onClick={clearMaterial}
                                                className="p-3 text-red-500 bg-white border border-red-200 rounded-lg hover:bg-red-50 transition-colors shrink-0"
                                                title="Apagar matéria"
                                                aria-label="Apagar matéria"
                                            >
                                                <Trash2 size={20} />
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        ) : (
                            /* FILE UPLOAD CARD */
                            <div className="border-2 border-dashed border-indigo-200 rounded-xl p-8 text-center hover:bg-indigo-50 transition-colors cursor-pointer relative group focus-within:ring-4 focus-within:ring-indigo-200 focus-within:border-indigo-500 focus-within:outline-none">
                                <input
                                    type="file"
                                    onChange={handleFileChange}
                                    accept=".pdf,.txt"
                                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                                    aria-label="Carregar ficheiro (PDF ou TXT)"
                                />
                                <div className="group-hover:scale-110 transition-transform duration-300 inline-block mb-3">
                                    <Upload className="mx-auto text-indigo-400" size={48} />
                                </div>
                                <p className="text-indigo-600 font-bold text-lg">
                                    {file ? file.name : "Carregar Ficheiro PDF ou TXT"}
                                </p>
                                <p className="text-sm text-gray-500 mt-2">Clica ou arrasta para aqui</p>
                            </div>
                        )}

                        {!savedMaterial && (
                            <button
                                onClick={analyzeFile}
                                disabled={!file || isAnalyzing}
                                className={`w-full py-4 rounded-xl text-xl font-bold flex items-center justify-center gap-2 transition-all transform hover:scale-[1.02] active:scale-95 shadow-lg ${!file || isAnalyzing
                                        ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                                        : 'bg-gradient-to-r from-purple-500 to-indigo-600 text-white hover:shadow-indigo-500/30'
                                    }`}
                            >
                                <Sparkles className={isAnalyzing ? "animate-spin" : ""} />
                                {isAnalyzing ? "A analisar..." : "Carregar e Analisar"}
                            </button>
                        )}

                        <p className="text-center text-gray-400 text-xs mt-4">10 perguntas automáticas sobre os teus tópicos!</p>
                    </div>
                </div>
            </div>
        );
    }

    // Tela de Loading
    if (gameState === 'loading') {
        return (
            <div className="min-h-screen bg-indigo-50 flex flex-col items-center justify-center p-6">
                <div className="w-32 h-32 relative">
                    <div className="absolute inset-0 border-8 border-indigo-200 rounded-full"></div>
                    <div className="absolute inset-0 border-8 border-indigo-600 rounded-full border-t-transparent animate-spin"></div>
                    <Brain className="absolute inset-0 m-auto text-indigo-500" size={40} />
                </div>
                <h2 className="mt-8 text-2xl font-bold text-indigo-800 animate-pulse">A gerar 10 perguntas...</h2>
                {selectedTopics.length > 0 && <p className="text-indigo-600 mt-1">Focadas em: {selectedTopics.join(", ")}</p>}
            </div>
        );
    }

    // Tela de Jogo (Quiz)
    if (gameState === 'playing') {
        const question = questions[currentQuestionIndex];
        const isCorrect = selectedOption === question.correctAnswer;
        const progress = ((currentQuestionIndex) / questions.length) * 100;

        return (
            <div className="min-h-screen bg-slate-100 p-4 md:p-8 flex items-center justify-center font-sans">
                <div className="max-w-3xl w-full">
                    {/* Top Bar with Exit */}
                    <div className="flex items-center justify-between mb-6 px-2">
                        <button
                            onClick={exitQuiz}
                            className="text-slate-400 hover:text-red-500 text-sm font-bold flex items-center gap-1 transition-colors"
                        >
                            <LogOut size={16} /> Sair
                        </button>
                        <div className="text-indigo-600 font-bold bg-indigo-100 px-3 py-1 rounded-full text-sm">
                            {currentQuestionIndex + 1} / {questions.length}
                        </div>
                    </div>

                    {/* Progress Bar */}
                    <div className="w-full bg-gray-200 rounded-full h-2 mb-6">
                        <div className="bg-gradient-to-r from-indigo-500 to-purple-500 h-2 rounded-full transition-all duration-300" style={{ width: `${progress}%` }}></div>
                    </div>

                    <div className="bg-white rounded-3xl shadow-xl overflow-hidden border border-slate-200">
                        {/* Pergunta */}
                        <div className="p-8 border-b border-slate-100 bg-indigo-50/30">
                            <h2 className="text-2xl md:text-3xl font-bold text-slate-800 leading-tight">
                                {question.question}
                            </h2>
                        </div>

                        {/* ... Rest of Quiz Logic (Options, Feedback) ... */}
                        <div className="p-8 grid gap-4">
                            {question.options.map((option, idx) => {
                                let btnClass = "w-full text-left p-5 rounded-2xl border-2 text-lg font-medium transition-all duration-200 ";

                                if (selectedOption === null) {
                                    btnClass += "border-slate-100 hover:border-indigo-400 hover:bg-indigo-50 text-slate-600 hover:text-indigo-700 cursor-pointer shadow-sm hover:shadow-md";
                                } else {
                                    if (idx === question.correctAnswer) {
                                        btnClass += "border-green-500 bg-green-50 text-green-800 shadow-md ring-2 ring-green-200";
                                    } else if (idx === selectedOption) {
                                        btnClass += "border-red-400 bg-red-50 text-red-800 opacity-75";
                                    } else {
                                        btnClass += "border-slate-100 text-slate-400 opacity-50";
                                    }
                                }

                                return (
                                    <button
                                        key={idx}
                                        onClick={() => handleOptionClick(idx)}
                                        disabled={selectedOption !== null}
                                        className={btnClass}
                                    >
                                        <div className="flex items-center justify-between">
                                            <span>{option}</span>
                                            {selectedOption !== null && idx === question.correctAnswer && (
                                                <CheckCircle className="text-green-600" size={24} />
                                            )}
                                            {selectedOption !== null && idx === selectedOption && idx !== question.correctAnswer && (
                                                <XCircle className="text-red-500" size={24} />
                                            )}
                                        </div>
                                    </button>
                                );
                            })}
                        </div>

                        {/* Feedback e Explicação */}
                        {showExplanation && (
                            <div className={`p-6 mx-8 mb-8 rounded-2xl ${isCorrect ? 'bg-green-100' : 'bg-orange-50'} animate-in fade-in slide-in-from-bottom-4 duration-500 border ${isCorrect ? 'border-green-200' : 'border-orange-200'}`}>
                                <div className="flex items-start gap-3">
                                    {isCorrect ? (
                                        <div className="p-2 bg-green-200 rounded-full text-green-700">
                                            <Sparkles size={24} />
                                        </div>
                                    ) : (
                                        <div className="p-2 bg-orange-200 rounded-full text-orange-700">
                                            <BookOpen size={24} />
                                        </div>
                                    )}
                                    <div>
                                        <h3 className={`font-bold text-lg mb-1 ${isCorrect ? 'text-green-800' : 'text-orange-800'}`}>
                                            {isCorrect ? "Excelente!" : "Quase lá!"}
                                        </h3>
                                        <p className="text-slate-700 leading-relaxed">
                                            {question.explanation}
                                        </p>
                                    </div>
                                </div>

                                <div className="mt-6 flex justify-end">
                                    <button
                                        onClick={nextQuestion}
                                        className="bg-indigo-600 text-white px-8 py-3 rounded-xl font-bold text-lg hover:bg-indigo-700 transition-colors flex items-center gap-2 shadow-lg shadow-indigo-200"
                                    >
                                        {currentQuestionIndex < questions.length - 1 ? 'Próxima Pergunta' : 'Ver Resultados'}
                                        <ArrowRight size={20} />
                                    </button>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        );
    }

    // Tela de Resultados
    if (gameState === 'results') {
        const percentage = Math.round((score / questions.length) * 100);
        let message = "";
        let emoji = "";

        if (percentage === 100) { message = "Fantástico! Sabes tudo!"; emoji = "🏆"; }
        else if (percentage >= 80) { message = "Muito bom trabalho!"; emoji = "🌟"; }
        else if (percentage >= 50) { message = "Bom esforço! Continua a estudar."; emoji = "📚"; }
        else { message = "Vamos rever a matéria mais uma vez?"; emoji = "💪"; }

        return (
            <div className="min-h-screen bg-gradient-to-br from-indigo-600 to-purple-700 flex items-center justify-center p-6 font-sans">
                <div className="bg-white rounded-3xl p-10 max-w-lg w-full text-center shadow-2xl animate-in zoom-in duration-300">
                    <div className="mb-6 inline-block p-6 bg-yellow-100 rounded-full text-6xl animate-bounce">
                        {emoji}
                    </div>

                    <h2 className="text-4xl font-bold text-slate-800 mb-2">Quiz Terminado!</h2>
                    <p className="text-slate-500 text-lg mb-8">{message}</p>

                    <div className="flex justify-center items-end gap-2 mb-8 text-indigo-900">
                        <span className="text-7xl font-extrabold">{score}</span>
                        <span className="text-2xl font-bold text-slate-400 mb-2">/ {questions.length}</span>
                    </div>

                    <div className="w-full bg-slate-100 rounded-full h-4 mb-8 overflow-hidden">
                        <div
                            className="bg-gradient-to-r from-green-400 to-indigo-500 h-full transition-all duration-1000 ease-out"
                            style={{ width: `${percentage}%` }}
                        />
                    </div>

                    <div className="flex flex-col gap-3">
                        <button
                            onClick={restartGamePayload}
                            className="w-full py-4 bg-indigo-600 text-white rounded-xl font-bold text-xl hover:bg-indigo-700 transition-all flex items-center justify-center gap-2 shadow-lg hover:shadow-indigo-500/40"
                        >
                            <RefreshCw size={24} />
                            Reiniciar
                        </button>
                        <button
                            onClick={() => { clearMaterial(); restartGamePayload(); }}
                            className="text-white/80 hover:text-white text-sm font-medium py-2"
                        >
                            Escolher outra matéria
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    return null;
}
