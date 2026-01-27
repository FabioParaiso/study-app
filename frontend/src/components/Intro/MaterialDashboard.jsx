import React from 'react';
import { BookOpen, XCircle, Trophy, PenTool, Lock } from 'lucide-react';
import WeakPointsPanel from '../WeakPointsPanel';

const MaterialDashboard = ({
    savedMaterial,
    availableTopics,
    selectedTopic,
    setSelectedTopic,
    clearMaterial,
    startQuiz,
    loading,
    studentId
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
                        <p className="text-xs uppercase font-bold text-duo-green tracking-wider">Matéria Atual</p>
                    </div>
                </div>
                <button
                    onClick={clearMaterial}
                    className="text-gray-400 hover:text-duo-red-dark transition-colors"
                    aria-label="Remover matéria"
                    title="Remover matéria"
                >
                    <XCircle size={28} />
                </button>
            </div>

            {/* Filters */}
            {availableTopics.length > 0 && (
                <div className="space-y-3">
                    <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider">Tópicos</h3>
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

            {/* Mastery / Weak Points */}
            <WeakPointsPanel
                key={savedMaterial?.id}
                studentId={studentId}
                materialId={savedMaterial?.id}
            />

            {/* Level Selection - Locked Progression */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* Beginner Level - Always Unlocked */}
                <button
                    onClick={() => startQuiz('multiple-choice')}
                    disabled={loading}
                    className="group relative bg-white rounded-2xl border-2 border-gray-200 border-b-4 hover:border-green-500 hover:bg-green-50 active:border-b-2 active:translate-y-1 transition-all p-6 flex flex-col items-center gap-4 h-full"
                >
                    <div className="w-20 h-20 rounded-2xl bg-green-500 text-white flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform">
                        <Trophy size={40} strokeWidth={2.5} />
                    </div>
                    <div className="text-center">
                        <h3 className="font-black text-gray-700 text-lg uppercase tracking-wide group-hover:text-green-600">Iniciante</h3>
                        <p className="text-gray-400 text-sm font-medium mt-1">Quiz Rápido</p>
                    </div>
                </button>

                {/* Intermediate Level - Requires 300 XP */}
                {savedMaterial.total_xp >= 300 ? (
                    <button
                        onClick={() => startQuiz('short_answer')}
                        disabled={loading}
                        className="group relative bg-white rounded-2xl border-2 border-gray-200 border-b-4 hover:border-yellow-500 hover:bg-yellow-50 active:border-b-2 active:translate-y-1 transition-all p-6 flex flex-col items-center gap-4 h-full"
                    >
                        <div className="w-20 h-20 rounded-2xl bg-yellow-500 text-white flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform">
                            <BookOpen size={40} strokeWidth={2.5} />
                        </div>
                        <div className="text-center">
                            <h3 className="font-black text-gray-700 text-lg uppercase tracking-wide group-hover:text-yellow-600">Intermédio</h3>
                            <p className="text-gray-400 text-sm font-medium mt-1">Frases Simples</p>
                        </div>
                    </button>
                ) : (
                    <div className="relative bg-gray-100 rounded-2xl border-2 border-gray-200 p-6 flex flex-col items-center gap-4 h-full opacity-75 cursor-not-allowed">
                        {/* Lock Overlay */}
                        <div className="w-20 h-20 rounded-2xl bg-gray-300 text-gray-500 flex items-center justify-center shadow-inner">
                            <Lock size={40} strokeWidth={2.5} />
                        </div>
                        <div className="text-center w-full">
                            <h3 className="font-black text-gray-400 text-lg uppercase tracking-wide">Intermédio</h3>
                            <div className="mt-2 w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-300">
                                <div className="bg-yellow-500 h-2.5 rounded-full transition-all" style={{ width: `${Math.min((savedMaterial.total_xp / 300) * 100, 100)}%` }}></div>
                            </div>
                            <p className="text-gray-400 text-xs font-bold mt-1 uppercase">{savedMaterial.total_xp}/300 XP para desbloquear</p>
                        </div>
                    </div>
                )}

                {/* Advanced Level - Requires 900 XP */}
                {savedMaterial.total_xp >= 900 ? (
                    <button
                        onClick={() => startQuiz('open-ended')}
                        disabled={loading}
                        className="group relative bg-white rounded-2xl border-2 border-gray-200 border-b-4 hover:border-purple-600 hover:bg-purple-50 active:border-b-2 active:translate-y-1 transition-all p-6 flex flex-col items-center gap-4 h-full"
                    >
                        <div className="w-20 h-20 rounded-2xl bg-purple-600 text-white flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform">
                            <PenTool size={40} strokeWidth={2.5} />
                        </div>
                        <div className="text-center">
                            <h3 className="font-black text-gray-700 text-lg uppercase tracking-wide group-hover:text-purple-700">Avançado</h3>
                            <p className="text-gray-400 text-sm font-medium mt-1">Escrita Livre</p>
                        </div>
                    </button>
                ) : (
                    <div className="relative bg-gray-100 rounded-2xl border-2 border-gray-200 p-6 flex flex-col items-center gap-4 h-full opacity-75 cursor-not-allowed">
                        {/* Lock Overlay */}
                        <div className="w-20 h-20 rounded-2xl bg-gray-300 text-gray-500 flex items-center justify-center shadow-inner">
                            <Lock size={40} strokeWidth={2.5} />
                        </div>
                        <div className="text-center w-full">
                            <h3 className="font-black text-gray-400 text-lg uppercase tracking-wide">Avançado</h3>
                            <div className="mt-2 w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-300">
                                <div className="bg-purple-500 h-2.5 rounded-full transition-all" style={{ width: `${Math.min((savedMaterial.total_xp / 900) * 100, 100)}%` }}></div>
                            </div>
                            <p className="text-gray-400 text-xs font-bold mt-1 uppercase">{savedMaterial.total_xp}/900 XP para desbloquear</p>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default MaterialDashboard;
