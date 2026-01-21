import React, { useState } from 'react';
import { Send, Volume2, StopCircle, CheckCircle, XCircle } from 'lucide-react';

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

    // Derived state for styling
    const isCorrect = evaluation?.is_correct;

    return (
        <>
            {/* Main Card */}
            <div className="w-full max-w-2xl mx-auto animate-fade-in mb-32">
                {/* Progress Bar */}
                <div className="w-full h-4 bg-gray-200 rounded-full mb-8 relative overflow-hidden">
                    <div
                        className="h-full bg-duo-green transition-all duration-500 rounded-full"
                        style={{ width: `${((index + 1) / total) * 100}%` }}
                    >
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
                            ? 'bg-duo-blue text-white border-duo-blue-dark'
                            : 'bg-white text-duo-blue border-gray-200 hover:bg-gray-50'
                            }`}
                    >
                        {speakingPart === 'question' ? <StopCircle size={24} /> : <Volume2 size={24} />}
                    </button>
                </div>

                {/* Input Area */}
                <div className="w-full">
                    <input
                        type="text"
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
                className={`fixed bottom-0 left-0 w-full transform transition-transform duration-300 ease-out z-50 ${submitted ? 'translate-y-0' : 'translate-y-0' // Always visible when submitted, but we handle "Submit" button state below
                    }`}
            >
                <div className={`p-6 pb-8 border-t-2 ${evaluation
                    ? (isCorrect ? 'bg-green-100 border-transparent' : 'bg-red-50 border-transparent')
                    : 'bg-white border-gray-200'
                    }`}>
                    <div className="max-w-2xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">

                        {/* Feedback Content (Only if evaluated) */}
                        {evaluation ? (
                            <div className="flex-1 flex items-start gap-4 w-full">
                                <div className={`p-2 rounded-full hidden md:block ${isCorrect ? 'bg-white text-duo-green' : 'bg-white text-duo-red'}`}>
                                    {isCorrect ? <CheckCircle size={32} /> : <XCircle size={32} />}
                                </div>
                                <div className="w-full">
                                    <h3 className={`font-bold text-xl mb-1 ${isCorrect ? 'text-duo-green-dark' : 'text-duo-red-dark'}`}>
                                        {isCorrect
                                            ? ["Fantástico! 🎉", "Muito bem! 🌟", "Acertaste! 💪"][Math.floor(Math.random() * 3)]
                                            : "Fica a saber que: 🧠"}
                                    </h3>
                                    <p className={`text-lg font-medium leading-relaxed ${isCorrect ? 'text-green-700' : 'text-red-700'}`}>
                                        {evaluation.feedback}
                                    </p>
                                </div>
                            </div>
                        ) : (
                            // Empty spacer when just showing the submit button
                            <div className="hidden md:block flex-1"></div>
                        )}

                        {/* Action Button */}
                        <button
                            onClick={submitted ? onNext : handleSubmit}
                            disabled={!submitted && userText.trim().length === 0}
                            className={`w-full md:w-auto px-10 py-4 rounded-2xl border-b-4 font-bold text-white uppercase tracking-wider transition-all active:border-b-0 active:translate-y-1 text-center flex items-center justify-center gap-2 ${!submitted
                                ? (userText.trim().length === 0
                                    ? 'bg-gray-300 border-gray-400 cursor-not-allowed text-gray-500'
                                    : 'bg-duo-green border-duo-green-dark hover:bg-green-500')
                                : (isCorrect
                                    ? 'bg-duo-green border-duo-green-dark hover:bg-green-500'
                                    : 'bg-duo-red border-duo-red-dark hover:bg-red-500')
                                }`}
                        >
                            {submitted ? (
                                index < total - 1 ? 'Continuar' : 'Ver Nota'
                            ) : (
                                <>VERIFICAR <Send size={20} className="ml-2" /></>
                            )}
                        </button>
                    </div>
                </div>
            </div>
        </>
    );
};

export default ShortAnswerCard;
