import { describe, it, expect, vi, beforeEach } from 'vitest';
import { studyService } from './studyService';
import api from './api';

vi.mock('./api', () => ({
    default: {
        post: vi.fn(),
        get: vi.fn(),
        delete: vi.fn()
    }
}));

describe('studyService', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    it('generateQuiz sends empty topics when "all"', async () => {
        api.post.mockResolvedValue({ data: { questions: [], quiz_session_token: 'tok' } });

        const payload = await studyService.generateQuiz('all', 'multiple-choice');

        expect(api.post).toHaveBeenCalledWith('/generate-quiz', {
            topics: [],
            quiz_type: 'multiple-choice'
        });
        expect(payload).toEqual({ questions: [], quiz_session_token: 'tok' });
    });

    it('generateQuiz wraps single topic string', async () => {
        api.post.mockResolvedValue({ data: { questions: [] } });

        await studyService.generateQuiz('History', 'multiple-choice');

        expect(api.post).toHaveBeenCalledWith('/generate-quiz', {
            topics: ['History'],
            quiz_type: 'multiple-choice'
        });
    });

    it('generateQuiz passes topic arrays directly', async () => {
        api.post.mockResolvedValue({ data: { questions: [] } });

        await studyService.generateQuiz(['Math', 'Science'], 'multiple-choice');

        expect(api.post).toHaveBeenCalledWith('/generate-quiz', {
            topics: ['Math', 'Science'],
            quiz_type: 'multiple-choice'
        });
    });

    it('submitQuizResult sends timing data', async () => {
        api.post.mockResolvedValue({ data: {} });

        await studyService.submitQuizResult(5, 10, 'multiple-choice', [], 20, 3, 12.7, 9.2, 'quiz-token');

        expect(api.post).toHaveBeenCalledWith('/quiz/result', {
            score: 5,
            total_questions: 10,
            quiz_type: 'multiple-choice',
            detailed_results: [],
            study_material_id: 3,
            xp_earned: 20,
            duration_seconds: 13,
            active_seconds: 9,
            quiz_session_token: 'quiz-token'
        });
    });

    it('getChallengeStatus calls weekly-status endpoint', async () => {
        api.get.mockResolvedValue({ data: { week_id: '2026W07' } });

        const response = await studyService.getChallengeStatus();

        expect(api.get).toHaveBeenCalledWith('/challenge/weekly-status');
        expect(response).toEqual({ week_id: '2026W07' });
    });

    it('getMetrics builds query string with days and offset', async () => {
        api.get.mockResolvedValue({ data: { ok: true } });

        await studyService.getMetrics(7, -60);

        const url = api.get.mock.calls[0][0];
        expect(url).toContain('/analytics/metrics?');
        expect(url).toContain('days=7');
        expect(url).toContain('tz_offset_minutes=-60');
    });

    it('getLearningTrend builds query string with days, offset, and min_questions', async () => {
        api.get.mockResolvedValue({ data: { ok: true } });

        await studyService.getLearningTrend(14, 120, 3);

        const url = api.get.mock.calls[0][0];
        expect(url).toContain('/analytics/learning-trend?');
        expect(url).toContain('days=14');
        expect(url).toContain('tz_offset_minutes=120');
        expect(url).toContain('min_questions=3');
    });
});
