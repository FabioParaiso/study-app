import React from 'react';
import { BookOpen, XCircle, RefreshCw, Trophy, PenTool } from 'lucide-react';

const MaterialDashboard = ({
    savedMaterial,
    availableTopics,
    selectedTopic,
    setSelectedTopic,
    clearMaterial,
    startQuiz,
    loading
}) => {
    return (
        <div className="space-y-6 animate-fade-in">
            {/* Active Material Card */}
            <div className="bg-white p-6 rounded-2xl border-2 border-gray-200 flex justify-between items-center">
                <div className="flex items-center gap-4">
                    <div className="bg-duo-green p-3 rounded-xl">
                        <BookOpen className="text-white" size={24} />
                    </div>
                    <div>
                        <p className="font-bold text-gray-700 text-lg">{savedMaterial.source}</p>
                        <p className="text-xs uppercase font-bold text-duo-green tracking-wider">Matéria Ativa</p>
                    </div>
                </div>
                <button onClick={clearMaterial} className="text-gray-400 hover:text-duo-red-dark transition-colors">
                    <XCircle size={28} />
                </button>
            </div>

            {/* Filters */}
            {availableTopics.length > 0 && (
                <div className="space-y-3">
                    <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider">Filtrar por Tópico</h3>
                    <div className="flex flex-wrap gap-2">
                        <button
                            onClick={() => setSelectedTopic('all')}
                            className={`px-4 py-2 rounded-xl font-bold uppercase text-sm border-b-4 transition-all active:border-b-0 active:translate-y-1 ${selectedTopic === 'all'
                                ? 'bg-duo-blue border-duo-blue-dark text-white'
                                : 'bg-white border-gray-200 text-gray-400 hover:bg-gray-50'
                                }`}
                        >
                            Todos
                        </button>
                        {availableTopics.map((t, i) => (
                            <button
                                key={i}
                                onClick={() => setSelectedTopic(t)}
                                className={`px-4 py-2 rounded-xl font-bold uppercase text-sm border-b-4 transition-all active:border-b-0 active:translate-y-1 ${selectedTopic === t
                                    ? 'bg-duo-blue border-duo-blue-dark text-white'
                                    : 'bg-white border-gray-200 text-gray-400 hover:bg-gray-50'
                                    }`}
                            >
                                {t}
                            </button>
                        ))}
                    </div>
                </div>
            )}

            {/* Quiz Modes */}
            <div className="grid gap-4">
                <button
                    onClick={() => startQuiz('multiple')}
                    disabled={loading}
                    className="bg-white border-2 border-gray-200 border-b-4 p-6 rounded-2xl flex items-center justify-between hover:bg-gray-50 active:border-b-2 active:translate-y-1 transition-all group"
                >
                    <div className="flex items-center gap-4">
                        <div className="w-16 h-16 bg-duo-green rounded-xl flex items-center justify-center text-white">
                            <Trophy size={32} />
                        </div>
                        <div className="text-left">
                            <h3 className="font-bold text-gray-700 text-xl">Modo Clássico</h3>
                            <p className="text-gray-400 font-medium">Perguntas de escolha múltipla</p>
                        </div>
                    </div>
                    {loading ? <RefreshCw className="animate-spin text-duo-gray-dark" /> : <div className="bg-duo-green text-white font-bold px-6 py-3 rounded-xl shadow-lg uppercase">Começar</div>}
                </button>

                <button
                    onClick={() => startQuiz('open-ended')}
                    disabled={loading}
                    className="bg-white border-2 border-gray-200 border-b-4 p-6 rounded-2xl flex items-center justify-between hover:bg-gray-50 active:border-b-2 active:translate-y-1 transition-all group"
                >
                    <div className="flex items-center gap-4">
                        <div className="w-16 h-16 bg-duo-blue rounded-xl flex items-center justify-center text-white">
                            <PenTool size={32} />
                        </div>
                        <div className="text-left">
                            <h3 className="font-bold text-gray-700 text-xl">Modo Escrita</h3>
                            <p className="text-gray-400 font-medium">Respostas abertas com avaliação</p>
                        </div>
                    </div>
                    <div className="bg-duo-blue text-white font-bold px-6 py-3 rounded-xl shadow-lg uppercase">Praticar</div>
                </button>
            </div>
        </div>
    );
};

export default MaterialDashboard;
