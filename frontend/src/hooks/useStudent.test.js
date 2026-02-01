import { renderHook, act } from '@testing-library/react';
import { describe, it, expect, beforeEach } from 'vitest';
import { useStudent } from './useStudent';

describe('useStudent', () => {
    beforeEach(() => {
        localStorage.clear();
    });

    it('loads student from localStorage on init', () => {
        localStorage.setItem('study_student', JSON.stringify({ id: 1, name: 'Alice' }));
        const { result } = renderHook(() => useStudent());

        expect(result.current.student).toEqual({ id: 1, name: 'Alice' });
    });

    it('logout clears student and token', () => {
        localStorage.setItem('study_student', JSON.stringify({ id: 1, name: 'Alice' }));
        localStorage.setItem('study_token', 'token');

        const { result } = renderHook(() => useStudent());

        act(() => {
            result.current.logout();
        });

        expect(localStorage.getItem('study_student')).toBeNull();
        expect(localStorage.getItem('study_token')).toBeNull();
    });
});
