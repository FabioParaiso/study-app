import { renderHook, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { useAnalytics } from './useAnalytics';
import { studyService } from '../services/studyService';

vi.mock('../services/studyService', () => ({
    studyService: {
        getWeakPoints: vi.fn()
    }
}));

describe('useAnalytics', () => {
    let consoleError;

    beforeEach(() => {
        vi.clearAllMocks();
        consoleError = vi.spyOn(console, 'error').mockImplementation(() => {});
    });

    afterEach(() => {
        consoleError.mockRestore();
    });

    it('fetches analytics when studentId is present', async () => {
        studyService.getWeakPoints.mockResolvedValue([{ topic: 'Math' }]);

        const { result } = renderHook(() => useAnalytics(1, 2));

        await waitFor(() => {
            expect(result.current.points.length).toBe(1);
        });
        expect(studyService.getWeakPoints).toHaveBeenCalledWith(2);
    });

    it('clears analytics when studentId is missing', async () => {
        const { result } = renderHook(() => useAnalytics(null, null));

        await waitFor(() => {
            expect(result.current.points).toEqual([]);
        });
        expect(studyService.getWeakPoints).not.toHaveBeenCalled();
    });

    it('sets error when request fails', async () => {
        studyService.getWeakPoints.mockRejectedValueOnce(new Error('fail'));

        const { result } = renderHook(() => useAnalytics(1, null));

        await waitFor(() => {
            expect(result.current.error).toBeTruthy();
            expect(result.current.loading).toBe(false);
        });
    });
});
