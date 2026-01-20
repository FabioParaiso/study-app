import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

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
    generateQuiz: async (topics, type, studentId) => {
        const payload = {
            topics: topics === 'all' ? [] : [topics],
            quiz_type: type === 'open-ended' ? 'open-ended' : 'multiple',
            student_id: studentId
        };
        const res = await api.post('/generate-quiz', payload);
        return res.data.questions;
    },
    evaluateAnswer: async (question, userAnswer) => {
        const res = await api.post('/evaluate-answer', {
            question,
            user_answer: userAnswer
        });
        return res.data;
    },
    submitQuizResult: async (score, total, type, detailedResults, studentId) => {
        await api.post('/quiz/result', {
            score,
            total_questions: total,
            quiz_type: type,
            detailed_results: detailedResults,
            student_id: studentId
        });
    },
    getWeakPoints: async (studentId) => {
        if (!studentId) return [];
        const res = await api.get(`/analytics/weak-points?student_id=${studentId}`);
        return res.data;
    },
    loginStudent: async (name) => {
        const res = await api.post('/students', { name });
        return res.data;
    },
    getRecommendations: async (studentId) => {
        const res = await api.get(`/students/${studentId}/recommendations`);
        return res.data;
    }
};

export default api;
