import React, { useState } from 'react';
import { Send, CheckCircle, XCircle } from 'lucide-react';
import { ProgressBar, QuestionHeader, SUCCESS_MESSAGES, PARTIAL_SUCCESS_MESSAGES, getRandomMessage, FeedbackIcon } from './shared';

const ShortAnswerCard = ({
    question,
    index,
    total,
    onSubmit,
    evaluation,
    onNext,
    isEvaluating,
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

    // Derived state for styling
    const isCorrect = evaluation?.is_correct;

    // Loading state: Either explicitly evaluating OR local submission happened but no result yet
    const isLoading = isEvaluating || (submitted && !evaluation);

    return (
        <>
            {/* Main Card */}
            <div className="w-full max-w-2xl mx-auto animate-fade-in mb-32">
                <ProgressBar current={index} total={total} />

                <QuestionHeader
                    topic={question.topic}
                    concept={question.concepts?.[0]}
                    question={question.question}
                    onSpeak={handleSpeak}
                    isSpeaking={speakingPart === 'question'}
                    accentColor="blue"
                />

                {/* Input Area */}
                <div className="w-full">
                    <input
                        type="text"
                        aria-label="A tua resposta"
                        className={`w-full p-6 text-xl rounded-2xl border-2 border-b-4 outline-none transition-all font-medium ${submitted
                            ? 'bg-gray-100 border-gray-300 text-gray-500 cursor-not-allowed'
                            : 'bg-white border-gray-200 focus:border-duo-blue focus:border-b-4 text-gray-700'
                            }`}
                        placeholder="Escreve a tua resposta..."
                        value={userText}
                        onChange={(e) => setUserText(e.target.value)}
                        onKeyPress={handleKeyPress}
                        disabled={submitted}
                        autoFocus
                    />
                </div>
            </div>

            {/* Bottom Sheet Feedback / Action */}
            <div
                className={`fixed bottom-0 left-0 w-full transform transition-transform duration-300 ease-out z-50 ${submitted ? 'translate-y-0' : 'translate-y-0'}`}
            >
                <div className={`p-6 pb-8 border-t-2 ${evaluation
                    ? (isCorrect ? 'bg-green-100 border-transparent' : 'bg-red-50 border-transparent')
                    : 'bg-white border-gray-200'
                    }`}>
                    <div className="max-w-2xl mx-auto flex flex-col items-center justify-between gap-6">

                        {evaluation ? (
                            <div className="w-full space-y-2">
                                {/* Header with Score Box and Feedback Title */}
                                <div className="flex items-start gap-4 w-full">
                                    {/* Score Box equivalent to Advanced Level */}
                                    <div className={`p-3 rounded-2xl flex flex-col items-center justify-center w-20 h-20 flex-shrink-0 border-b-4 ${isCorrect
                                        ? 'bg-white text-green-600 border-green-200'
                                        : 'bg-white text-red-600 border-red-200'}`}>
                                        <span className="text-2xl font-black">{evaluation.score}</span>
                                        <span className="text-[10px] font-bold uppercase">Nota</span>
                                    </div>

                                    <div className="flex-1">
                                        {(() => {
                                            const msg = isCorrect
                                                ? getRandomMessage(SUCCESS_MESSAGES)
                                                : getRandomMessage(PARTIAL_SUCCESS_MESSAGES);
                                            return (
                                                <h3 className={`font-bold text-xl mb-1 flex items-center gap-2 ${isCorrect ? 'text-duo-green-dark' : 'text-duo-red-dark'}`}>
                                                    <FeedbackIcon iconName={msg.icon} className="w-6 h-6" />
                                                    <span>{msg.text}</span>
                                                </h3>
                                            );
                                        })()}
                                    </div>
                                </div>

                                {/* Logic: Score < 50 -> Global Re-teaching (Text) | Score >= 50 -> Specific Refining (List) */}
                                {evaluation.score < 50 ? (
                                    /* Re-teaching Mode: Show Full Model Answer */
                                    <div className="bg-orange-50 border border-orange-100 rounded-xl p-4 w-full ml-0 md:ml-0 mt-2">
                                        <p className="text-xs font-bold text-orange-600 uppercase tracking-wider mb-2">💡 Resposta Completa:</p>
                                        <p className="text-gray-800 text-sm leading-relaxed">{evaluation.model_answer}</p>
                                    </div>
                                ) : (
                                    /* Refining Mode: Show Missing Points (if any) */
                                    evaluation.missing_points && evaluation.missing_points.length > 0 && (
                                        <div className="bg-red-50 border border-red-100 rounded-xl p-4 w-full ml-0 md:ml-0 mt-2">
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
                                    <div className="bg-blue-50 border border-blue-100 rounded-xl p-4 w-full ml-0 md:ml-0 mt-2">
                                        <p className="text-xs font-bold text-blue-500 uppercase tracking-wider mb-2">🤔 Sabias que...</p>
                                        <p className="text-gray-800 text-sm leading-relaxed">{evaluation.curiosity}</p>
                                    </div>
                                )}
                            </div>
                        ) : (
                            <div className="hidden md:block flex-1"></div>
                        )}

                        {/* Action Button */}
                        <div className="w-full flex justify-end">
                            <button
                                onClick={evaluation ? onNext : handleSubmit}
                                disabled={isLoading || (!submitted && userText.trim().length === 0)}
                                className={`w-full md:w-auto px-10 py-4 rounded-2xl border-b-4 font-bold text-white uppercase tracking-wider transition-all active:border-b-0 active:translate-y-1 text-center flex items-center justify-center gap-2 outline-none focus:outline-none ${isLoading
                                    ? 'bg-gray-400 border-gray-600 cursor-wait'
                                    : !submitted
                                        ? (userText.trim().length === 0
                                            ? 'bg-gray-300 border-gray-400 cursor-not-allowed text-gray-500'
                                            : 'bg-duo-green border-duo-green-dark hover:bg-green-500')
                                        : (isCorrect
                                            ? 'bg-duo-green border-duo-green-dark hover:bg-green-500'
                                            : 'bg-duo-red border-duo-red-dark hover:bg-red-500')
                                    }`}
                            >
                                {isLoading ? (
                                    'A CORRIGIR...'
                                ) : evaluation ? (
                                    index < total - 1 ? 'Continuar' : 'Ver Nota'
                                ) : (
                                    <>VERIFICAR <Send size={20} className="ml-2" /></>
                                )}
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </>
    );
};

export default ShortAnswerCard;
