import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import QuestionHeader from './QuestionHeader';

describe('QuestionHeader', () => {
    const defaultProps = {
        topic: "Geography",
        question: "What is the capital of France?",
        onSpeak: vi.fn(),
        isSpeaking: false,
        accentColor: 'blue'
    };

    it('renders topic and question text', () => {
        render(<QuestionHeader {...defaultProps} />);
        expect(screen.getByText("Geography")).toBeInTheDocument();
        expect(screen.getByText("What is the capital of France?")).toBeInTheDocument();
    });

    it('has an accessible TTS button with correct initial label', () => {
        render(<QuestionHeader {...defaultProps} />);
        const button = screen.getByLabelText("Ouvir pergunta");
        expect(button).toBeInTheDocument();
        fireEvent.click(button);
        expect(defaultProps.onSpeak).toHaveBeenCalledWith("What is the capital of France?", "question");
    });

    it('changes label when speaking', () => {
        render(<QuestionHeader {...defaultProps} isSpeaking={true} />);
        const button = screen.getByLabelText("Parar de ouvir");
        expect(button).toBeInTheDocument();
    });
});
