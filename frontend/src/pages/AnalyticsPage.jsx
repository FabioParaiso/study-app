import React, { useEffect, useMemo, useState, useRef, useLayoutEffect } from 'react';
import { ArrowLeft, BarChart3, Clock, CheckCircle2, Layers } from 'lucide-react';
import IntroHeader from '../components/Intro/IntroHeader';
import { studyService } from '../services/studyService';

const TYPE_LABELS = {
    'multiple-choice': 'Iniciante',
    'short_answer': 'Intermedio',
    'open-ended': 'Avancado'
};

const TYPE_COLORS = {
    'multiple-choice': 'bg-green-500',
    'short_answer': 'bg-yellow-500',
    'open-ended': 'bg-purple-500'
};

const CHART_HEIGHT_PX = 120;
const TOOLTIP_OFFSET_PX = 8;
const TOOLTIP_EDGE_PADDING = 8;

const formatMinutes = (seconds) => Math.round((seconds || 0) / 60);

const formatDayLabel = (isoDay) => {
    if (!isoDay) return '';
    const parts = isoDay.split('-');
    if (parts.length !== 3) return isoDay;
    return `${parts[2]}/${parts[1]}`;
};

const formatDayTitle = (isoDay) => {
    if (!isoDay) return '';
    const parts = isoDay.split('-');
    if (parts.length !== 3) return isoDay;
    return `${parts[2]}/${parts[1]}/${parts[0]}`;
};

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

const FloatingTooltip = ({ anchorRef, text, visible }) => {
    const tooltipRef = useRef(null);
    const [style, setStyle] = useState({ left: 0, top: 0, placement: "top" });

    useLayoutEffect(() => {
        if (!visible) return;

        const updatePosition = () => {
            if (!anchorRef.current || !tooltipRef.current) return;
            const anchorRect = anchorRef.current.getBoundingClientRect();
            const tooltipRect = tooltipRef.current.getBoundingClientRect();

            let top = anchorRect.top - tooltipRect.height - TOOLTIP_OFFSET_PX;
            let placement = "top";
            if (top < TOOLTIP_EDGE_PADDING) {
                top = anchorRect.bottom + TOOLTIP_OFFSET_PX;
                placement = "bottom";
            }

            const centerX = anchorRect.left + anchorRect.width / 2;
            let left = centerX - tooltipRect.width / 2;
            const maxLeft = window.innerWidth - tooltipRect.width - TOOLTIP_EDGE_PADDING;
            left = Math.max(TOOLTIP_EDGE_PADDING, Math.min(left, maxLeft));

            setStyle({ left, top, placement });
        };

        const frameId = requestAnimationFrame(updatePosition);
        window.addEventListener('resize', updatePosition);
        window.addEventListener('scroll', updatePosition, true);

        return () => {
            cancelAnimationFrame(frameId);
            window.removeEventListener('resize', updatePosition);
            window.removeEventListener('scroll', updatePosition, true);
        };
    }, [visible, text, anchorRef]);

    return (
        <div
            ref={tooltipRef}
            role="tooltip"
            aria-hidden={!visible}
            className={`pointer-events-none fixed z-50 rounded-xl bg-white text-gray-700 text-[10px] font-bold px-2.5 py-1.5 border border-gray-200 shadow-md max-w-[220px] whitespace-normal text-center transition-opacity ${visible ? 'opacity-100' : 'opacity-0'}`}
            style={{ left: style.left, top: style.top }}
        >
            {text}
            <span
                className={`absolute left-1/2 -translate-x-1/2 w-0 h-0 border-4 border-transparent ${style.placement === "top" ? "top-full border-t-white" : "bottom-full border-b-white"}`}
            ></span>
        </div>
    );
};

