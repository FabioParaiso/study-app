import { useCallback, useEffect, useMemo, useState } from 'react';
import { studyService } from '../services/studyService';

const POLL_MS = 30 * 1000;

const isEnabledByEnv = () => {
    const raw = String(import.meta.env.VITE_COOP_CHALLENGE_ENABLED || 'false').toLowerCase();
    return raw === '1' || raw === 'true' || raw === 'yes' || raw === 'on';
};

export function useChallengeStatus(studentId, options = {}) {
    const enabled = options.enabled ?? isEnabledByEnv();
    const [status, setStatus] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const canFetch = useMemo(() => Boolean(enabled && studentId), [enabled, studentId]);

    const fetchStatus = useCallback(async () => {
        if (!canFetch) return null;
        setLoading(true);
        setError('');
        try {
            const data = await studyService.getChallengeStatus();
            setStatus(data || null);
            return data;
        } catch (err) {
            const detail = err?.response?.data?.detail;
            setError(detail || 'Falha ao carregar estado do desafio.');
            return null;
        } finally {
            setLoading(false);
        }
    }, [canFetch]);

    useEffect(() => {
        if (!canFetch) {
            setStatus(null);
            setError('');
            setLoading(false);
            return;
        }

        fetchStatus();
        const intervalId = setInterval(fetchStatus, POLL_MS);
        return () => clearInterval(intervalId);
    }, [canFetch, fetchStatus]);

    return { status, loading, error, refresh: fetchStatus, enabled: Boolean(enabled) };
}
