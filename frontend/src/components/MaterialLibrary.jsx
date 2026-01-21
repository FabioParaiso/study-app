import React from 'react';
import { Book, CheckCircle, Clock } from 'lucide-react';

const MaterialLibrary = ({ materials, onActivate, currentId }) => {
    if (!materials || materials.length === 0) return null;

    return (
        <div className="bg-white rounded-2xl border-2 border-gray-200 p-6">
            <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-6 flex items-center gap-2">
                <Book size={16} />
                Biblioteca de Estudo
            </h3>

            <div className="space-y-3 max-h-60 overflow-y-auto pr-2 custom-scrollbar">
                {materials.map((m) => {
                    const isActive = m.id === currentId;
                    return (
                        <button
                            key={m.id}
                            onClick={() => !isActive && onActivate(m.id)}
                            disabled={isActive}
                            className={`w-full text-left p-3 rounded-xl border-2 transition-all flex items-center justify-between group
                                ${isActive
                                    ? 'bg-blue-50 border-blue-200 cursor-default'
                                    : 'bg-white border-gray-100 hover:border-blue-300 hover:shadow-sm'
                                }
                            `}
                        >
                            <div className="flex-1 min-w-0 mr-3">
                                <div className={`font-bold truncate ${isActive ? 'text-blue-600' : 'text-gray-700 group-hover:text-blue-500'}`}>
                                    {m.source}
                                </div>
                                <div className="text-xs text-gray-400 flex items-center gap-1 mt-1">
                                    <Clock size={12} />
                                    <span>{new Date(m.created_at).toLocaleDateString()}</span>
                                    <span className="mx-1">•</span>
                                    <span>{m.total_xp || 0} XP</span>
                                </div>
                            </div>

                            {isActive && (
                                <div className="text-blue-500">
                                    <CheckCircle size={20} />
                                </div>
                            )}
                        </button>
                    );
                })}
            </div>
        </div>
    );
};

export default MaterialLibrary;
