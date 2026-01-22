import React from 'react';
import { Volume2, StopCircle } from 'lucide-react';

/**
 * Cabeçalho de pergunta reutilizável com tópico, texto e botão TTS.
 * @param {string} topic - Nome do tópico
 * @param {string} question - Texto da pergunta
 * @param {function} onSpeak - Callback para TTS
 * @param {boolean} isSpeaking - Se está a falar atualmente
 * @param {string} accentColor - Cor de destaque ('blue' | 'purple')
 */
const QuestionHeader = ({
    topic,
    question,
    onSpeak,
    isSpeaking = false,
    accentColor = 'blue'
}) => {
    const colorMap = {
        blue: {
            active: 'bg-duo-blue text-white border-duo-blue-dark',
            inactive: 'bg-white text-duo-blue border-gray-200 hover:bg-gray-50'
        },
        purple: {
            active: 'bg-purple-500 text-white border-purple-700',
            inactive: 'bg-white text-purple-500 border-gray-200 hover:bg-purple-50'
        }
    };

    const colors = colorMap[accentColor] || colorMap.blue;

    return (
        <div className="flex items-start gap-4 mb-8">
            <div className="flex-1">
                <span className="inline-block bg-blue-100 text-blue-600 text-xs font-bold px-3 py-1 rounded-lg mb-3 tracking-widest uppercase">
                    {topic}
                </span>
                <h2 className="text-2xl md:text-3xl font-bold text-gray-700 leading-tight">
                    {question}
                </h2>
            </div>
            <button
                onClick={() => onSpeak(question, 'question')}
                className={`p-3 rounded-2xl border-b-4 transition-all active:border-b-0 active:translate-y-1 ${isSpeaking ? colors.active : colors.inactive
                    }`}
            >
                {isSpeaking ? <StopCircle size={24} /> : <Volume2 size={24} />}
            </button>
        </div>
    );
};

export default QuestionHeader;
