import React from 'react';
import { useAnalytics } from '../hooks/useAnalytics';
import { TrendingUp, AlertTriangle, CheckCircle } from 'lucide-react';

const WeakPointsPanel = ({ studentId, onTrain, materialId }) => {
    // We pass materialId to force re-fetch when it changes
    const { points, loading } = useAnalytics(studentId, materialId);

    if (loading) return <div className="animate-pulse h-20 bg-gray-100 rounded-xl"></div>;
    if (points.length === 0) return null;

    return (
        <div className="bg-white rounded-2xl border-2 border-gray-200 p-6">
            <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-6 flex items-center gap-2">
                <TrendingUp size={16} />
                As tuas Stats
            </h3>

            <div className="space-y-5">
                {points.map((p, i) => {
                    const isWeak = p.success_rate < 50;
                    const isGreat = p.success_rate >= 80;
                    const colorClass = isWeak ? 'bg-duo-red' : isGreat ? 'bg-duo-green' : 'bg-duo-blue';
                    const textColorClass = isWeak ? 'text-duo-red-dark' : isGreat ? 'text-duo-green-dark' : 'text-duo-blue-dark';

                    return (
                        <div key={i} className="space-y-1.5">
                            <div className="flex justify-between items-end">
                                <span className="font-bold text-gray-700 text-sm">{p.topic}</span>
                                <span className={`text-xs font-black ${textColorClass}`}>
                                    {p.success_rate}%
                                </span>
                            </div>
                            <div className="h-3 w-full bg-gray-100 rounded-full border-b border-white shadow-inner relative overflow-hidden">
                                <div
                                    className={`h-full ${colorClass} transition-all duration-500 rounded-full`}
                                    style={{ width: `${p.success_rate}%` }}
                                >
                                    {/* Subtle shine effect on progress bar */}
                                    <div className="absolute top-0 left-0 right-0 h-1/3 bg-white/20"></div>
                                </div>
                            </div>
                        </div>
                    );
                })}
            </div>

            {points.some(p => p.success_rate < 60) ? (
                <div className="mt-6 bg-red-50 border border-red-100 rounded-xl p-4 flex gap-3 text-sm text-red-800">
                    <AlertTriangle className="shrink-0 mt-0.5 text-duo-red" size={18} />
                    <div>
                        <p className="font-bold">O sistema detetou pontos fracos!</p>
                        <p className="text-red-600/80 mt-1">
                            Não te preocupes. O próximo quiz vai <b>automaticamente</b> incluir perguntas sobre estes temas para te ajudar a subir a nota. 💪
                        </p>
                    </div>
                </div>
            ) : (
                <div className="mt-6 bg-green-50 border border-green-100 rounded-xl p-4 flex gap-3 text-sm text-green-800">
                    <CheckCircle className="shrink-0 mt-0.5 text-duo-green" size={18} />
                    <div>
                        <p className="font-bold">Estás em grande!</p>
                        <p className="text-green-600/80 mt-1">
                            Continua assim para desbloqueares mais níveis. 🚀
                        </p>
                    </div>
                </div>
            )}
        </div>
    );
};

export default WeakPointsPanel;