const TooltipTarget = ({ text, enabled = true, children }) => {
    const anchorRef = useRef(null);
    const [visible, setVisible] = useState(false);

    const show = () => setVisible(true);
    const hide = () => setVisible(false);

    return (
        <div
            ref={anchorRef}
            className="relative flex flex-col items-center"
            onMouseEnter={show}
            onMouseLeave={hide}
            onFocus={show}
            onBlur={hide}
            tabIndex={enabled ? 0 : -1}
            aria-label={text}
        >
            {children}
            {enabled && <FloatingTooltip anchorRef={anchorRef} text={text} visible={visible} />}
        </div>
    );
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
    const [metrics, setMetrics] = useState(null);
    const [loading, setLoading] = useState(true);
    const [errorMsg, setErrorMsg] = useState('');

    useEffect(() => {
        let cancelled = false;
        const tzOffset = -new Date().getTimezoneOffset();

        setLoading(true);
        setErrorMsg('');

        studyService.getMetrics(30, tzOffset)
            .then((data) => {
                if (!cancelled) {
                    setMetrics(data);
                }
            })
            .catch(() => {
                if (!cancelled) {
                    setErrorMsg('Nao foi possivel carregar as metricas.');
                }
            })
            .finally(() => {
                if (!cancelled) {
                    setLoading(false);
                }
            });

        return () => {
            cancelled = true;
        };
    }, []);

    const { daily, totals } = useMemo(() => {
        if (!metrics) {
            return { daily: [], totals: null };
        }
        return {
            daily: metrics.daily || [],
            totals: metrics.totals || null
        };
    }, [metrics]);

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
                            <div className="bg-white rounded-2xl border-2 border-gray-200 p-6 flex items-center gap-4">
                                <div className="w-12 h-12 rounded-xl bg-duo-green text-white flex items-center justify-center">
                                    <Clock size={22} />
                                </div>
                                <div>
                                    <p className="text-xs font-bold text-gray-400 uppercase tracking-widest">Tempo ativo (30 dias)</p>
                                    <p className="text-2xl font-black text-gray-700">{totalActiveMinutes} min</p>
                                </div>
                            </div>
                            <div className="bg-white rounded-2xl border-2 border-gray-200 p-6 flex items-center gap-4">
                                <div className="w-12 h-12 rounded-xl bg-duo-blue text-white flex items-center justify-center">
                                    <Layers size={22} />
                                </div>
                                <div>
                                    <p className="text-xs font-bold text-gray-400 uppercase tracking-widest">Media diaria</p>
                                    <p className="text-2xl font-black text-gray-700">{avgActiveMinutes} min</p>
                                </div>
                            </div>
                            <div className="bg-white rounded-2xl border-2 border-gray-200 p-6 flex items-center gap-4">
                                <div className="w-12 h-12 rounded-xl bg-yellow-400 text-yellow-900 flex items-center justify-center">
                                    <CheckCircle2 size={22} />
                                </div>
                                <div>
                                    <p className="text-xs font-bold text-gray-400 uppercase tracking-widest">Dias &gt;= 30 min</p>
                                    <p className="text-2xl font-black text-gray-700">{daysWithGoal}/30</p>
                                </div>
                            </div>
                        </div>

                        <div className="bg-white rounded-2xl border-2 border-gray-200 p-6 space-y-4">
                            <div className="flex items-center justify-between">
                                <div>
                                    <h3 className="font-black text-gray-700 uppercase tracking-wide text-sm">Tempo ativo por dia</h3>
                                    <p className="text-xs text-gray-400 font-bold uppercase tracking-widest">Minutos ativos</p>
                                </div>
                                <div className="text-xs font-bold text-gray-400">Max: {formatMinutes(maxActive)} min</div>
                            </div>
                            <div className="overflow-x-auto overflow-y-visible">
                                <div className="flex items-end justify-end gap-2 min-w-[720px] h-44">
                                    {daily.map((day, idx) => {
                                        const heightPct = Math.round(((day.active_seconds || 0) / maxActive) * 100);
                                        const barHeight = (day.active_seconds || 0) > 0
                                            ? Math.max(2, Math.round((heightPct / 100) * CHART_HEIGHT_PX))
                                            : 0;
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
                                                <span className={`text-[10px] font-bold ${idx % 5 === 0 ? 'text-gray-400' : 'text-transparent'}`}>{formatDayLabel(day.day)}</span>
                                            </div>
                                        );
                                    })}
                                </div>
                            </div>
                        </div>

                        <div className="bg-white rounded-2xl border-2 border-gray-200 p-6 space-y-4">
                            <div className="flex items-center justify-between">
                                <div>
                                    <h3 className="font-black text-gray-700 uppercase tracking-wide text-sm">Testes por tipo (dia)</h3>
                                    <p className="text-xs text-gray-400 font-bold uppercase tracking-widest">Breakdown por nivel</p>
                                </div>
                                <div className="flex items-center gap-3 text-xs font-bold text-gray-400">
                                    {Object.keys(TYPE_LABELS).map((type) => (
                                        <div key={type} className="flex items-center gap-1">
                                            <span className={`w-2 h-2 rounded-full ${TYPE_COLORS[type]}`}></span>
                                            <span>{TYPE_LABELS[type]}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                            <div className="overflow-x-auto overflow-y-visible">
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
                                                                const heightPct = Math.round((count / maxTests) * 100);
                                                                const segmentHeight = count > 0
                                                                    ? Math.max(2, Math.round((heightPct / 100) * CHART_HEIGHT_PX))
                                                                    : 0;
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
                                                <span className={`text-[10px] font-bold ${idx % 5 === 0 ? 'text-gray-400' : 'text-transparent'}`}>{formatDayLabel(day.day)}</span>
                                            </div>
                                        );
                                    })}
                                </div>
                            </div>
                        </div>
                    </>
                )}
            </main>
        </div>
    );
};

export default AnalyticsPage;
