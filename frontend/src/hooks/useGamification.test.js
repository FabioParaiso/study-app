import { renderHook, act } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { useGamification } from './useGamification';

// Mock auth context or service if needed
// Assuming simple state logic for now based on file view earlier

describe('useGamification Hook', () => {
    it('initializes with default values', () => {
        const { result } = renderHook(() => useGamification());

        expect(result.current.totalXP).toBe(0);
        // Level is an object, but hook might return current level object
        // Checking initial level title or min xp
        expect(result.current.level.min).toBe(0);
        expect(result.current.level.title).toBe("Estudante Curiosa");
    });

    it('adds generic xp correctly', () => {
        const { result } = renderHook(() => useGamification());

        act(() => {
            result.current.addXP(100);
        });

        expect(result.current.totalXP).toBe(100);
    });

    it('calculates level up correctly', () => {
        const { result } = renderHook(() => useGamification());

        // Assuming level up threshold is e.g. 1000 or formula
        // We'll test state change

        act(() => {
            // Simulate massive XP gain
            result.current.addXP(5000);
        });

        expect(result.current.level.min).toBeGreaterThan(0);
    });
});
