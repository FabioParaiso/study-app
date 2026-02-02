import React, { useMemo } from 'react';
import { ArrowLeft, BarChart3, Clock, CheckCircle2, Layers } from 'lucide-react';
import IntroHeader from '../components/Intro/IntroHeader';
import MetricCard from '../components/Analytics/MetricCard';
import { ChartSection, TYPE_LABELS, TYPE_COLORS, LINE_COLORS, LEVEL_SHORT, AxisLabel } from '../components/Analytics/ChartSection';
import { TooltipTarget } from '../components/common/Tooltip';
import { calcBarHeight, formatMinutes, formatDayLabel, formatDayTitle, buildLinePaths } from '../utils/chartUtils';
import { useAsyncData } from '../hooks/useAsyncData';
import { studyService } from '../services/studyService';

const CHART_HEIGHT_PX = 120;
const LINE_CHART_HEIGHT_PX = 140;
const LINE_CHART_MIN_WIDTH = 720;

const formatActiveTooltip = (day) => {
    const minutes = formatMinutes(day.active_seconds);
    const label = minutes === 1 ? "min ativo" : "min ativos";
    return `${formatDayTitle(day.day)} - ${minutes} ${label}`;
};

const formatTestsTooltip = (day, byType) => {
    const total = day.tests_total || 0;
    const label = total === 1 ? "teste" : "testes";
    const counts = `I${byType['multiple-choice'] || 0} M${byType['short_answer'] || 0} A${byType['open-ended'] || 0}`;
    return `${formatDayTitle(day.day)} - ${total} ${label} (${counts})`;
};

const formatLearningTooltip = (day) => {
    if (!day) return '';
    const byLevel = day.by_level || {};
    const parts = Object.keys(TYPE_LABELS).map((type) => {
        const entry = byLevel[type] || {};
        const value = entry.value;
        const questions = entry.questions || 0;
        const display = value === null || value === undefined ? "-" : `${value}%`;
        return `${LEVEL_SHORT[type]} ${display} (${questions})`;
    });
    return `${formatDayTitle(day.day)} - ${parts.join(" | ")}`;
};

