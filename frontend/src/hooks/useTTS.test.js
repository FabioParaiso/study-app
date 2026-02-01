import { renderHook, act } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { useTTS } from './useTTS';

describe('useTTS', () => {
    const originalSpeech = window.speechSynthesis;
    const originalUtterance = global.SpeechSynthesisUtterance;

    beforeEach(() => {
        window.speechSynthesis = {
            speak: vi.fn(),
            cancel: vi.fn()
        };
        global.SpeechSynthesisUtterance = class {
            constructor(text) {
                this.text = text;
                this.lang = '';
                this.onend = null;
                this.onerror = null;
            }
        };
    });

    afterEach(() => {
        window.speechSynthesis = originalSpeech;
        global.SpeechSynthesisUtterance = originalUtterance;
    });

    it('speaks and toggles off when same part is requested', () => {
        const { result } = renderHook(() => useTTS());

        act(() => {
            result.current.handleSpeak('Hello world', 'question');
        });

        expect(window.speechSynthesis.speak).toHaveBeenCalled();

        act(() => {
            result.current.handleSpeak('Hello world', 'question');
        });

        expect(window.speechSynthesis.cancel).toHaveBeenCalled();
    });
});
