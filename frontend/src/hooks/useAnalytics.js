import { useState, useEffect } from 'react';
import { studyService } from '../services/studyService';

export function useAnalytics(studentId, materialId) {
    const [points, setPoints] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!studentId) {
            setPoints([]);
            return;
        }

        let isActive = true;
        setLoading(true);
        // Clear old points immediately to avoid "ghost topics"
        setPoints([]);

        const loadPoints = async () => {
            try {
                // Backend automatically scopes to active material for this student
                const data = await studyService.getWeakPoints(materialId);

                if (isActive) {
                    setPoints(data);
                    setError(null);
                }
            } catch (err) {
                if (isActive) {
                    console.error(err);
                    setError(err);
                }
            } finally {
                if (isActive) {
                    setLoading(false);
                }
            }
        };

        loadPoints();

        return () => {
            isActive = false;
        };
    }, [studentId, materialId]);

    return { points, loading, error };
}
