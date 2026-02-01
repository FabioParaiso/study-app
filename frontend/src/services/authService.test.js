import { describe, it, expect, vi, beforeEach } from 'vitest';
import { authService } from './authService';
import api from './api';

vi.mock('./api', () => ({
    default: {
        post: vi.fn()
    }
}));

describe('authService', () => {
    beforeEach(() => {
        localStorage.clear();
        vi.clearAllMocks();
    });

    it('stores token on login', async () => {
        api.post.mockResolvedValue({
            data: {
                access_token: 'token-123',
                user: { id: 1, name: 'User' }
            }
        });

        const user = await authService.loginStudent('User', 'StrongPass1!');

        expect(localStorage.getItem('study_token')).toBe('token-123');
        expect(user.id).toBe(1);
    });

    it('stores token on register', async () => {
        api.post.mockResolvedValue({
            data: {
                access_token: 'token-456',
                user: { id: 2, name: 'User2' }
            }
        });

        const user = await authService.registerStudent('User2', 'StrongPass1!', 'INVITE');

        expect(localStorage.getItem('study_token')).toBe('token-456');
        expect(user.id).toBe(2);
    });
});
