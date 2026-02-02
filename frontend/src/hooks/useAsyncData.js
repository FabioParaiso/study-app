import { useState, useEffect, useCallback } from 'react';

/**
 * Generic hook for async data fetching with loading and error states.
 * Handles component unmount cancellation to prevent state updates on unmounted components.
 *
 * @param {Function} fetchFn - Async function that returns a promise with data.
 * @param {Array} deps - Dependency array for the effect.
 * @param {string} errorMessage - Error message to display on failure.
 * @returns {{ data: any, loading: boolean, error: string, refetch: Function }}
 */
export function useAsyncData(fetchFn, deps = [], errorMessage = 'Failed to load data.') {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    const load = useCallback(() => {
        let cancelled = false;

        setLoading(true);
        setError('');

        fetchFn()
            .then((result) => {
                if (!cancelled) {
                    setData(result);
                }
            })
            .catch(() => {
                if (!cancelled) {
                    setError(errorMessage);
                }
            })
            .finally(() => {
                if (!cancelled) {
                    setLoading(false);
                }
            });

        return () => {
            cancelled = true;
        };
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, deps);

    useEffect(() => {
        return load();
    }, [load]);

    const refetch = useCallback(() => {
        load();
    }, [load]);

    return { data, loading, error, refetch };
}

export default useAsyncData;
