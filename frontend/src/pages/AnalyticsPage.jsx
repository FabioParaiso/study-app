import { useMemo } from 'react';
import { ArrowLeft, BarChart3, Clock, Layers } from 'lucide-react';
import IntroHeader from '../components/Intro/IntroHeader';
import MetricCard from '../components/Analytics/MetricCard';
import { ChartSection, TYPE_LABELS, TYPE_COLORS, LINE_COLORS, LEVEL_SHORT, AxisLabel } from '../components/Analytics/ChartSection';
import { TooltipTarget } from '../components/common/Tooltip';
import { calcBarHeight, formatMinutes, formatDayLabel, formatDayTitle, buildLinePaths } from '../utils/chartUtils';
import { useAsyncData } from '../hooks/useAsyncData';
import { studyService } from '../services/studyService';

const CHART_HEIGHT_PX = 120;
const LINE_CHART_HEIGHT_PX = 140;

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
    xpLabel,
    xpValue,
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

    const learningDailyRaw = useMemo(() => {
        if (!learningTrend) return [];
        return learningTrend.daily || [];
    }, [learningTrend]);

    const chartDays = useMemo(() => {
        const candidates = [];
        if (daily.length > 0) {
            candidates.push(daily[0].day, daily[daily.length - 1].day);
        }
        if (learningDailyRaw.length > 0) {
            candidates.push(learningDailyRaw[0].day, learningDailyRaw[learningDailyRaw.length - 1].day);
        }
        if (candidates.length === 0) return [];

        const parseIso = (iso) => {
            const [year, month, day] = iso.split('-').map(Number);
            return new Date(Date.UTC(year, month - 1, day));
        };
        const formatIso = (date) => date.toISOString().slice(0, 10);

        const start = parseIso(candidates.reduce((min, cur) => (cur < min ? cur : min)));
        const end = parseIso(candidates.reduce((max, cur) => (cur > max ? cur : max)));

        const days = [];
        for (let ts = start.getTime(); ts <= end.getTime(); ts += 24 * 60 * 60 * 1000) {
            days.push(formatIso(new Date(ts)));
        }
        return days;
    }, [daily, learningDailyRaw]);

    const dailyAligned = useMemo(() => {
        if (chartDays.length === 0) return [];
        const baseByType = Object.keys(TYPE_LABELS).reduce((acc, type) => {
            acc[type] = 0;
            return acc;
        }, {});
        const byDay = new Map(daily.map((day) => [day.day, day]));
        return chartDays.map((day) => {
            const entry = byDay.get(day);
            if (entry) return entry;
            return {
                day,
                active_seconds: 0,
                duration_seconds: 0,
                tests_total: 0,
                by_type: { ...baseByType }
            };
        });
    }, [chartDays, daily]);

    const learningDaily = useMemo(() => {
        if (learningDailyRaw.length === 0) return [];
        if (chartDays.length === 0) return learningDailyRaw;
        const byDay = new Map(learningDailyRaw.map((day) => [day.day, day]));
        return chartDays.map((day) => byDay.get(day) || { day, by_level: {} });
    }, [learningDailyRaw, chartDays]);

    const learningColumnWidth = useMemo(() => {
        if (learningDaily.length === 0) return 0;
        return 100 / learningDaily.length;
    }, [learningDaily]);

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
        if (dailyAligned.length === 0) return 1;
        return Math.max(1, ...dailyAligned.map((d) => d.active_seconds || 0));
    }, [dailyAligned]);

    const maxTests = useMemo(() => {
        if (dailyAligned.length === 0) return 1;
        return Math.max(1, ...dailyAligned.map((d) => d.tests_total || 0));
    }, [dailyAligned]);

    const totalActiveMinutes = totals ? formatMinutes(totals.active_seconds) : 0;
    const avgActiveMinutes = totals ? formatMinutes((totals.active_seconds || 0) / 30) : 0;
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
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
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
                            {!trendLoading && !trendError && learningDailyRaw.length === 0 && (
                                <div className="text-center text-gray-400 text-sm font-semibold py-10">
                                    Sem dados suficientes.
                                </div>
                            )}
                            {!trendLoading && !trendError && learningDaily.length > 0 && (
                                <div className="w-full">
                                    <div className="relative w-full" style={{ height: `${LINE_CHART_HEIGHT_PX}px` }}>
                                        <svg
                                            viewBox={`0 0 100 ${LINE_CHART_HEIGHT_PX}`}
                                            preserveAspectRatio="none"
                                            className="absolute inset-0 w-full h-full"
                                        >
                                            <line x1="0" y1={LINE_CHART_HEIGHT_PX} x2="100" y2={LINE_CHART_HEIGHT_PX} stroke="#e5e7eb" strokeWidth="1" vectorEffect="non-scaling-stroke" />
                                            {[25, 50, 75].map((tick) => {
                                                const y = (1 - tick / 100) * LINE_CHART_HEIGHT_PX;
                                                return (
                                                    <line key={tick} x1="0" y1={y} x2="100" y2={y} stroke="#f3f4f6" strokeWidth="1" vectorEffect="non-scaling-stroke" />
                                                );
                                            })}
                                            {Object.keys(TYPE_LABELS).map((type) => {
                                                const paths = buildLinePaths(learningValues[type], 100, LINE_CHART_HEIGHT_PX, learningColumnWidth / 2);
                                                return paths.map((path, idx) => (
                                                    <path
                                                        key={`${type}-${idx}`}
                                                        d={path}
                                                        fill="none"
                                                        stroke={LINE_COLORS[type]}
                                                        strokeWidth="2.5"
                                                        strokeLinecap="round"
                                                        strokeLinejoin="round"
                                                        vectorEffect="non-scaling-stroke"
                                                    />
                                                ));
                                            })}
                                        </svg>
                                        <div className="absolute inset-0 flex z-10">
                                            {learningDaily.map((day) => {
                                                const hasData = day.by_level && Object.values(day.by_level).some(l => l.value !== null && l.value > 0);
                                                return (
                                                    <div key={day.day} className="flex-1 h-full">
                                                        <TooltipTarget text={formatLearningTooltip(day)} enabled={hasData}>
                                                            <div
                                                                className={`w-full transition-colors ${hasData ? 'hover:bg-duo-blue/10' : ''}`}
                                                                style={{ height: `${LINE_CHART_HEIGHT_PX}px` }}
                                                            />
                                                        </TooltipTarget>
                                                    </div>
                                                );
                                            })}
                                        </div>
                                    </div>
                                    <div className="flex mt-2">
                                        {learningDaily.map((day, idx) => (
                                            <AxisLabel
                                                key={day.day}
                                                idx={idx}
                                                label={formatDayLabel(day.day)}
                                                center
                                                className="flex-1"
                                            />
                                        ))}
                                    </div>
                                </div>
                            )}
                        </ChartSection>

                        <ChartSection
                            title="Tempo ativo por dia"
                            subtitle="Minutos ativos"
                            rightContent={<div className="text-xs font-bold text-gray-400">Max: {formatMinutes(maxActive)} min</div>}
                        >
                            <div className="flex items-end h-44">
                                {dailyAligned.map((day, idx) => {
                                    const barHeight = calcBarHeight(day.active_seconds, maxActive, CHART_HEIGHT_PX);
                                    const title = formatActiveTooltip(day);
                                    const enabled = (day.active_seconds || 0) > 0;
                                    return (
                                        <div key={day.day} className="flex-1 min-w-0 flex flex-col items-center gap-2 px-1">
                                            <TooltipTarget text={title} enabled={enabled}>
                                                <div
                                                    className="w-3 bg-duo-blue rounded-t"
                                                    style={{ height: `${barHeight}px` }}
                                                ></div>
                                            </TooltipTarget>
                                            <AxisLabel idx={idx} label={formatDayLabel(day.day)} center className="w-full" />
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
                            <div className="flex items-end h-44">
                                {dailyAligned.map((day, idx) => {
                                    const byType = day.by_type || {};
                                    const title = formatTestsTooltip(day, byType);
                                    const enabled = (day.tests_total || 0) > 0;
                                    return (
                                        <div key={day.day} className="flex-1 min-w-0 flex flex-col items-center gap-2 px-1">
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
                                            <AxisLabel idx={idx} label={formatDayLabel(day.day)} center className="w-full" />
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
