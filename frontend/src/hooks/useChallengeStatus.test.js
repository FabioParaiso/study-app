import { renderHook, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { useChallengeStatus } from './useChallengeStatus';
import { studyService } from '../services/studyService';

vi.mock('../services/studyService', () => ({
    studyService: {
        getChallengeStatus: vi.fn()
    }
}));

describe('useChallengeStatus', () => {
    beforeEach(() => {
        vi.clearAllMocks();
        vi.unstubAllEnvs();
    });

    it('does not fetch when feature flag is off', async () => {
        vi.stubEnv('VITE_COOP_CHALLENGE_ENABLED', 'false');

        const { result } = renderHook(() => useChallengeStatus(1));

        expect(result.current.enabled).toBe(false);
        expect(studyService.getChallengeStatus).not.toHaveBeenCalled();
    });

    it('fetches status when feature flag is on', async () => {
        vi.stubEnv('VITE_COOP_CHALLENGE_ENABLED', 'true');
        studyService.getChallengeStatus.mockResolvedValueOnce({ week_id: '2026W07' });

        const { result } = renderHook(() => useChallengeStatus(1));

        await waitFor(() => {
            expect(studyService.getChallengeStatus).toHaveBeenCalled();
            expect(result.current.status).toEqual({ week_id: '2026W07' });
        });
    });

    it('exposes error when API call fails', async () => {
        vi.stubEnv('VITE_COOP_CHALLENGE_ENABLED', 'true');
        studyService.getChallengeStatus.mockRejectedValueOnce({
            response: { data: { detail: 'boom' } }
        });

        const { result } = renderHook(() => useChallengeStatus(1));

        await waitFor(() => {
            expect(result.current.error).toBe('boom');
        });
    });
});