const AnalyticsPage = ({
    student,
    selectedAvatar,
    changeAvatar,
    totalXP,
    onLogout,
    level,
    onBack
}) => {
    const tzOffset = useMemo(() => -new Date().getTimezoneOffset(), []);

    const {
        data: metrics,
        loading,
        error: errorMsg
    } = useAsyncData(
        () => studyService.getMetrics(30, tzOffset),
        [tzOffset],
        'Nao foi possivel carregar as metricas.'
    );

    const {
        data: learningTrend,
        loading: trendLoading,
        error: trendError
    } = useAsyncData(
        () => studyService.getLearningTrend(30, tzOffset, 1),
        [tzOffset],
        'Nao foi possivel carregar a evolucao.'
    );

    const { daily, totals } = useMemo(() => {
        if (!metrics) {
            return { daily: [], totals: null };
        }
        return {
            daily: metrics.daily || [],
            totals: metrics.totals || null
        };
    }, [metrics]);

    const learningDaily = useMemo(() => {
        if (!learningTrend) return [];
        return learningTrend.daily || [];
    }, [learningTrend]);

    const learningChartWidth = useMemo(() => {
        if (learningDaily.length === 0) return LINE_CHART_MIN_WIDTH;
        return Math.max(LINE_CHART_MIN_WIDTH, learningDaily.length * 24);
    }, [learningDaily]);

    const learningColumnWidth = useMemo(() => {
        if (learningDaily.length === 0) return LINE_CHART_MIN_WIDTH;
        return learningChartWidth / learningDaily.length;
    }, [learningDaily, learningChartWidth]);

    const learningValues = useMemo(() => {
        const values = {};
        Object.keys(TYPE_LABELS).forEach((type) => {
            values[type] = learningDaily.map((day) => {
                const entry = day.by_level?.[type];
                const value = entry?.value;
                return value === null || value === undefined ? null : value;
            });
        });
        return values;
    }, [learningDaily]);

    const maxActive = useMemo(() => {
        if (daily.length === 0) return 1;
        return Math.max(1, ...daily.map((d) => d.active_seconds || 0));
    }, [daily]);

    const maxTests = useMemo(() => {
        if (daily.length === 0) return 1;
        return Math.max(1, ...daily.map((d) => d.tests_total || 0));
    }, [daily]);

    const totalActiveMinutes = totals ? formatMinutes(totals.active_seconds) : 0;
    const avgActiveMinutes = totals ? formatMinutes((totals.active_seconds || 0) / 30) : 0;
    const daysWithGoal = totals ? totals.days_with_goal || 0 : 0;

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

            <main className="flex-1 max-w-5xl mx-auto w-full p-4 md:p-8 space-y-6">
                <div className="flex items-center gap-4">
                    <button
                        onClick={onBack}
                        className="flex items-center gap-2 text-sm font-bold text-gray-500 hover:text-gray-700 bg-white border-2 border-gray-200 rounded-xl px-4 py-2 transition-colors"
                    >
                        <ArrowLeft size={16} />
                        Voltar
                    </button>
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-duo-blue text-white rounded-xl flex items-center justify-center">
                            <BarChart3 size={20} />
                        </div>
                        <div>
                            <h2 className="font-black text-lg text-gray-700 uppercase tracking-wide">Dashboard de Metricas</h2>
                            <p className="text-xs text-gray-400 font-bold uppercase tracking-widest">Ultimos 30 dias</p>
                        </div>
                    </div>
                </div>

                {loading && (
                    <div className="bg-white rounded-2xl border-2 border-gray-200 p-6 text-center text-gray-500">
                        A carregar metricas...
                    </div>
                )}

                {!loading && errorMsg && (
                    <div className="bg-white rounded-2xl border-2 border-gray-200 p-6 text-center text-duo-red">
                        {errorMsg}
                    </div>
                )}

                {!loading && !errorMsg && (
                    <>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <MetricCard
                                icon={Clock}
                                iconBg="bg-duo-green"
                                label="Tempo ativo (30 dias)"
                                value={`${totalActiveMinutes} min`}
                            />
                            <MetricCard
                                icon={Layers}
                                iconBg="bg-duo-blue"
                                label="Media diaria"
                                value={`${avgActiveMinutes} min`}
                            />
                            <MetricCard
                                icon={CheckCircle2}
                                iconBg="bg-yellow-400"
                                iconTextColour="text-yellow-900"
                                label="Dias >= 30 min"
                                value={`${daysWithGoal}/30`}
                            />
                        </div>

                        <ChartSection
                            title="Domínio efetivo por nível"
                            subtitle="Média acumulada (dias com atividade)"
                            showLegend
                            useLine
                        >
                            {trendLoading && (
                                <div className="text-center text-gray-500 text-sm font-semibold py-10">
                                    A carregar evolução...
                                </div>
                            )}
                            {!trendLoading && trendError && (
                                <div className="text-center text-duo-red text-sm font-semibold py-10">
                                    {trendError}
                                </div>
                            )}
                            {!trendLoading && !trendError && learningDaily.length === 0 && (
                                <div className="text-center text-gray-400 text-sm font-semibold py-10">
                                    Sem dados suficientes.
                                </div>
                            )}
                            {!trendLoading && !trendError && learningDaily.length > 0 && (
                                <div className="min-w-[720px]" style={{ width: `${learningChartWidth}px` }}>
                                    <div className="relative" style={{ height: `${LINE_CHART_HEIGHT_PX}px` }}>
                                        <svg
                                            viewBox={`0 0 ${learningChartWidth} ${LINE_CHART_HEIGHT_PX}`}
                                            width={learningChartWidth}
                                            height={LINE_CHART_HEIGHT_PX}
                                            className="absolute inset-0"
                                        >
                                            <line x1="0" y1={LINE_CHART_HEIGHT_PX} x2={learningChartWidth} y2={LINE_CHART_HEIGHT_PX} stroke="#e5e7eb" strokeWidth="1" />
                                            {[25, 50, 75].map((tick) => {
                                                const y = (1 - tick / 100) * LINE_CHART_HEIGHT_PX;
                                                return (
                                                    <line key={tick} x1="0" y1={y} x2={learningChartWidth} y2={y} stroke="#f3f4f6" strokeWidth="1" />
                                                );
                                            })}
                                            {Object.keys(TYPE_LABELS).map((type) => {
                                                const paths = buildLinePaths(learningValues[type], learningChartWidth, LINE_CHART_HEIGHT_PX, learningColumnWidth / 2);
                                                return paths.map((path, idx) => (
                                                    <path
                                                        key={`${type}-${idx}`}
                                                        d={path}
                                                        fill="none"
                                                        stroke={LINE_COLORS[type]}
                                                        strokeWidth="2.5"
                                                        strokeLinecap="round"
                                                        strokeLinejoin="round"
                                                    />
                                                ));
                                            })}
                                        </svg>
                                        <div className="absolute inset-0 flex">
                                            {learningDaily.map((day) => (
                                                <TooltipTarget key={day.day} text={formatLearningTooltip(day)} enabled={true}>
                                                    <div style={{ width: `${learningColumnWidth}px`, height: `${LINE_CHART_HEIGHT_PX}px` }}></div>
                                                </TooltipTarget>
                                            ))}
                                        </div>
                                    </div>
                                    <div className="flex mt-2">
                                        {learningDaily.map((day, idx) => <AxisLabel key={day.day} idx={idx} label={formatDayLabel(day.day)} center style={{ width: `${learningColumnWidth}px` }} />
                                        )}
                                    </div>
                                </div>
                            )}
                        </ChartSection>

                        <ChartSection
                            title="Tempo ativo por dia"
                            subtitle="Minutos ativos"
                            rightContent={<div className="text-xs font-bold text-gray-400">Max: {formatMinutes(maxActive)} min</div>}
                        >
                            <div className="flex items-end justify-end gap-2 min-w-[720px] h-44">
                                {daily.map((day, idx) => {
                                    const barHeight = calcBarHeight(day.active_seconds, maxActive, CHART_HEIGHT_PX);
                                    const title = formatActiveTooltip(day);
                                    const enabled = (day.active_seconds || 0) > 0;
                                    return (
                                        <div key={day.day} className="flex flex-col items-center gap-2">
                                            <TooltipTarget text={title} enabled={enabled}>
                                                <div
                                                    className="w-3 bg-duo-blue rounded-t"
                                                    style={{ height: `${barHeight}px` }}
                                                ></div>
                                            </TooltipTarget>
                                            <AxisLabel idx={idx} label={formatDayLabel(day.day)} />
                                        </div>
                                    );
                                })}
                            </div>
                        </ChartSection>

                        <ChartSection
                            title="Testes por tipo (dia)"
                            subtitle="Breakdown por nivel"
                            showLegend
                        >
                            <div className="flex items-end justify-end gap-2 min-w-[720px] h-44">
                                {daily.map((day, idx) => {
                                    const byType = day.by_type || {};
                                    const title = formatTestsTooltip(day, byType);
                                    const enabled = (day.tests_total || 0) > 0;
                                    return (
                                        <div key={day.day} className="flex flex-col items-center gap-2">
                                            <TooltipTarget text={title} enabled={enabled}>
                                                <div className="relative w-3" style={{ height: `${CHART_HEIGHT_PX}px` }}>
                                                    <div className="absolute inset-0 flex flex-col justify-end rounded-t overflow-hidden border border-transparent">
                                                        {Object.keys(TYPE_LABELS).map((type) => {
                                                            const count = byType[type] || 0;
                                                            const segmentHeight = calcBarHeight(count, maxTests, CHART_HEIGHT_PX);
                                                            return (
                                                                <div
                                                                    key={type}
                                                                    className={`${TYPE_COLORS[type]} w-full`}
                                                                    style={{ height: `${segmentHeight}px` }}
                                                                ></div>
                                                            );
                                                        })}
                                                    </div>
                                                </div>
                                            </TooltipTarget>
                                            <AxisLabel idx={idx} label={formatDayLabel(day.day)} />
                                        </div>
                                    );
                                })}
                            </div>
                        </ChartSection>
                    </>
                )}
            </main>
        </div>
    );
};

export default AnalyticsPage;
