import { renderHook, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { useGamification } from './useGamification';
import { studyService } from '../services/studyService';

vi.mock('../services/studyService', () => ({
    studyService: {
        updateAvatar: vi.fn()
    }
}));

// Mock auth context or service if needed
// Assuming simple state logic for now based on file view earlier

describe('useGamification Hook', () => {
    let consoleError;

    beforeEach(() => {
        vi.unstubAllEnvs();
        consoleError = vi.spyOn(console, 'error').mockImplementation(() => {});
    });

    afterEach(() => {
        consoleError.mockRestore();
    });

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

    it('syncs stats from props', () => {
        vi.stubEnv('VITE_COOP_CHALLENGE_ENABLED', 'false');
        const student = { id: 1, current_avatar: 'rocket' };
        const stats = { total_xp: 300, high_score: 42 };
        const { result } = renderHook(() => useGamification(student, stats));

        expect(result.current.totalXP).toBe(300);
        expect(result.current.highScore).toBe(42);
        expect(result.current.selectedAvatar).toBe('rocket');
    });

    it('uses challenge_xp when coop challenge flag is enabled', () => {
        vi.stubEnv('VITE_COOP_CHALLENGE_ENABLED', 'true');
        const student = { id: 1, challenge_xp: 555, current_avatar: 'mascot' };
        const stats = { total_xp: 999, high_score: 42 };

        const { result } = renderHook(() => useGamification(student, stats));

        expect(result.current.totalXP).toBe(555);
    });

    it('reverts avatar when update fails', async () => {
        const student = { id: 1, current_avatar: 'mascot' };
        const { result } = renderHook(() => useGamification(student, {}));

        studyService.updateAvatar.mockRejectedValueOnce(new Error('fail'));

        await act(async () => {
            await result.current.changeAvatar('rocket');
        });

        expect(result.current.selectedAvatar).toBe('mascot');
    });
});
