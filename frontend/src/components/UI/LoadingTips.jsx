import React, { useState, useEffect } from 'react';

const TIPS = [
    "A IA está a ler e a aprender o teu documento... 🧠",
    "Sabias que 20 minutos de estudo focado valem por 1 hora distraída? 🕒",
    "A preparar perguntas para te desafiar... ⚡",
    "Dica: Tenta explicar a matéria a alguém para aprenderes melhor! 🗣️",
    "Quase pronto! A organizar os tópicos... 📚",
    "A gerar quizzes personalizados para ti... 🚀",
    "Respira fundo. Estudar é uma maratona, não um sprint. 🏃"
];

const LoadingTips = () => {
    const [tipIndex, setTipIndex] = useState(0);

    useEffect(() => {
        const interval = setInterval(() => {
            setTipIndex((prev) => (prev + 1) % TIPS.length);
        }, 3000);
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="mt-6 p-4 bg-blue-50 border-2 border-blue-100 rounded-xl animate-fade-in w-full max-w-sm mx-auto">
            <h4 className="text-xs font-bold text-blue-400 uppercase tracking-wider mb-2 text-center">Enquanto esperamos...</h4>
            <p key={tipIndex} className="text-blue-800 text-sm font-medium text-center animate-slide-up">
                {TIPS[tipIndex]}
            </p>
        </div>
    );
};

export default LoadingTips;
