import api from './api';

export const studyService = {
    checkMaterial: async () => {
        const res = await api.get('/current-material');
        return res.data;
    },
    uploadFile: async (file) => {
        const formData = new FormData();
        formData.append("file", file);
        const res = await api.post('/upload', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });
        return res.data;
    },
    analyzeTopics: async () => {
        const res = await api.post('/analyze-topics', {});
        return res.data;
    },
    clearMaterial: async () => {
        await api.post('/clear-material');
    },
    generateQuiz: async (topics, type) => {
        const payload = {
            // If it's an array, use it directly. If 'all', empty list. If string, wrap in list.
            topics: Array.isArray(topics) ? topics : (topics === 'all' ? [] : [topics]),
            quiz_type: type // Pass the type directly (multiple-choice, short_answer, open-ended)
        };
        const res = await api.post('/generate-quiz', payload);
        return res.data;
    },
    evaluateAnswer: async (question, userAnswer, type = 'open-ended') => {
        const res = await api.post('/evaluate-answer', {
            question,
            user_answer: userAnswer,
            quiz_type: type
        });
        return res.data;
    },
    submitQuizResult: async (
        score,
        total,
        type,
        detailedResults,
        xpEarned,
        materialId,
        durationSeconds = 0,
        activeSeconds = 0,
        quizSessionToken = null
    ) => {
        await api.post('/quiz/result', {
            score,
            total_questions: total,
            quiz_type: type,
            detailed_results: detailedResults,
            study_material_id: materialId,
            xp_earned: xpEarned,
            duration_seconds: Math.round(durationSeconds),
            active_seconds: Math.round(activeSeconds),
            quiz_session_token: quizSessionToken
        });
    },
    getChallengeStatus: async () => {
        const res = await api.get('/challenge/weekly-status');
        return res.data;
    },
    getWeakPoints: async (materialId) => {
        let url = `/analytics/weak-points?t=${Date.now()}`;
        if (materialId) {
            url += `&material_id=${materialId}`;
        }
        const res = await api.get(url);
        return res.data;
    },
    getMetrics: async (days = 30, tzOffsetMinutes = 0) => {
        const params = new URLSearchParams({
            days: String(days),
            tz_offset_minutes: String(tzOffsetMinutes),
            t: String(Date.now())
        });
        const res = await api.get(`/analytics/metrics?${params.toString()}`);
        return res.data;
    },
    getLearningTrend: async (days = 30, tzOffsetMinutes = 0, minQuestions = 1) => {
        const params = new URLSearchParams({
            days: String(days),
            tz_offset_minutes: String(tzOffsetMinutes),
            min_questions: String(minQuestions),
            t: String(Date.now())
        });
        const res = await api.get(`/analytics/learning-trend?${params.toString()}`);
        return res.data;
    },
    updateAvatar: async (avatar) => {
        const res = await api.post('/gamification/avatar', { avatar });
        return res.data;
    },
    getMaterials: async () => {
        const res = await api.get('/materials');
        return res.data;
    },
    activateMaterial: async (materialId) => {
        const res = await api.post(`/materials/${materialId}/activate`);
        return res.data;
    },
    deleteMaterial: async (materialId) => {
        const res = await api.delete(`/delete-material/${materialId}`);
        return res.data;
    }
};
