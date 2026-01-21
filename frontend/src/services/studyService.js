import api from './api';

export const studyService = {
    checkMaterial: async (studentId) => {
        const res = await api.get(`/current-material?student_id=${studentId}`);
        return res.data;
    },
    uploadFile: async (file, studentId) => {
        const formData = new FormData();
        formData.append("file", file);
        formData.append("student_id", studentId);
        const res = await api.post('/upload', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });
        return res.data;
    },
    analyzeTopics: async (studentId) => {
        const res = await api.post('/analyze-topics', { student_id: studentId });
        return res.data;
    },
    clearMaterial: async (studentId) => {
        await api.post(`/clear-material?student_id=${studentId}`);
    },
    generateQuiz: async (topics, type, studentId) => {
        const payload = {
            // If it's an array, use it directly. If 'all', empty list. If string, wrap in list.
            topics: Array.isArray(topics) ? topics : (topics === 'all' ? [] : [topics]),
            quiz_type: type, // Pass the type directly (multiple, short_answer, open-ended)
            student_id: studentId
        };
        const res = await api.post('/generate-quiz', payload);
        return res.data.questions;
    },
    evaluateAnswer: async (question, userAnswer, studentId, type = 'open-ended') => {
        const res = await api.post('/evaluate-answer', {
            question,
            user_answer: userAnswer,
            student_id: studentId,
            quiz_type: type
        });
        return res.data;
    },
    submitQuizResult: async (score, total, type, detailedResults, studentId, xpEarned, materialId) => {
        await api.post('/quiz/result', {
            score,
            total_questions: total,
            quiz_type: type,
            detailed_results: detailedResults,
            student_id: studentId,
            study_material_id: materialId,
            xp_earned: xpEarned
        });
    },
    getWeakPoints: async (studentId, materialId) => {
        if (!studentId) return [];
        let url = `/analytics/weak-points?student_id=${studentId}&t=${Date.now()}`;
        if (materialId) {
            url += `&material_id=${materialId}`;
        }
        const res = await api.get(url);
        return res.data;
    },
    getRecommendations: async (studentId) => {
        const res = await api.get(`/students/${studentId}/recommendations`);
        return res.data;
    },
    updateXP: async (studentId, amount) => {
        const res = await api.post('/gamification/xp', { student_id: studentId, amount });
        return res.data;
    },
    updateAvatar: async (studentId, avatar) => {
        const res = await api.post('/gamification/avatar', { student_id: studentId, avatar });
        return res.data;
    },
    updateHighScore: async (studentId, score) => {
        const res = await api.post('/gamification/highscore', { student_id: studentId, score });
        return res.data;
    },
    getMaterials: async (studentId) => {
        const res = await api.get(`/materials?student_id=${studentId}`);
        return res.data;
    },
    activateMaterial: async (studentId, materialId) => {
        const res = await api.post(`/materials/${materialId}/activate?student_id=${studentId}`);
        return res.data;
    }
};
