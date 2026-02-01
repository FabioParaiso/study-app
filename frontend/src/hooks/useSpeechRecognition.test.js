import { renderHook, waitFor } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { useSpeechRecognition } from './useSpeechRecognition';

describe('useSpeechRecognition', () => {
    it('returns unsupported when browser API is missing', async () => {
        const { result } = renderHook(() => useSpeechRecognition());

        await waitFor(() => {
            expect(result.current.supported).toBe(false);
            expect(result.current.error).toBe('Browser not supported');
        });
    });
});
