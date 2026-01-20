import { useState, useEffect } from 'react';
import { studyService } from '../services/studyService';

export function useAnalytics(studentId) {
    const [points, setPoints] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!studentId) return;

        const loadPoints = async () => {
            setLoading(true);
            try {
                const data = await studyService.getWeakPoints(studentId);
                setPoints(data);
                setError(null);
            } catch (err) {
                console.error(err);
                setError(err);
            } finally {
                setLoading(false);
            }
        };

        loadPoints();
    }, [studentId]);

    return { points, loading, error };
}
