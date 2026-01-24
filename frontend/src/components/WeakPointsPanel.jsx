import React, { useState, useMemo } from 'react';
import { useAnalytics } from '../hooks/useAnalytics';
import { TrendingUp, AlertTriangle, CheckCircle, ChevronDown, ChevronUp, BookOpen } from 'lucide-react';

const WeakPointsPanel = ({ studentId, materialId }) => {
    const { points, loading } = useAnalytics(studentId, materialId);
    const [expandedTopics, setExpandedTopics] = useState({});

    // Toggle accordion
    const toggleTopic = (topic) => {
        setExpandedTopics(prev => ({ ...prev, [topic]: !prev[topic] }));
    };

    // Group points by Topic
    const groupedPoints = useMemo(() => {
        if (!points) return {};
        const groups = {};
        points.forEach(p => {
            const topic = p.topic || "Geral"; // Macro Topic
            if (!groups[topic]) groups[topic] = [];
            groups[topic].push(p);
        });
        return groups;
    }, [points]);

    // Set initial expanded state (expand all by default if few, or just first?)
    // Let's expand all by default for better visibility
    // useEffect to set defaults? Or just treat undefined as true?
    // Let's treat undefined as TRUE (expanded by default)

    if (loading) return <div className="animate-pulse h-20 bg-gray-100 rounded-xl"></div>;
    if (points.length === 0) return null;

    return (
        <div className="bg-white rounded-2xl border-2 border-gray-200 p-6">
            <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-6 flex items-center gap-2">
                <TrendingUp size={16} />
                O teu Domínio
            </h3>

            <div className="space-y-4">
                {Object.entries(groupedPoints).map(([topic, concepts]) => {
                    const isExpanded = expandedTopics[topic] !== false; // Default true

                    return (
                        <div key={topic} className="border border-gray-100 rounded-xl overflow-hidden">
                            {/* Topic Header */}
                            <button
                                onClick={() => toggleTopic(topic)}
                                className="w-full flex items-center justify-between p-4 bg-gray-50 hover:bg-gray-100 transition-colors"
                            >
                                <div className="flex items-center gap-3">
                                    <div className="p-2 bg-white rounded-lg border border-gray-200 text-duo-purple">
                                        <BookOpen size={16} />
                                    </div>
                                    <span className="font-bold text-gray-700 text-sm">{topic}</span>
                                    <span className="text-xs text-gray-400 font-medium">({concepts.length} conceitos)</span>
                                </div>
                                {isExpanded ? <ChevronUp size={16} className="text-gray-400" /> : <ChevronDown size={16} className="text-gray-400" />}
                            </button>

                            {/* Concepts List */}
                            {isExpanded && (
                                <div className="p-4 bg-white space-y-4">
                                    {concepts.map((p, i) => {
                                        const isWeak = p.success_rate < 50;
                                        const isGreat = p.success_rate >= 80;
                                        const colorClass = isWeak ? 'bg-duo-red' : isGreat ? 'bg-duo-green' : 'bg-duo-blue';
                                        const textColorClass = isWeak ? 'text-duo-red-dark' : isGreat ? 'text-duo-green-dark' : 'text-duo-blue-dark';

                                        return (
                                            <div key={i} className="space-y-1.5">
                                                <div className="flex justify-between items-end">
                                                    <span className="font-medium text-gray-600 text-xs pl-1">{p.concept}</span>
                                                    <span className={`text-xs font-black ${textColorClass}`}>
                                                        {p.success_rate}%
                                                    </span>
                                                </div>
                                                <div className="h-2 w-full bg-gray-100 rounded-full border-b border-white shadow-inner relative overflow-hidden">
                                                    <div
                                                        className={`h-full ${colorClass} transition-all duration-500 rounded-full`}
                                                        style={{ width: `${p.success_rate}%` }}
                                                    >
                                                        <div className="absolute top-0 left-0 right-0 h-1/3 bg-white/20"></div>
                                                    </div>
                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>

            {points.some(p => p.success_rate < 70) ? (
                <div className="mt-6 bg-red-50 border border-red-100 rounded-xl p-4 flex gap-3 text-sm text-red-800">
                    <AlertTriangle className="shrink-0 mt-0.5 text-duo-red" size={18} />
                    <div>
                        <p className="font-bold">Alguns conceitos precisam de atenção!</p>
                        <p className="text-red-600/80 mt-1 text-xs">
                            O próximo quiz vai identificar estes pontos automaticamente.
                        </p>
                    </div>
                </div>
            ) : (
                <div className="mt-6 bg-green-50 border border-green-100 rounded-xl p-4 flex gap-3 text-sm text-green-800">
                    <CheckCircle className="shrink-0 mt-0.5 text-duo-green" size={18} />
                    <div>
                        <p className="font-bold">Domínio Total!</p>
                        <p className="text-green-600/80 mt-1 text-xs">
                            Continua o bom trabalho.
                        </p>
                    </div>
                </div>
            )}
        </div>
    );
};

export default WeakPointsPanel;
