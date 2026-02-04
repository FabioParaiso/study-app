import React from 'react';

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

const LINE_COLORS = {
    'multiple-choice': '#22c55e',
    'short_answer': '#eab308',
    'open-ended': '#a855f7'
};

const LEVEL_SHORT = {
    'multiple-choice': 'I',
    'short_answer': 'M',
    'open-ended': 'A'
};

/**
 * Legend component showing coloured dots with labels for each quiz type.
 * @param {boolean} useLine - If true, uses hex colours; otherwise uses Tailwind bg classes.
 */
const ChartLegend = ({ useLine = false }) => (
    <div className="flex items-center gap-3 text-xs font-bold text-gray-400">
        {Object.keys(TYPE_LABELS).map((type) => (
            <div key={type} className="flex items-center gap-1">
                <span
                    className={`w-2 h-2 rounded-full ${useLine ? '' : TYPE_COLORS[type]}`}
                    style={useLine ? { backgroundColor: LINE_COLORS[type] } : undefined}
                />
                <span>{TYPE_LABELS[type]}</span>
            </div>
        ))}
    </div>
);

/**
 * X-axis label for chart bars. Shows label every 5th item for readability.
 * @param {number} idx - Current index in the data array.
 * @param {string} label - The label text to display.
 * @param {boolean} center - Whether to center the text.
 * @param {string} className - Optional extra classnames.
 * @param {object} style - Optional inline styles.
 */
const AxisLabel = ({ idx, label, center = false, className = '', style }) => (
    <span
        style={style}
        className={`text-[10px] font-bold ${center ? 'text-center' : ''} ${idx % 5 === 0 ? 'text-gray-400' : 'text-transparent'} ${className}`}
    >
        {label}
    </span>
);

/**
 * Wrapper component for chart sections in the Analytics Dashboard.
 * Provides consistent styling for title, subtitle, legend, and scrollable content.
 */
const ChartSection = ({ title, subtitle, showLegend = false, useLine = false, rightContent, children, contentRef }) => (
    <div className="bg-white rounded-2xl border-2 border-gray-200 p-6 space-y-4">
        <div className="flex items-center justify-between">
            <div>
                <h3 className="font-black text-gray-700 uppercase tracking-wide text-sm">{title}</h3>
                <p className="text-xs text-gray-400 font-bold uppercase tracking-widest">{subtitle}</p>
            </div>
            {showLegend && <ChartLegend useLine={useLine} />}
            {rightContent}
        </div>
        <div className="overflow-x-hidden overflow-y-visible" ref={contentRef}>
            {children}
        </div>
    </div>
);

export { ChartSection, ChartLegend, AxisLabel, TYPE_LABELS, TYPE_COLORS, LINE_COLORS, LEVEL_SHORT };
export default ChartSection;
