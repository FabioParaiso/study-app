import { useState } from 'react';
import { Book, CheckCircle, Clock, Trash2 } from 'lucide-react';
import Modal from './UI/Modal';

const MaterialLibrary = ({ materials, onActivate, onDelete, currentId }) => {
    const [deleteId, setDeleteId] = useState(null);

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
                        <div
                            key={m.id}
                            onClick={() => !isActive && onActivate(m.id)}
                            className={`w-full text-left p-3 rounded-xl border-2 transition-all flex items-center justify-between group relative
                                ${isActive
                                    ? 'bg-blue-50 border-blue-200 cursor-default'
                                    : 'bg-white border-gray-100 hover:border-blue-300 hover:shadow-sm cursor-pointer'
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

                            <div className="flex items-center gap-2">
                                {/* Activate Check */}
                                {isActive && (
                                    <div className="text-blue-500">
                                        <CheckCircle size={20} />
                                    </div>
                                )}

                                <button
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        setDeleteId(m.id);
                                    }}
                                    className={`p-2 rounded-lg text-gray-300 hover:text-red-500 hover:bg-red-50 transition-all z-10 ${isActive ? 'opacity-100' : 'opacity-0 group-hover:opacity-100'}`}
                                    title="Remover ficheiro"
                                >
                                    <Trash2 size={18} />
                                </button>
                            </div>
                        </div>
                    );
                })}
            </div>

            <Modal
                isOpen={!!deleteId}
                onClose={() => setDeleteId(null)}
                title="Apagar Material"
            >
                <div className="space-y-6">
                    <p className="text-gray-600 text-lg">
                        Tens a certeza que queres eliminar este ficheiro? <br />
                        <span className="text-red-500 font-bold text-sm">⚠️ Todo o progresso e XP associados serão perdidos para sempre.</span>
                    </p>

                    <div className="flex gap-3 justify-end">
                        <button
                            onClick={() => setDeleteId(null)}
                            className="px-5 py-2.5 rounded-xl font-bold text-gray-500 hover:bg-gray-100 transition-colors"
                        >
                            Cancelar
                        </button>
                        <button
                            onClick={() => {
                                onDelete(deleteId);
                                setDeleteId(null);
                            }}
                            className="px-5 py-2.5 rounded-xl font-bold bg-red-500 text-white hover:bg-red-600 shadow-lg hover:shadow-xl transition-all active:scale-95 flex items-center gap-2"
                        >
                            <Trash2 size={18} />
                            Apagar
                        </button>
                    </div>
                </div>
            </Modal>
        </div>
    );
};

export default MaterialLibrary;
