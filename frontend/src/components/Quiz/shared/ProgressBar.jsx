import React from 'react';

/**
 * Barra de progresso reutilizável para Quiz.
 * @param {number} current - Índice atual (0-based)
 * @param {number} total - Total de itens
 * @param {string} color - Cor Tailwind da barra (default: 'bg-duo-green')
 */
const ProgressBar = ({ current, total, color = 'bg-duo-green' }) => {
    const percentage = ((current + 1) / total) * 100;

    return (
        <div className="w-full h-4 bg-gray-200 rounded-full mb-8 relative overflow-hidden">
            <div
                className={`h-full ${color} transition-all duration-500 rounded-full`}
                style={{ width: `${percentage}%` }}
            >
                <div className="absolute top-1 left-2 w-full h-1 bg-white opacity-20 rounded-full"></div>
            </div>
        </div>
    );
};

export default ProgressBar;
