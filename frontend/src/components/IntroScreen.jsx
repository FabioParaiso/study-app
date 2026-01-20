import React from 'react';
import { BookOpen, Trophy, XCircle, Filter, RefreshCw, AlertCircle, ChevronRight, PenTool, Upload, FileText, ArrowRight } from 'lucide-react';
import WeakPointsPanel from './WeakPointsPanel';

const IntroScreen = ({
    student, onLogout,
    file, handleFileChange, analyzeFile, isAnalyzing, savedMaterial, clearMaterial,
    availableTopics, selectedTopic, setSelectedTopic, detectTopics, errorMsg, loading, startQuiz,
    changeAvatar, selectedAvatar, level, totalXP, highScore, nextLevel, LEVELS
}) => {

    // Duolingo-style Button Component
    const DuoButton = ({ children, onClick, variant = 'primary', disabled, className = '', ...props }) => {
        const variants = {
            primary: 'bg-duo-green border-duo-green-dark text-white hover:bg-[#61E002]',
            secondary: 'bg-duo-blue border-duo-blue-dark text-white hover:bg-[#20BEF5]',
            danger: 'bg-duo-red border-duo-red-dark text-white hover:bg-[#FF5C5C]',
            outline: 'bg-white border-gray-200 text-gray-500 hover:bg-gray-50 border-b-2 active:border-b-2', // Less 3D
            disabled: 'bg-gray-200 border-gray-300 text-gray-400 cursor-not-allowed border-b-0 translate-y-1'
        };

        const style = disabled ? variants.disabled : variants[variant];

        return (
            <button
                onClick={onClick}
                disabled={disabled}
                className={`w-full py-3 px-6 rounded-2xl border-b-4 font-bold uppercase tracking-wider transition-all active:border-b-0 active:translate-y-1 flex items-center justify-center gap-2 ${style} ${className}`}
                {...props}
            >
                {children}
            </button>
        );
    };

    return (
        <div className="min-h-screen bg-gray-50 flex flex-col font-sans text-gray-800">
            {/* Top Bar */}
            <header className="bg-white border-b-2 border-gray-200 sticky top-0 z-10">
                <div className="max-w-5xl mx-auto px-4 h-16 flex justify-between items-center">
                    <div className="flex items-center gap-4">
                        <button
                            onClick={() => changeAvatar(selectedAvatar === '👩‍🎓' ? '🧑‍🎓' : '👩‍🎓')}
                            className="bg-gray-100 hover:bg-gray-200 p-2 rounded-xl border-b-4 border-gray-200 active:border-b-0 active:translate-y-1 transition-all"
                        >
                            <span className="text-2xl">{selectedAvatar}</span>
                        </button>
                        <div>
                            <h1 className="font-bold text-gray-700 text-lg uppercase tracking-wide">
                                {student.name}
                            </h1>
                            <p className="text-xs font-bold text-gray-400 uppercase">
                                {level.emoji} {level.title}
                            </p>
                        </div>
                    </div>

                    <div className="flex items-center gap-4">
                        <div className="flex items-center gap-2">
                            <img src="https://d35aaqx5ub95lt.cloudfront.net/images/icons/398e4298a3b39ce566050e5c041949ef.svg" className="w-6 h-6" alt="gem" />
                            <span className="font-bold text-duo-red text-lg">{totalXP} XP</span>
                        </div>
                        <button
                            onClick={onLogout}
                            className="text-xs font-bold text-duo-gray-dark hover:text-duo-red uppercase tracking-wider px-3 py-1 hover:bg-gray-100 rounded-lg transition-colors"
                        >
                            Sair
                        </button>
                    </div>
                </div>
            </header>

            <main className="flex-1 max-w-5xl mx-auto w-full p-4 md:p-8 grid grid-cols-1 md:grid-cols-3 gap-8">
                {/* Main Content Area (2 cols) */}
                <div className="md:col-span-2 space-y-8">

                    {/* Upload Section */}
                    {!savedMaterial ? (
                        <div className="bg-white rounded-2xl p-8 border-2 border-gray-200 text-center">
                            <div className="w-24 h-24 bg-gray-100 rounded-full mx-auto mb-6 flex items-center justify-center text-gray-400">
                                <Upload size={40} />
                            </div>
                            <h2 className="text-2xl font-bold text-gray-700 mb-2">Carregar Apontamentos</h2>
                            <p className="text-gray-500 mb-8 max-w-sm mx-auto">
                                Faz upload de um PDF ou TXT e a IA vai criar testes personalizados para ti.
                            </p>

                            <div className="relative inline-block w-full max-w-xs">
                                <input
                                    type="file"
                                    accept=".pdf,.txt"
                                    onChange={handleFileChange}
                                    className="hidden"
                                    id="file-upload"
                                />
                                <label htmlFor="file-upload">
                                    <div className="bg-white border-2 border-duo-blue border-b-4 text-duo-blue font-bold py-3 px-6 rounded-2xl uppercase tracking-wider cursor-pointer hover:bg-blue-50 active:border-b-2 active:translate-y-1 transition-all mb-4 block">
                                        {file ? `Selecionado: ${file.name}` : "Escolher Ficheiro"}
                                    </div>
                                </label>
                            </div>

                            <DuoButton
                                onClick={analyzeFile}
                                disabled={!file || isAnalyzing}
                                className="max-w-xs mx-auto"
                            >
                                {isAnalyzing ? <RefreshCw className="animate-spin" /> : "COMEÇAR A ESTUDAR"}
                            </DuoButton>
                        </div>
                    ) : (
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
                    )}
                </div>

                {/* Sidebar (Right) */}
                <div className="space-y-6">
                    <div className="bg-white rounded-2xl border-2 border-gray-200 p-6">
                        <h3 className="font-bold text-lg text-gray-700 mb-4 uppercase tracking-wide border-b-2 border-gray-100 pb-2">O teu Progresso</h3>
                        <WeakPointsPanel studentId={student.id} />
                    </div>

                    <div className="bg-white rounded-2xl border-2 border-gray-200 p-6 flex flex-col items-center text-center">
                        <div className="w-20 h-20 bg-yellow-100 rounded-full flex items-center justify-center mb-4 text-yellow-500">
                            <Trophy size={40} />
                        </div>
                        <h3 className="font-bold text-gray-700 text-xl">Nível {LEVELS.indexOf(level) + 1}</h3>
                        <p className="text-gray-400 font-bold uppercase text-xs mb-4">{level.title}</p>
                        <div className="w-full bg-gray-200 rounded-full h-4 relative overflow-hidden">
                            <div className="bg-yellow-400 h-full rounded-full w-3/4"></div>
                        </div>
                        <p className="mt-2 font-bold text-yellow-500">{totalXP} XP</p>
                    </div>
                </div>
            </main>
        </div>
    );
};

export default IntroScreen;
