import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import OpenEndedCard from './OpenEndedCard';

describe('OpenEndedCard', () => {
    const mockQuestion = {
        question: "Explain the industrial revolution",
        topic: "History",
        correctIndex: 0,
        options: [],
        explanation: "Machine power replaced muscle power."
    };

    const defaultProps = {
        question: mockQuestion,
        index: 0,
        total: 5,
        onEvaluate: vi.fn(),
        evaluation: null,
        isEvaluating: false,
        onNext: vi.fn(),
        handleSpeak: vi.fn(),
        speakingPart: null
    };

    it('renders the question text', () => {
        render(<OpenEndedCard {...defaultProps} />);
        expect(screen.getByText("Explain the industrial revolution")).toBeInTheDocument();
        expect(screen.getByText("Pergunta Objetiva 1 de 5")).toBeInTheDocument();
    });

    it('allows typing in the textarea', () => {
        render(<OpenEndedCard {...defaultProps} />);
        const textarea = screen.getByPlaceholderText("Escreve a tua resposta aqui...");
        fireEvent.change(textarea, { target: { value: "Machine power" } });
        expect(textarea.value).toBe("Machine power");
    });

    it('disables submit button when input is empty', () => {
        render(<OpenEndedCard {...defaultProps} />);
        const button = screen.getByText("Enviar Resposta");
        // Button is actually disabled by class logic and disabled attribute? 
        // Let's check the code: disabled={isEvaluating || userText.trim().length === 0}
        expect(button.closest('button')).toBeDisabled();
    });

    it('enables submit button when input has text', () => {
        render(<OpenEndedCard {...defaultProps} />);
        const textarea = screen.getByPlaceholderText("Escreve a tua resposta aqui...");
        fireEvent.change(textarea, { target: { value: "Some answer" } });
        const button = screen.getByText("Enviar Resposta");
        expect(button.closest('button')).not.toBeDisabled();
    });

    it('calls onEvaluate when submit button is clicked', () => {
        render(<OpenEndedCard {...defaultProps} />);
        const textarea = screen.getByPlaceholderText("Escreve a tua resposta aqui...");
        fireEvent.change(textarea, { target: { value: "My Answer" } });
        const button = screen.getByText("Enviar Resposta");

        fireEvent.click(button);
        expect(defaultProps.onEvaluate).toHaveBeenCalledWith("My Answer");
    });

    it('displays evaluation when provided', () => {
        const evaluation = {
            score: 85,
            feedback: "Good job!"
        };
        render(<OpenEndedCard {...defaultProps} evaluation={evaluation} />);

        // Input should be gone
        expect(screen.queryByPlaceholderText("Escreve a tua resposta aqui...")).not.toBeInTheDocument();

        // Evaluation should be shown
        expect(screen.getByText("85")).toBeInTheDocument();
        expect(screen.getByText("Good job!")).toBeInTheDocument();
    });
});
