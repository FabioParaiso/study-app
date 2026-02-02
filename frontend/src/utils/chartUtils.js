/**
 * Calculates the pixel height for a bar in a bar chart.
 * Returns 0 if the value is 0, otherwise ensures a minimum height of 2px.
 *
 * @param {number} value - The value to represent.
 * @param {number} maxValue - The maximum value in the dataset (for scaling).
 * @param {number} chartHeight - The total height of the chart in pixels.
 * @returns {number} The bar height in pixels.
 */
export const calcBarHeight = (value, maxValue, chartHeight) => {
    if (!value || value <= 0) return 0;
    const safeMax = Math.max(1, maxValue);
    const heightPct = Math.round((value / safeMax) * 100);
    return Math.max(2, Math.round((heightPct / 100) * chartHeight));
};

/**
 * Formats seconds to minutes (rounded).
 * @param {number} seconds - The value in seconds.
 * @returns {number} The value in minutes.
 */
export const formatMinutes = (seconds) => Math.round((seconds || 0) / 60);

/**
 * Formats an ISO date string (YYYY-MM-DD) to DD/MM format.
 * @param {string} isoDay - ISO date string.
 * @returns {string} Formatted date.
 */
export const formatDayLabel = (isoDay) => {
    if (!isoDay) return '';
    const parts = isoDay.split('-');
    if (parts.length !== 3) return isoDay;
    return `${parts[2]}/${parts[1]}`;
};

/**
 * Formats an ISO date string (YYYY-MM-DD) to DD/MM/YYYY format.
 * @param {string} isoDay - ISO date string.
 * @returns {string} Formatted date.
 */
export const formatDayTitle = (isoDay) => {
    if (!isoDay) return '';
    const parts = isoDay.split('-');
    if (parts.length !== 3) return isoDay;
    return `${parts[2]}/${parts[1]}/${parts[0]}`;
};

/**
 * Builds SVG path strings for a line chart from an array of values.
 * Handles null/undefined values by creating separate path segments.
 *
 * @param {Array<number|null>} values - Values to plot (0-100 scale).
 * @param {number} width - Chart width in pixels.
 * @param {number} height - Chart height in pixels.
 * @param {number} padding - Padding around the chart area.
 * @returns {string[]} Array of SVG path d-attribute strings.
 */
export const buildLinePaths = (values, width, height, padding = 8) => {
    if (!values || values.length === 0) return [];
    const usableWidth = Math.max(1, width - padding * 2);
    const usableHeight = Math.max(1, height - padding * 2);
    const step = values.length > 1 ? usableWidth / (values.length - 1) : 0;
    const paths = [];
    let current = [];

    values.forEach((val, idx) => {
        if (val === null || val === undefined) {
            if (current.length > 0) {
                paths.push(current);
                current = [];
            }
            return;
        }
        const x = padding + step * idx;
        const y = padding + (1 - Math.max(0, Math.min(100, val)) / 100) * usableHeight;
        current.push({ x, y });
    });

    if (current.length > 0) {
        paths.push(current);
    }

    return paths.map((segment) => segment.map((point, idx) => `${idx === 0 ? 'M' : 'L'} ${point.x} ${point.y}`).join(' '));
};
