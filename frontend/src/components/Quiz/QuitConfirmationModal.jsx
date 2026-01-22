import React from 'react';
import { AlertTriangle } from 'lucide-react';

const QuitConfirmationModal = ({ isOpen, onClose, onConfirm }) => {
    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-6 bg-slate-900/40 backdrop-blur-sm animate-fade-in font-sans">
            <div className="bg-white rounded-[2rem] p-8 max-w-sm w-full shadow-2xl animate-bounce-in transform transition-all text-center border-b-8 border-gray-100">

                {/* Icon (Mascot-like Warning) */}
                <div className="flex justify-center mb-6">
                    <div className="bg-red-50 p-6 rounded-3xl animate-bounce-short border-4 border-red-100 transform -rotate-6">
                        <AlertTriangle size={64} className="text-red-500 drop-shadow-sm" strokeWidth={2.5} />
                    </div>
                </div>

                {/* Content */}
                <div className="mb-8">
                    <h3 className="text-3xl font-black text-gray-700 mb-4 uppercase tracking-wide">
                        Esperaaa!
                    </h3>
                    <p className="text-gray-500 font-bold text-lg leading-relaxed px-2">
                        Vais mesmo sair? Todo o teu progresso será perdido!
                    </p>
                </div>

                {/* Actions */}
                <div className="flex flex-col gap-4">
                    <button
                        onClick={onClose}
                        className="w-full py-4 rounded-2xl bg-blue-500 border-b-[6px] border-blue-700 text-white text-lg font-black uppercase tracking-widest hover:bg-blue-400 hover:border-blue-600 active:border-b-0 active:translate-y-[6px] transition-all shadow-blue-200 shadow-lg"
                    >
                        Quero Ficar
                    </button>

                    <button
                        onClick={onConfirm}
                        className="w-full py-4 rounded-2xl bg-transparent text-red-500 text-lg font-black uppercase tracking-widest hover:bg-red-50 transition-colors"
                    >
                        Sair
                    </button>
                </div>
            </div>
        </div>
    );
};

export default QuitConfirmationModal;
