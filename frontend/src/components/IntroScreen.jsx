import React from 'react';
import { Trophy } from 'lucide-react';
import WeakPointsPanel from './WeakPointsPanel';
import IntroHeader from './Intro/IntroHeader';
import UploadSection from './Intro/UploadSection';
import MaterialDashboard from './Intro/MaterialDashboard';

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
            <IntroHeader
                student={student}
                selectedAvatar={selectedAvatar}
                changeAvatar={changeAvatar}
                totalXP={totalXP}
                onLogout={onLogout}
                level={level}
            />

            <main className="flex-1 max-w-5xl mx-auto w-full p-4 md:p-8 grid grid-cols-1 md:grid-cols-3 gap-8">
                {/* Main Content Area (2 cols) */}
                <div className="md:col-span-2 space-y-8">
                    {!savedMaterial ? (
                        <UploadSection
                            file={file}
                            handleFileChange={handleFileChange}
                            analyzeFile={analyzeFile}
                            isAnalyzing={isAnalyzing}
                            DuoButton={DuoButton}
                        />
                    ) : (
                        <MaterialDashboard
                            savedMaterial={savedMaterial}
                            availableTopics={availableTopics}
                            selectedTopic={selectedTopic}
                            setSelectedTopic={setSelectedTopic}
                            clearMaterial={clearMaterial}
                            startQuiz={startQuiz}
                            loading={loading}
                        />
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
                            <div
                                className="bg-yellow-400 h-full rounded-full transition-all duration-500"
                                style={{ width: `${nextLevel ? Math.max(0, Math.min(100, ((totalXP - level.min) / (nextLevel.min - level.min)) * 100)) : 100}%` }}
                            ></div>
                        </div>
                        <p className="mt-2 font-bold text-yellow-500">{totalXP} XP</p>
                    </div>
                </div>
            </main>
        </div>
    );
};

export default IntroScreen;
