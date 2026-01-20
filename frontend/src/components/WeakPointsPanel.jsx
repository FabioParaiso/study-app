import React, { useEffect, useState } from 'react';
import { studyService } from '../services/studyService';
import { TrendingUp, AlertTriangle, CheckCircle } from 'lucide-react';

const WeakPointsPanel = ({ studentId }) => {
    const [points, setPoints] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (studentId) loadPoints();
    }, [studentId]);

    const loadPoints = async () => {
        try {
            const data = await studyService.getWeakPoints(studentId);
            setPoints(data);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <div className="animate-pulse h-20 bg-gray-100 rounded-xl"></div>;
    if (points.length === 0) return null;

    return (
        <div className="bg-white rounded-3xl shadow-lg p-6 border border-gray-100 mb-8">
            <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
                <TrendingUp className="text-indigo-500" size={20} /> O teu Progresso por Tópico
            </h3>

            <div className="space-y-4">
                {points.map((p, i) => {
                    const isWeak = p.success_rate < 50;
                    const isGreat = p.success_rate >= 80;
                    return (
                        <div key={i} className="flex items-center gap-3">
                            <div className="flex-1">
                                <div className="flex justify-between mb-1">
                                    <span className="text-sm font-bold text-gray-700">{p.topic}</span>
                                    <span className={`text-xs font-bold ${isWeak ? 'text-red-500' : isGreat ? 'text-green-500' : 'text-indigo-500'}`}>
                                        {p.success_rate}%
                                    </span>
                                </div>
                                <div className="h-2 w-full bg-gray-100 rounded-full overflow-hidden">
                                    <div
                                        className={`h-full ${isWeak ? 'bg-red-500' : isGreat ? 'bg-green-500' : 'bg-indigo-500'}`}
                                        style={{ width: `${p.success_rate}%` }}
                                    ></div>
                                </div>
                            </div>
                            {isWeak && <AlertTriangle className="text-red-400" size={16} />}
                            {isGreat && <CheckCircle className="text-green-400" size={16} />}
                        </div>
                    );
                })}
            </div>

            <div className="mt-4 pt-4 border-t border-gray-100 text-xs text-center text-gray-400">
                Foca-te nos tópicos a vermelho para subires de nível mais rápido! 🚀
            </div>
        </div>
    );
};

export default WeakPointsPanel;
