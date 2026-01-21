import React, { useState, useEffect } from 'react';
import { useSpeechRecognition } from '../../hooks/useSpeechRecognition';
import { Send, Volume2, StopCircle, ArrowRight, Mic, MicOff, CheckCircle, XCircle } from 'lucide-react';

const OpenEndedCard = ({ question, index, total, onEvaluate, evaluation, isEvaluating, onNext, handleSpeak, speakingPart }) => {
    const [userText, setUserText] = useState("");
    const { isListening, transcript, startListening, stopListening, supported } = useSpeechRecognition();

    // Append speech to text when finished listening
    useEffect(() => {
        if (!isListening && transcript) {
            setUserText(prev => (prev + " " + transcript).trim());
        }
    }, [isListening, transcript]);

    const handleEvaluation = () => {
        if (userText.trim()) {
            onEvaluate(userText);
        }
    };

    const isGoodScore = evaluation?.score >= 50;

    return (
        <>
            {/* Main Card */}
            <div className="w-full max-w-2xl mx-auto animate-fade-in mb-32">
                {/* Progress Bar */}
                <div className="w-full h-4 bg-gray-200 rounded-full mb-8 relative overflow-hidden">
                    <div className="h-full bg-purple-500 transition-all duration-500 rounded-full" style={{ width: `${((index + 1) / total) * 100}%` }}>
                        <div className="absolute top-1 left-2 w-full h-1 bg-white opacity-20 rounded-full"></div>
                    </div>
                </div>

                {/* Header & Question */}
                <div className="flex items-start gap-4 mb-8">
                    <h2 className="text-2xl md:text-3xl font-bold text-gray-700 leading-tight flex-1">
                        {question.question}
                    </h2>
                    <button
                        onClick={() => handleSpeak(question.question, 'question')}
                        className={`p-3 rounded-2xl border-b-4 transition-all active:border-b-0 active:translate-y-1 ${speakingPart === 'question'
                            ? 'bg-purple-500 text-white border-purple-700'
                            : 'bg-white text-purple-500 border-gray-200 hover:bg-purple-50'
                            }`}
                    >
                        {speakingPart === 'question' ? <StopCircle size={24} /> : <Volume2 size={24} />}
                    </button>
                </div>

                {/* Input Area */}
                <div className="relative w-full">
                    <textarea
                        className={`w-full p-6 text-xl rounded-2xl border-2 border-b-4 outline-none transition-all font-medium min-h-[200px] resize-y ${evaluation
                            ? 'bg-gray-50 border-gray-200 text-gray-500 cursor-not-allowed'
                            : 'bg-white border-gray-200 focus:border-purple-500 focus:border-b-4 text-gray-700'
                            }`}
                        placeholder={isListening ? "A escutar..." : "Escreve a tua resposta aqui..."}
                        value={isListening ? userText + " " + transcript : userText}
                        onChange={(e) => setUserText(e.target.value)}
                        disabled={!!evaluation || isEvaluating}
                    />

                    {/* Microphone Button inside textarea area */}
                    {!evaluation && supported && (
                        <button
                            onClick={isListening ? stopListening : startListening}
                            className={`absolute bottom-4 right-4 p-3 rounded-xl transition-all border-b-4 active:border-b-0 active:translate-y-1 ${isListening
                                ? 'bg-red-100 text-red-500 border-red-300 animate-pulse'
                                : 'bg-gray-100 text-gray-400 border-gray-300 hover:text-purple-500 hover:bg-purple-50'
                                }`}
                        >
                            {isListening ? <MicOff size={24} /> : <Mic size={24} />}
                        </button>
                    )}
                </div>
            </div>

            {/* Bottom Sheet Feedback / Action */}
            <div
                className={`fixed bottom-0 left-0 w-full transform transition-transform duration-300 ease-out z-50 ${evaluation ? 'translate-y-0' : 'translate-y-0'
                    }`}
            >
                <div className={`p-6 pb-8 border-t-2 ${evaluation
                    ? (isGoodScore ? 'bg-green-100 border-transparent' : 'bg-red-50 border-transparent')
                    : 'bg-white border-gray-200'
                    }`}>
                    <div className="max-w-3xl mx-auto flex flex-col gap-6">

                        {/* Detailed Feedback Content (Only if evaluated) */}
                        {evaluation ? (
                            <div className="animate-slide-up space-y-4">
                                {/* Score & Feedback Header */}
                                <div className="flex items-start gap-4">
                                    <div className={`p-3 rounded-2xl flex flex-col items-center justify-center w-20 h-20 flex-shrink-0 border-b-4 ${isGoodScore
                                        ? 'bg-white text-green-600 border-green-200'
                                        : 'bg-white text-red-600 border-red-200'}`}>
                                        <span className="text-2xl font-black">{evaluation.score}</span>
                                        <span className="text-[10px] font-bold uppercase">Nota</span>
                                    </div>
                                    <div className="flex-1">
                                        <h3 className={`font-bold text-xl mb-1 ${isGoodScore ? 'text-green-800' : 'text-red-800'}`}>
                                            {isGoodScore
                                                ? ["Fantástico! 🎉", "Muito bem! 🌟", "Excelente! 🚀"][Math.floor(Math.random() * 3)]
                                                : "Vamos aprender: 🧠"}
                                        </h3>
                                        <div className="flex items-start gap-2">
                                            <p className="text-gray-700 leading-relaxed flex-1">{evaluation.feedback}</p>
                                            <button
                                                onClick={() => handleSpeak(evaluation.feedback, 'feedback')}
                                                className={`p-2 rounded-full transition-all ${speakingPart === 'feedback'
                                                    ? 'bg-blue-100 text-blue-600'
                                                    : 'bg-white/50 text-gray-400 hover:text-blue-600'}`}
                                            >
                                                {speakingPart === 'feedback' ? <StopCircle size={20} /> : <Volume2 size={20} />}
                                            </button>
                                        </div>
                                    </div>
                                </div>

                                {/* Model Answer */}
                                {evaluation.model_answer && (
                                    <div className="bg-white/60 border border-black/5 rounded-xl p-4">
                                        <p className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">💡 Resposta Sugerida</p>
                                        <p className="text-gray-800 text-sm leading-relaxed">{evaluation.model_answer}</p>
                                    </div>
                                )}
                            </div>
                        ) : (
                            <div className="hidden md:block"></div>
                        )}

                        {/* Action Button */}
                        <div className="flex justify-end w-full">
                            <button
                                onClick={evaluation ? onNext : handleEvaluation}
                                disabled={(!evaluation && userText.trim().length === 0) || isEvaluating}
                                className={`w-full md:w-auto px-10 py-4 rounded-2xl border-b-4 font-bold text-white uppercase tracking-wider transition-all active:border-b-0 active:translate-y-1 text-center flex items-center justify-center gap-2 ${isEvaluating
                                    ? 'bg-gray-400 border-gray-600 cursor-wait'
                                    : !evaluation
                                        ? (userText.trim().length === 0
                                            ? 'bg-gray-300 border-gray-400 cursor-not-allowed text-gray-500'
                                            : 'bg-purple-600 border-purple-800 hover:bg-purple-500')
                                        : (isGoodScore
                                            ? 'bg-green-500 border-green-700 hover:bg-green-400'
                                            : 'bg-red-500 border-red-700 hover:bg-red-400')
                                    }`}
                            >
                                {isEvaluating ? (
                                    <>A CORRIGIR...</>
                                ) : evaluation ? (
                                    index < total - 1 ? 'CONTINUAR' : 'VER NOTA'
                                ) : (
                                    <>ENVIAR RESPOSTA <Send size={20} className="ml-2" /></>
                                )}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </>
    );
};

export default OpenEndedCard;
