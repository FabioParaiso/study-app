import { describe, it, expect } from 'vitest';
import { calculateXPFromScore } from './xpCalculator';

describe('calculateXPFromScore', () => {
    it('returns base XP (5) for scores below 50', () => {
        expect(calculateXPFromScore(0)).toBe(5);
        expect(calculateXPFromScore(49)).toBe(5);
    });

    it('returns base + bonus (10) for scores 50-79', () => {
        expect(calculateXPFromScore(50)).toBe(10);
        expect(calculateXPFromScore(79)).toBe(10);
    });

    it('returns base + two bonuses (15) for scores >= 80', () => {
        expect(calculateXPFromScore(80)).toBe(15);
        expect(calculateXPFromScore(100)).toBe(15);
    });

    it('handles edge cases correctly', () => {
        // Lower boundary
        expect(calculateXPFromScore(0)).toBe(5);

        // First tier boundary
        expect(calculateXPFromScore(49)).toBe(5);
        expect(calculateXPFromScore(50)).toBe(10);

        // Second tier boundary
        expect(calculateXPFromScore(79)).toBe(10);
        expect(calculateXPFromScore(80)).toBe(15);

        // Upper boundary
        expect(calculateXPFromScore(100)).toBe(15);
    });

    it('is a pure function (consistent output)', () => {
        const score = 75;
        const result1 = calculateXPFromScore(score);
        const result2 = calculateXPFromScore(score);
        expect(result1).toBe(result2);
    });
});
