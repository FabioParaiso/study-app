import React, { useState } from 'react';
import { Send, Volume2, StopCircle, ArrowRight, CheckCircle, XCircle } from 'lucide-react';

const ShortAnswerCard = ({
    question,
    index,
    total,
    onSubmit,
    evaluation,
    onNext,
    handleSpeak,
    speakingPart
}) => {
    const [userText, setUserText] = useState("");
    const [submitted, setSubmitted] = useState(false);

    const handleSubmit = () => {
        if (userText.trim()) {
            setSubmitted(true);
            onSubmit(userText);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !submitted) {
            handleSubmit();
        }
    };

    return (
        <div className="w-full max-w-2xl mx-auto animate-fade-in">
            <div className="bg-white rounded-3xl shadow-xl p-8 border-b-8 border-blue-100 relative overflow-hidden">
                {/* Progress Bar */}
                <div className="absolute top-0 left-0 w-full h-2 bg-gray-100">
                    <div className="h-full bg-blue-500 transition-all duration-500" style={{ width: `${((index + 1) / total) * 100}%` }}></div>
                </div>

                {/* Header */}
                <div className="flex justify-between items-center mb-6 mt-2">
                    <span className="text-xs font-bold tracking-wider text-blue-400 uppercase">
                        Resposta Curta {index + 1} de {total}
                    </span>
                    <span className="px-3 py-1 bg-blue-50 text-blue-600 rounded-full text-xs font-bold border border-blue-100">
                        {question.topic || "Geral"}
                    </span>
                </div>

                {/* Question */}
                <div className="flex items-start gap-4 mb-6">
                    <p className="text-gray-800 text-xl font-medium leading-relaxed flex-grow">{question.question}</p>
                    <button
                        onClick={() => handleSpeak(question.question, 'question')}
                        aria-label={speakingPart === 'question' ? "Parar leitura" : "Ler pergunta"}
                        className={`p-3 rounded-full transition-all duration-200 flex-shrink-0 shadow-sm ${speakingPart === 'question'
                            ? 'bg-blue-100 text-blue-600 ring-2 ring-blue-300'
                            : 'bg-gray-100 text-gray-500 hover:bg-blue-50 hover:text-blue-600'
                            }`}
                    >
                        {speakingPart === 'question' ? <StopCircle size={24} /> : <Volume2 size={24} />}
                    </button>
                </div>

                {/* Input or Result */}
                {!evaluation ? (
                    <div className="space-y-4">
                        <input
                            type="text"
                            className="w-full p-4 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all text-gray-700 text-lg"
                            placeholder="Escreve a tua resposta..."
                            value={userText}
                            onChange={(e) => setUserText(e.target.value)}
                            onKeyPress={handleKeyPress}
                            disabled={submitted}
                            autoFocus
                        />
                        <div className="flex justify-end">
                            <button
                                onClick={handleSubmit}
                                disabled={submitted || userText.trim().length === 0}
                                className={`font-bold py-3 px-8 rounded-full shadow-lg flex items-center text-lg transition-all ${submitted || userText.trim().length === 0
                                        ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                                        : 'bg-blue-600 hover:bg-blue-700 text-white hover:shadow-xl hover:-translate-y-1'
                                    }`}
                            >
                                Confirmar <Send className="ml-2" size={20} />
                            </button>
                        </div>
                    </div>
                ) : (
                    <div className="animate-slide-up space-y-4">
                        {/* User Answer */}
                        <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                            <p className="text-gray-500 text-xs font-bold uppercase mb-1">A tua resposta:</p>
                            <p className="text-gray-700 italic">"{userText}"</p>
                        </div>

                        {/* Result */}
                        <div className={`p-5 rounded-xl border shadow-sm flex items-center gap-4 ${evaluation.is_correct
                                ? 'bg-green-50 border-green-200'
                                : 'bg-orange-50 border-orange-200'
                            }`}>
                            <div className={`p-3 rounded-full ${evaluation.is_correct
                                    ? 'bg-green-100 text-green-600'
                                    : 'bg-orange-100 text-orange-600'
                                }`}>
                                {evaluation.is_correct
                                    ? <CheckCircle size={32} />
                                    : <XCircle size={32} />
                                }
                            </div>
                            <p className={`text-lg font-medium ${evaluation.is_correct ? 'text-green-700' : 'text-orange-700'
                                }`}>
                                {evaluation.feedback}
                            </p>
                        </div>

                        {/* Next Button */}
                        <div className="flex justify-end">
                            <button
                                onClick={onNext}
                                className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-8 rounded-full shadow-lg hover:shadow-xl transform transition hover:-translate-y-1 flex items-center text-lg"
                            >
                                {index < total - 1 ? 'Próxima' : 'Ver Nota'}
                                <ArrowRight className="ml-2" size={20} />
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ShortAnswerCard;
