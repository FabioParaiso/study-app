import { renderHook, waitFor, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { useMaterial } from './useMaterial';
import { studyService } from '../services/studyService';

vi.mock('../services/studyService', () => ({
    studyService: {
        checkMaterial: vi.fn(),
        getMaterials: vi.fn(),
        uploadFile: vi.fn(),
        analyzeTopics: vi.fn(),
        clearMaterial: vi.fn(),
        activateMaterial: vi.fn(),
        deleteMaterial: vi.fn()
    }
}));

describe('useMaterial', () => {
    let consoleError;

    beforeEach(() => {
        vi.clearAllMocks();
        consoleError = vi.spyOn(console, 'error').mockImplementation(() => {});
    });

    afterEach(() => {
        consoleError.mockRestore();
    });

    it('maps topic dictionary into sorted list', async () => {
        studyService.checkMaterial.mockResolvedValue({
            has_material: true,
            id: 1,
            source: 'file.txt',
            text: 'content',
            topics: { Biology: ['Cell'], Algebra: ['X'] }
        });
        studyService.getMaterials.mockResolvedValue([{ id: 1 }]);

        const { result } = renderHook(() => useMaterial(1));

        await waitFor(() => {
            expect(result.current.availableTopics).toEqual(['Algebra', 'Biology']);
        });

        expect(result.current.savedMaterial.id).toBe(1);
    });

    it('sets error message when upload fails', async () => {
        studyService.checkMaterial.mockResolvedValue({ has_material: false });
        studyService.getMaterials.mockResolvedValue([]);
        studyService.uploadFile.mockRejectedValueOnce(new Error('upload fail'));

        const { result } = renderHook(() => useMaterial(1));

        // Simulate file selection
        act(() => {
            result.current.handleFileChange({ target: { files: [new File(['x'], 'file.txt', { type: 'text/plain' })] } });
        });

        await act(async () => {
            await result.current.analyzeFile();
        });

        expect(result.current.errorMsg).toBe('Falha ao analisar o ficheiro.');
        expect(result.current.isAnalyzing).toBe(false);
    });

    it('sets error message when detectTopics fails', async () => {
        studyService.checkMaterial.mockResolvedValue({ has_material: false });
        studyService.getMaterials.mockResolvedValue([]);
        studyService.analyzeTopics.mockRejectedValueOnce(new Error('fail'));

        const { result } = renderHook(() => useMaterial(1));

        await act(async () => {
            await result.current.detectTopics();
        });

        expect(result.current.errorMsg).toContain('Falha ao detetar');
        expect(result.current.isAnalyzing).toBe(false);
    });

    it('shows backend quota detail when upload is rate-limited', async () => {
        studyService.checkMaterial.mockResolvedValue({ has_material: false });
        studyService.getMaterials.mockResolvedValue([]);
        studyService.uploadFile.mockRejectedValueOnce({
            response: { data: { detail: 'Limite diario atingido (200/dia).' } }
        });

        const { result } = renderHook(() => useMaterial(1));

        act(() => {
            result.current.handleFileChange({ target: { files: [new File(['x'], 'file.txt', { type: 'text/plain' })] } });
        });

        await act(async () => {
            await result.current.analyzeFile();
        });

        expect(result.current.errorMsg).toBe('Limite diario atingido (200/dia).');
        expect(result.current.isAnalyzing).toBe(false);
    });

    it('resets selectedTopic to all when current topic is no longer available', async () => {
        studyService.checkMaterial
            .mockResolvedValueOnce({
                has_material: true,
                id: 1,
                source: 'file1.txt',
                text: 'content',
                topics: { Biology: ['Cell'] }
            })
            .mockResolvedValueOnce({
                has_material: true,
                id: 2,
                source: 'file2.txt',
                text: 'content',
                topics: { Math: ['Algebra'] }
            });
        studyService.getMaterials.mockResolvedValue([]);

        const { result } = renderHook(() => useMaterial(1));

        await waitFor(() => {
            expect(result.current.availableTopics).toEqual(['Biology']);
        });

        act(() => {
            result.current.setSelectedTopic('Biology');
        });
        expect(result.current.selectedTopic).toBe('Biology');

        await act(async () => {
            await result.current.refreshMaterial();
        });

        await waitFor(() => {
            expect(result.current.availableTopics).toEqual(['Math']);
            expect(result.current.selectedTopic).toBe('all');
        });
    });
});
