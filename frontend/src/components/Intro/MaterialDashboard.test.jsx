import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import MaterialDashboard from './MaterialDashboard';

// Mock child components
vi.mock('../WeakPointsPanel', () => ({
  default: () => <div data-testid="weak-points-panel">Weak Points Panel</div>
}));

// Mock lucide-react icons
vi.mock('lucide-react', () => ({
    BookOpen: () => <span data-testid="icon-book-open" />,
    XCircle: () => <span data-testid="icon-x-circle" />,
    Trophy: () => <span data-testid="icon-trophy" />,
    PenTool: () => <span data-testid="icon-pen-tool" />,
    Lock: () => <span data-testid="icon-lock" />
}));

describe('MaterialDashboard', () => {
    const defaultProps = {
        savedMaterial: {
            id: 1,
            source: 'Test Material',
            total_xp: 150
        },
        availableTopics: ['Topic 1', 'Topic 2'],
        selectedTopic: 'all',
        setSelectedTopic: vi.fn(),
        clearMaterial: vi.fn(),
        startQuiz: vi.fn(),
        loading: false,
        studentId: 123
    };

    it('renders the delete button with correct aria-label', () => {
        render(<MaterialDashboard {...defaultProps} />);

        const deleteButton = screen.getByRole('button', { name: /remover matéria atual/i });
        expect(deleteButton).toBeInTheDocument();
    });

    it('calls clearMaterial when delete button is clicked', () => {
        render(<MaterialDashboard {...defaultProps} />);

        const deleteButton = screen.getByRole('button', { name: /remover matéria atual/i });
        fireEvent.click(deleteButton);

        expect(defaultProps.clearMaterial).toHaveBeenCalledTimes(1);
    });

    it('has accessible focus styles', () => {
        render(<MaterialDashboard {...defaultProps} />);
        const deleteButton = screen.getByRole('button', { name: /remover matéria atual/i });
        expect(deleteButton).toHaveClass('focus-visible:ring-2');
        expect(deleteButton).toHaveClass('focus-visible:ring-duo-red');
    });
});
