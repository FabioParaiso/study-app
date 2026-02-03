import { describe, it, expect } from 'vitest';
import { calcBarHeight, formatMinutes, formatDayLabel, formatDayTitle, buildLinePaths } from './chartUtils';

describe('chartUtils', () => {
    describe('calcBarHeight', () => {
        it('returns 0 for zero or negative values', () => {
            expect(calcBarHeight(0, 100, 120)).toBe(0);
            expect(calcBarHeight(-5, 100, 120)).toBe(0);
            expect(calcBarHeight(null, 100, 120)).toBe(0);
            expect(calcBarHeight(undefined, 100, 120)).toBe(0);
        });

        it('calculates height proportionally to max value', () => {
            // 50% of max should be roughly 50% of chart height
            const height = calcBarHeight(50, 100, 120);
            expect(height).toBeGreaterThan(50);
            expect(height).toBeLessThanOrEqual(60);
        });

        it('returns at least 2px for small positive values', () => {
            expect(calcBarHeight(1, 1000, 120)).toBeGreaterThanOrEqual(2);
        });

        it('handles max value of 0 gracefully (uses safeMax of 1)', () => {
            // When maxValue is 0, safeMax becomes 1, so value 10 gives 1000%
            // This is an edge case that shouldn't occur in practice
            expect(calcBarHeight(10, 0, 120)).toBeGreaterThan(0);
        });
    });

    describe('formatMinutes', () => {
        it('converts seconds to rounded minutes', () => {
            expect(formatMinutes(60)).toBe(1);
            expect(formatMinutes(90)).toBe(2); // rounds up
            expect(formatMinutes(59)).toBe(1); // rounds to nearest
            expect(formatMinutes(120)).toBe(2);
        });

        it('handles zero and null gracefully', () => {
            expect(formatMinutes(0)).toBe(0);
            expect(formatMinutes(null)).toBe(0);
            expect(formatMinutes(undefined)).toBe(0);
        });
    });

    describe('formatDayLabel', () => {
        it('formats ISO date to DD/MM', () => {
            expect(formatDayLabel('2026-01-15')).toBe('15/01');
            expect(formatDayLabel('2026-12-31')).toBe('31/12');
        });

        it('returns empty string for falsy input', () => {
            expect(formatDayLabel('')).toBe('');
            expect(formatDayLabel(null)).toBe('');
            expect(formatDayLabel(undefined)).toBe('');
        });

        it('returns original string for invalid format', () => {
            expect(formatDayLabel('invalid')).toBe('invalid');
            expect(formatDayLabel('01-15')).toBe('01-15');
        });
    });

    describe('formatDayTitle', () => {
        it('formats ISO date to DD/MM/YYYY', () => {
            expect(formatDayTitle('2026-01-15')).toBe('15/01/2026');
            expect(formatDayTitle('2026-12-31')).toBe('31/12/2026');
        });

        it('returns empty string for falsy input', () => {
            expect(formatDayTitle('')).toBe('');
            expect(formatDayTitle(null)).toBe('');
        });
    });

    describe('buildLinePaths', () => {
        it('returns empty array for empty or null values', () => {
            expect(buildLinePaths([], 100, 100)).toEqual([]);
            expect(buildLinePaths(null, 100, 100)).toEqual([]);
            expect(buildLinePaths(undefined, 100, 100)).toEqual([]);
        });

        it('creates a single path for continuous values', () => {
            const paths = buildLinePaths([50, 60, 70], 100, 100, 0);
            expect(paths).toHaveLength(1);
            expect(paths[0]).toMatch(/^M \d/); // starts with M (moveto)
            expect(paths[0]).toContain('L'); // contains L (lineto)
        });

        it('creates multiple paths when values have nulls', () => {
            const paths = buildLinePaths([50, null, 70], 100, 100, 0);
            expect(paths).toHaveLength(2);
        });

        it('handles single value correctly', () => {
            const paths = buildLinePaths([50], 100, 100, 8);
            expect(paths).toHaveLength(1);
            expect(paths[0]).toMatch(/^M \d+ \d+$/);
        });

        it('clamps values to 0-100 range', () => {
            const paths = buildLinePaths([150, -20], 100, 100, 0);
            expect(paths).toHaveLength(1);
            // Values should be clamped - 150 becomes 100 (y=0), -20 becomes 0 (y=100)
        });

        it('applies padding correctly', () => {
            const pathsNoPadding = buildLinePaths([0, 100], 100, 100, 0);
            const pathsWithPadding = buildLinePaths([0, 100], 100, 100, 10);

            // With padding, coordinates should be within bounds
            expect(pathsWithPadding[0]).not.toEqual(pathsNoPadding[0]);
        });

        it('handles all null values', () => {
            const paths = buildLinePaths([null, null, null], 100, 100);
            expect(paths).toEqual([]);
        });
    });
});
