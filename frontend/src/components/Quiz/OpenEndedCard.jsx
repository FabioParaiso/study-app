import React, { useState, useEffect } from 'react';
import { useSpeechRecognition } from '../../hooks/useSpeechRecognition';
import { Send, Mic, MicOff } from 'lucide-react';
import { ProgressBar, QuestionHeader, SUCCESS_MESSAGES, PARTIAL_SUCCESS_MESSAGES, getRandomMessage } from './shared';

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
            <div className="w-full max-w-2xl mx-auto animate-fade-in mb-40">
                <ProgressBar current={index} total={total} color="bg-purple-500" />

                <QuestionHeader
                    topic={question.topic}
                    question={question.question}
                    onSpeak={handleSpeak}
                    isSpeaking={speakingPart === 'question'}
                    accentColor="purple"
                />

                {/* Input Area */}
                <div className="relative w-full mb-6">
                    <textarea
                        aria-label="A tua resposta detalhada"
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
                            aria-label={isListening ? "Desativar microfone" : "Ativar microfone"}
                            className={`absolute bottom-4 right-4 p-3 rounded-xl transition-all border-b-4 active:border-b-0 active:translate-y-1 ${isListening
                                ? 'bg-red-100 text-red-500 border-red-300 animate-pulse'
                                : 'bg-gray-100 text-gray-400 border-gray-300 hover:text-purple-500 hover:bg-purple-50'
                                }`}
                        >
                            {isListening ? <MicOff size={24} /> : <Mic size={24} />}
                        </button>
                    )}
                </div>

                {/* Feedback Section (In Flow) */}
                {evaluation && (
                    <div className="animate-slide-up space-y-4 w-full">
                        {/* Score & Feedback Header */}
                        <div className="flex items-start gap-4">
                            <div className={`p-3 rounded-2xl flex flex-col items-center justify-center w-20 h-20 flex-shrink-0 border-b-4 ${isGoodScore
                                ? 'bg-white text-green-600 border-green-200'
                                : 'bg-white text-red-600 border-red-200'}`}>
                                <span className="text-2xl font-black">{evaluation.score}</span>
                                <span className="text-[10px] font-bold uppercase">Nota</span>
                            </div>
                            <div className="flex-1 py-2">
                                <h3 className={`font-bold text-xl mb-1 ${isGoodScore ? 'text-green-600' : 'text-red-600'}`}>
                                    {isGoodScore
                                        ? getRandomMessage(SUCCESS_MESSAGES)
                                        : getRandomMessage(PARTIAL_SUCCESS_MESSAGES)}
                                </h3>
                                <p className="text-sm font-medium text-gray-500">{evaluation.feedback}</p>
                            </div>
                        </div>

                        {/* Logic: Score < 50 -> Global Re-teaching (Text) | Score >= 50 -> Specific Refining (List) */}
                        {evaluation.score < 50 ? (
                            /* Re-teaching Mode: Show Full Model Answer */
                            <div className="bg-orange-50 border border-orange-100 rounded-xl p-4">
                                <p className="text-xs font-bold text-orange-600 uppercase tracking-wider mb-2">💡 Resposta Completa:</p>
                                <p className="text-gray-800 text-sm leading-relaxed">{evaluation.model_answer}</p>
                            </div>
                        ) : (
                            /* Refining Mode: Show Missing Points (if any) */
                            evaluation.missing_points && evaluation.missing_points.length > 0 && (
                                <div className="bg-red-50 border border-red-100 rounded-xl p-4">
                                    <p className="text-xs font-bold text-red-500 uppercase tracking-wider mb-2">Faltou referir:</p>
                                    <ul className="list-disc list-inside space-y-1">
                                        {evaluation.missing_points.map((point, i) => (
                                            <li key={i} className="text-gray-800 text-sm leading-relaxed font-medium">
                                                {point}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            )
                        )}

                        {/* Curiosity Block (Always show) */}
                        {evaluation.curiosity && (
                            <div className="bg-blue-50 border border-blue-100 rounded-xl p-4">
                                <p className="text-xs font-bold text-blue-500 uppercase tracking-wider mb-2">🤔 Sabias que...</p>
                                <p className="text-gray-800 text-sm leading-relaxed">{evaluation.curiosity}</p>
                            </div>
                        )}
                    </div>
                )}
            </div>

            {/* Fixed Bottom Action Bar */}
            <div className={`fixed bottom-0 left-0 w-full p-4 border-t-2 bg-white border-gray-200 z-50`}>
                <div className="max-w-2xl mx-auto">
                    <button
                        onClick={evaluation ? onNext : handleEvaluation}
                        disabled={(!evaluation && userText.trim().length === 0) || isEvaluating}
                        className={`w-full py-4 rounded-2xl border-b-4 font-bold text-white uppercase tracking-wider transition-all active:border-b-0 active:translate-y-1 text-center flex items-center justify-center gap-2 outline-none focus:outline-none ${isEvaluating
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
        </>
    );
};

export default OpenEndedCard;
