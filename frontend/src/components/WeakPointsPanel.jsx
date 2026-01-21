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

            {points.some(p => p.success_rate < 60) && (
                <button
                    onClick={() => onTrain(points.filter(p => p.success_rate < 60).map(p => p.topic))}
                    className="mt-8 w-full py-3 px-6 rounded-xl border-b-4 font-bold uppercase tracking-wider transition-all active:border-b-0 active:translate-y-1 flex items-center justify-center gap-2 bg-duo-red border-duo-red-dark text-white hover:brightness-110"
                >
                    <AlertTriangle size={18} />
                    Melhorar Pontos Fracos
                </button>
            )}

            <div className="mt-4 pt-4 border-t border-gray-100 text-xs text-center text-gray-400">
                Melhora os tópicos a vermelho para evoluíres! 🚀
            </div>
        </div>
    );
};

export default WeakPointsPanel;
