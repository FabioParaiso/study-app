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
        api.post.mockResolvedValue({ data: { questions: [] } });

        await studyService.generateQuiz('all', 'multiple-choice');

        expect(api.post).toHaveBeenCalledWith('/generate-quiz', {
            topics: [],
            quiz_type: 'multiple-choice'
        });
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
});
