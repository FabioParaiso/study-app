import React, { useState } from 'react';
import { useSpeechRecognition } from '../../hooks/useSpeechRecognition';
import { Send, Volume2, StopCircle, ArrowRight, Mic, MicOff } from 'lucide-react';

const OpenEndedCard = ({ question, index, total, onEvaluate, evaluation, isEvaluating, onNext, handleSpeak, speakingPart }) => {
    const [userText, setUserText] = useState("");
    const { isListening, transcript, startListening, stopListening, supported } = useSpeechRecognition();

    // Append speech to text when finished listening
    React.useEffect(() => {
        if (!isListening && transcript) {
            setUserText(prev => (prev + " " + transcript).trim());
        }
    }, [isListening, transcript]);

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
                        <div className="relative">
                            <textarea
                                className="w-full p-4 border-2 border-gray-200 rounded-xl focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition-all text-gray-700 min-h-[120px] resize-y pr-14"
                                placeholder={isListening ? "A escutar..." : "Escreve a tua resposta aqui ou usa o microfone..."}
                                value={isListening ? userText + " " + transcript : userText}
                                onChange={(e) => setUserText(e.target.value)}
                                disabled={isEvaluating}
                            />
                            {supported && (
                                <button
                                    onClick={isListening ? stopListening : startListening}
                                    className={`absolute top-3 right-3 p-2 rounded-full transition-all ${isListening
                                        ? 'bg-red-100 text-red-500 animate-pulse'
                                        : 'bg-gray-100 text-gray-400 hover:text-purple-500'
                                        }`}
                                >
                                    {isListening ? <MicOff size={20} /> : <Mic size={20} />}
                                </button>
                            )}
                        </div>
                        <div className="flex justify-end">
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

                        <div className={`p-5 rounded-xl border mb-4 shadow-sm ${evaluation.score >= 50 ? 'bg-green-50 border-green-200' : 'bg-orange-50 border-orange-200'}`}>
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

                        {/* Model Answer Section */}
                        {evaluation.model_answer && (
                            <div className="bg-blue-50 border-2 border-blue-200 rounded-xl p-4 mb-6">
                                <p className="text-xs font-bold text-blue-600 uppercase tracking-wider mb-2">💡 Resposta Modelo</p>
                                <p className="text-gray-700 text-sm leading-relaxed mb-3">{evaluation.model_answer}</p>
                                <p className="text-xs text-blue-500 italic">Compara com a tua resposta. O que tinhas de diferente?</p>
                            </div>
                        )}

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

export default OpenEndedCard;
