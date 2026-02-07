import { Trophy, BarChart3 } from 'lucide-react';
import IntroHeader from '../components/Intro/IntroHeader';
import UploadSection from '../components/Intro/UploadSection';
import MaterialDashboard from '../components/Intro/MaterialDashboard';
import MaterialLibrary from '../components/MaterialLibrary';
import WeeklyChallengeCard from '../components/Challenge/WeeklyChallengeCard';

const IntroScreen = ({
    student, onLogout,
    file, handleFileChange, analyzeFile, isAnalyzing, savedMaterial, clearMaterial,
    availableTopics, selectedTopic, setSelectedTopic, loading, startQuiz,
    changeAvatar, selectedAvatar, level, totalXP, nextLevel, LEVELS,
    materialsList, activateMaterial, onDeleteMaterial, onOpenAnalytics,
    xpLabel, xpValue,
    isChallengeEnabled, challengeStatus, challengeLoading, challengeError
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
                xpLabel={xpLabel}
                xpValue={xpValue}
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
                            studentId={student.id}
                        />
                    )}
                </div>

                {/* Sidebar (Right) */}
                <div className="space-y-6">
                    {isChallengeEnabled && (
                        <WeeklyChallengeCard
                            status={challengeStatus}
                            loading={challengeLoading}
                            error={challengeError}
                        />
                    )}

                    {/* Analytics */}
                    <div className="bg-white rounded-2xl border-2 border-gray-200 p-6 flex flex-col gap-4">
                        <div className="flex items-center gap-3">
                            <div className="w-12 h-12 bg-duo-blue text-white rounded-xl flex items-center justify-center">
                                <BarChart3 size={22} />
                            </div>
                            <div>
                                <h3 className="font-bold text-gray-700 text-lg uppercase tracking-wide">Metricas</h3>
                                <p className="text-xs uppercase font-bold text-gray-400 tracking-widest">Ultimos 30 dias</p>
                            </div>
                        </div>
                        <button
                            onClick={onOpenAnalytics}
                            className="w-full py-3 px-6 rounded-2xl border-b-4 font-bold uppercase tracking-wider transition-all active:border-b-0 active:translate-y-1 flex items-center justify-center gap-2 bg-duo-blue border-duo-blue-dark text-white hover:bg-[#20BEF5]"
                        >
                            Ver dashboard
                        </button>
                    </div>

                    {/* Library (Navigation) - Absolute top for maximum stability */}
                    <MaterialLibrary
                        materials={materialsList}
                        onActivate={activateMaterial}
                        onDelete={onDeleteMaterial}
                        currentId={savedMaterial?.id}
                    />

                    {/* Level & Stats Card */}
                    <div className="bg-white rounded-2xl border-2 border-gray-200 p-6 flex flex-col items-center text-center">
                        <div className="w-20 h-20 bg-yellow-100 rounded-full flex items-center justify-center mb-4 text-yellow-500 shadow-inner">
                            <Trophy size={40} />
                        </div>
                        <h3 className="font-bold text-gray-700 text-xl">Nível {LEVELS.indexOf(level) + 1}</h3>
                        <p className="text-gray-400 font-bold uppercase text-xs mb-4 tracking-widest">{level.title}</p>
                        <div className="w-full bg-gray-100 rounded-full h-4 border-b border-white shadow-inner relative overflow-hidden">
                            <div
                                className="bg-yellow-400 h-full rounded-full transition-all duration-700 ease-out"
                                style={{ width: `${nextLevel ? Math.max(0, Math.min(100, ((totalXP - level.min) / (nextLevel.min - level.min)) * 100)) : 100}%` }}
                            >
                                <div className="absolute top-0 left-0 right-0 h-1/3 bg-white/30"></div>
                            </div>
                        </div>
                        <p className="mt-3 font-black text-yellow-500 tracking-wider font-mono">{totalXP} XP</p>
                    </div>
                </div>
            </main>
        </div>
    );
};

export default IntroScreen;
