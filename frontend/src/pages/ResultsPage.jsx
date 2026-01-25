import React from 'react';
import { Award, RefreshCw, RotateCcw, CheckCircle, Flame } from 'lucide-react';
import Confetti from '../components/UI/Confetti';

const ResultsScreen = ({
    score, totalQuestions, xpEarned, streak, quizType,
    getOpenEndedAverage, exitQuiz, numMissed, onReview, onRestart
}) => {
    const isMultiple = quizType === 'multiple-choice';
    const finalScore = isMultiple ? Math.round((score / totalQuestions) * 100) : getOpenEndedAverage();

    // Determine status color and message
    let status = { color: 'text-duo-green', border: 'border-duo-green', bg: 'bg-green-50', message: "Incrível!" };
    if (finalScore < 50) status = { color: 'text-duo-red', border: 'border-duo-red', bg: 'bg-red-50', message: "Bom esforço!" };
    else if (finalScore < 80) status = { color: 'text-duo-blue', border: 'border-duo-blue', bg: 'bg-blue-50', message: "Muito bom!" };

    // Stop any TTS
    React.useEffect(() => {
        window.speechSynthesis.cancel();
    }, []);

    return (
        <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-6 font-sans">
            {finalScore >= 70 && <Confetti />}

            <div className="w-full max-w-md animate-scale-up space-y-6">
                {/* Score Card */}
                <div className="bg-white rounded-3xl border-2 border-gray-200 border-b-4 p-8 text-center relative overflow-hidden">
                    <div className="mb-6 relative inline-block">
                        <div className={`w-32 h-32 rounded-full border-4 ${status.border} flex items-center justify-center bg-white shadow-sm mx-auto`}>
                            <span className={`text-4xl font-black ${status.color}`}>{finalScore}%</span>
                        </div>
                        {streak > 1 && (
                            <div className="absolute -bottom-2 -right-2 bg-orange-500 text-white text-xs font-bold px-3 py-1 rounded-full border-2 border-white flex items-center gap-1">
                                <Flame size={14} fill="currentColor" /> {streak}
                            </div>
                        )}
                    </div>

                    <h2 className={`text-3xl font-black ${status.color} mb-2`}>{status.message}</h2>
                    <p className="text-gray-400 font-bold uppercase tracking-wider text-sm mb-8">
                        {isMultiple ? `Acertaste ${score} de ${totalQuestions}` : 'Pontuação Final'}
                    </p>

                    <div className="grid grid-cols-2 gap-4">
                        <div className="bg-yellow-50 border-2 border-yellow-200 rounded-2xl p-4">
                            <div className="flex items-center justify-center gap-2 mb-1">
                                <img src="https://d35aaqx5ub95lt.cloudfront.net/images/icons/398e4298a3b39ce566050e5c041949ef.svg" className="w-6 h-6" alt="gem" />
                                <span className="text-xl font-black text-yellow-600">+{xpEarned}</span>
                            </div>
                            <p className="text-xs uppercase font-bold text-yellow-600/60">XP Total</p>
                        </div>
                        <div className="bg-blue-50 border-2 border-blue-200 rounded-2xl p-4">
                            <div className="flex items-center justify-center gap-2 mb-1">
                                <CheckCircle className="text-duo-blue" size={24} />
                                <span className="text-xl font-black text-duo-blue">
                                    {finalScore >= 90 ? "Top" : finalScore >= 70 ? "Boa" : finalScore >= 50 ? "Média" : "Baixa"}
                                </span>
                            </div>
                            <p className="text-xs uppercase font-bold text-duo-blue/60">Precisão</p>
                        </div>
                    </div>
                </div>

                {/* Actions */}
                <div className="space-y-3">
                    {/* Review Mistakes Button */}
                    {numMissed > 0 && onReview && (
                        <button
                            onClick={onReview}
                            className="w-full bg-duo-red border-b-4 border-duo-red-dark hover:bg-[#FF5C5C] active:border-b-0 active:translate-y-1 text-white font-bold py-4 rounded-2xl uppercase tracking-wider transition-all flex items-center justify-center gap-3 text-lg"
                        >
                            <RotateCcw size={24} /> Rever {numMissed} Erros
                        </button>
                    )}

                    {/* Restart Button */}
                    <button
                        onClick={onRestart}
                        className="w-full bg-yellow-400 border-b-4 border-yellow-600 hover:bg-yellow-500 active:border-b-0 active:translate-y-1 text-white font-bold py-4 rounded-2xl uppercase tracking-wider transition-all flex items-center justify-center gap-3 text-lg"
                    >
                        <RefreshCw size={24} /> NOVO TESTE
                    </button>

                    <button
                        onClick={exitQuiz}
                        className="w-full bg-duo-green border-b-4 border-duo-green-dark hover:bg-[#61E002] active:border-b-0 active:translate-y-1 text-white font-bold py-4 rounded-2xl uppercase tracking-wider transition-all flex items-center justify-center gap-3 text-lg"
                    >
                        MENU PRINCIPAL
                    </button>
                </div>
            </div>
        </div>
    );
};

export default ResultsScreen;
