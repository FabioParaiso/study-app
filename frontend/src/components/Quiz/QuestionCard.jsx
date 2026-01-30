import React from 'react';
import { CheckCircle, XCircle } from 'lucide-react';
import { ProgressBar, QuestionHeader, SUCCESS_MESSAGES, ERROR_MESSAGES, getRandomMessage, FeedbackIcon } from './shared';

const QuestionCard = ({ question, index, total, onAnswer, userAnswer, onNext, handleSpeak, speakingPart, showFeedback }) => {
    // Derived state
    const isAnswered = userAnswer !== null && userAnswer !== undefined;
    const isCorrect = isAnswered && userAnswer === question.correctIndex;

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

                <div className="grid gap-4">
                    {question.options.map((option, optIndex) => {
                        // Styles
                        let baseClass = "w-full text-left p-4 rounded-2xl border-2 border-b-4 text-lg font-bold transition-all flex items-center gap-4 relative ";
                        let stateClass = "bg-white border-gray-200 text-gray-700 hover:bg-gray-50 active:border-b-0 active:translate-y-1 active:mt-1 active:mb-[-1px]";

                        // Interaction Logic
                        if (isAnswered) {
                            if (optIndex === question.correctIndex) {
                                stateClass = "bg-green-50 border-duo-green text-duo-green-dark";
                            } else if (optIndex === userAnswer) {
                                stateClass = "bg-red-50 border-duo-red text-duo-red-dark";
                            } else {
                                stateClass = "bg-white border-gray-200 text-gray-300 opacity-60";
                            }
                        }

                        const letters = ['A', 'B', 'C', 'D'];

                        return (
                            <button
                                key={optIndex}
                                onClick={() => !isAnswered && onAnswer(index, optIndex)}
                                disabled={isAnswered}
                                className={`${baseClass} ${stateClass}`}
                            >
                                <span className={`w-8 h-8 rounded-lg border-2 flex items-center justify-center text-sm ${isAnswered && optIndex === question.correctIndex ? 'border-duo-green text-duo-green' :
                                    isAnswered && optIndex === userAnswer ? 'border-duo-red text-duo-red' :
                                        'border-gray-200 text-gray-400'
                                    }`}>
                                    {letters[optIndex]}
                                </span>
                                {option}
                            </button>
                        );
                    })}
                </div>
            </div>

            {/* Bottom Sheet Feedback */}
            <div
                className={`fixed bottom-0 left-0 w-full transform transition-transform duration-300 ease-out z-50 ${isAnswered ? 'translate-y-0' : 'translate-y-full'
                    }`}
            >
                <div className={`p-6 pb-8 border-t-2 ${isCorrect ? 'bg-green-100 border-transparent' : 'bg-red-50 border-transparent'
                    }`}>
                    <div className="max-w-2xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
                        <div className="flex-1 flex items-start gap-4 w-full">
                            <div className={`p-2 rounded-full hidden md:block ${isCorrect ? 'bg-white text-duo-green' : 'bg-white text-duo-red'}`}>
                                {isCorrect ? <CheckCircle size={32} /> : <XCircle size={32} />}
                            </div>
                            <div className="w-full">
                                {(() => {
                                    const msg = isCorrect
                                        ? getRandomMessage(SUCCESS_MESSAGES)
                                        : getRandomMessage(ERROR_MESSAGES);
                                    return (
                                        <h3 className={`font-bold text-xl mb-1 flex items-center gap-2 ${isCorrect ? 'text-duo-green-dark' : 'text-duo-red-dark'}`}>
                                            <FeedbackIcon iconName={msg.icon} className="w-6 h-6" />
                                            <span>{msg.text}</span>
                                        </h3>
                                    );
                                })()}
                                {!isCorrect && (
                                    <div className="text-gray-800 font-medium mb-2">
                                        A resposta certa é: <span className="font-bold">{question.options[question.correctIndex]}</span>
                                    </div>
                                )}
                                <div className="bg-white/50 p-3 rounded-xl text-sm text-gray-700 leading-relaxed border border-black/5">
                                    <span className="font-bold">💡 Curiosidade: </span>
                                    {question.explanation}
                                </div>
                            </div>
                        </div>

                        <button
                            onClick={onNext}
                            className={`w-full md:w-auto px-10 py-4 rounded-2xl border-b-4 font-bold text-white uppercase tracking-wider transition-all active:border-b-0 active:translate-y-1 ${isCorrect
                                ? 'bg-duo-green border-duo-green-dark hover:bg-green-500'
                                : 'bg-duo-red border-duo-red-dark hover:bg-red-500'
                                }`}
                        >
                            {index < total - 1 ? 'Continuar' : 'Ver Nota'}
                        </button>
                    </div>
                </div>
            </div >
        </>
    );
};

export default QuestionCard;
