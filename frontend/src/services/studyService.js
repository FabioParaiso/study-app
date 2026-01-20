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
            topics: topics === 'all' ? [] : [topics],
            quiz_type: type === 'open-ended' ? 'open-ended' : 'multiple',
            student_id: studentId
        };
        const res = await api.post('/generate-quiz', payload);
        return res.data.questions;
    },
    evaluateAnswer: async (question, userAnswer, studentId) => {
        const res = await api.post('/evaluate-answer', {
            question,
            user_answer: userAnswer,
            student_id: studentId
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
    getRecommendations: async (studentId) => {
        const res = await api.get(`/students/${studentId}/recommendations`);
        return res.data;
    }
};
