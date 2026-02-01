import { describe, it, expect, vi, beforeEach } from 'vitest';

vi.mock('axios', () => {
    const create = vi.fn(() => ({
        interceptors: {
            request: {
                use: vi.fn()
            }
        }
    }));
    return { default: { create } };
});

describe('api interceptor', () => {
    beforeEach(() => {
        localStorage.clear();
        vi.resetModules();
    });

    it('injects Authorization header when token exists', async () => {
        localStorage.setItem('study_token', 'token-abc');

        const axios = await import('axios');
        const apiModule = await import('./api');
        const config = { headers: {} };

        const useCalls = axios.default.create.mock.results[0].value.interceptors.request.use.mock.calls;
        const interceptor = useCalls[0][0];
        const result = interceptor(config);

        expect(result.headers.Authorization).toBe('Bearer token-abc');
        expect(apiModule.default).toBeDefined();
    });
});
