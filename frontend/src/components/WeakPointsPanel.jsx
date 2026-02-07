import { useState, useMemo } from 'react';
import { TrendingUp, ChevronDown, ChevronUp, BookOpen, Trophy, PenTool } from 'lucide-react';

/**
 * Get color classes based on PERFORMANCE only.
 */
const getPerformanceColors = (scoreData) => {
    if (!scoreData) return { bg: 'bg-gray-100', text: 'text-gray-400', border: 'border-gray-200' };

    const level = scoreData.confidence_level;

    if (level === 'not_seen') {
        return { bg: 'bg-gray-100', text: 'text-gray-400', border: 'border-gray-200' };
    }
    if (level === 'exploring') {
        return { bg: 'bg-blue-100', text: 'text-blue-600', border: 'border-blue-200' };
    }

    const score = scoreData.score || 0;
    if (score >= 0.8) {
        return { bg: 'bg-green-100', text: 'text-green-700', border: 'border-green-200' };
    }
    if (score >= 0.65) {
        return { bg: 'bg-yellow-100', text: 'text-yellow-700', border: 'border-yellow-200' };
    }
    return { bg: 'bg-red-100', text: 'text-red-600', border: 'border-red-200' };
};

/**
 * Custom Tooltip - positioned to the left to avoid overflow
 */
const Tooltip = ({ children, content }) => {
    const [show, setShow] = useState(false);

    return (
        <div
            className="relative inline-block"
            onMouseEnter={() => setShow(true)}
            onMouseLeave={() => setShow(false)}
        >
            {children}
            {show && content && (
                <div className="absolute bottom-full right-0 mb-2 z-50 pointer-events-none">
                    <div className="bg-gray-900 text-white text-xs rounded-lg py-1.5 px-2.5 whitespace-nowrap shadow-lg">
                        {content}
                    </div>
                </div>
            )}
        </div>
    );
};

/**
 * Score badge: Icon = quiz type, Color = performance
 * Tooltip shows only the status label (not redundant info)
 */
const ScoreBadge = ({ scoreData, icon: Icon }) => {
    const colors = getPerformanceColors(scoreData);
    const displayValue = scoreData?.display_value || '--';
    const statusLabel = scoreData?.status_label || 'Não Visto';

    return (
        <Tooltip content={statusLabel}>
            <div
                className={`flex items-center justify-center gap-1.5 px-2 py-1.5 rounded-lg border w-20 transition-all duration-300 cursor-default ${colors.bg} ${colors.text} ${colors.border}`}
            >
                <Icon size={13} strokeWidth={3} />
                <span className="font-bold">{displayValue}</span>
            </div>
        </Tooltip>
    );
};

const WeakPointsPanel = ({ points = [], loading = false }) => {
    const [expandedTopics, setExpandedTopics] = useState({});

    const safePoints = useMemo(() => {
        return Array.isArray(points) ? points : [];
    }, [points]);

    const toggleTopic = (topic) => {
        setExpandedTopics(prev => ({ ...prev, [topic]: !prev[topic] }));
    };

    const groupedPoints = useMemo(() => {
        if (!safePoints.length) return {};
        const groups = {};
        safePoints.forEach(p => {
            const topic = p.topic || "Geral";
            if (!groups[topic]) groups[topic] = [];
            groups[topic].push(p);
        });
        return groups;
    }, [safePoints]);

    if (loading) return <div className="animate-pulse h-20 bg-gray-100 rounded-xl"></div>;
    if (safePoints.length === 0) return null;

    return (
        <div className="bg-white rounded-2xl border-2 border-gray-200 p-6">
            <div className="mb-6">
                <h3 className="text-sm font-bold text-gray-400 uppercase tracking-wider flex items-center gap-2">
                    <TrendingUp size={16} />
                    O teu Domínio
                </h3>
                <p className="text-xs text-gray-400 font-medium mt-1">
                    Baseado nas últimas 7 respostas por conceito.
                </p>
            </div>

            <div className="space-y-4">
                {Object.entries(groupedPoints).map(([topic, concepts]) => {
                    const isExpanded = expandedTopics[topic] !== false;

                    return (
                        <div key={topic} className="border border-gray-100 rounded-xl overflow-hidden">
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

                            {isExpanded && (
                                <div className="p-4 bg-white space-y-4">
                                    {concepts.map((p, i) => (
                                        <div key={i} className="py-3 border-b border-gray-50 last:border-0 flex justify-between items-center gap-4">
                                            <span className="font-semibold text-gray-700 text-sm truncate" title={p.concept}>{p.concept}</span>

                                            <div className="flex items-center gap-2 text-xs shrink-0">
                                                <ScoreBadge scoreData={p.score_data_mcq} icon={Trophy} />
                                                <ScoreBadge scoreData={p.score_data_short} icon={BookOpen} />
                                                <ScoreBadge scoreData={p.score_data_bloom} icon={PenTool} />
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    );
                })}
            </div>
        </div>
    );
};

export default WeakPointsPanel;
