import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import MaterialDashboard from './MaterialDashboard';

// Mock WeakPointsPanel to avoid useAnalytics hook issues
vi.mock('../WeakPointsPanel', () => ({
  default: () => <div data-testid="weak-points-panel">Weak Points Panel</div>
}));

describe('MaterialDashboard', () => {
  const mockSavedMaterial = {
    id: 'mat-123',
    source: 'Test PDF',
    total_xp: 150
  };

  const defaultProps = {
    savedMaterial: mockSavedMaterial,
    availableTopics: ['Topic A', 'Topic B'],
    selectedTopic: 'all',
    setSelectedTopic: vi.fn(),
    clearMaterial: vi.fn(),
    startQuiz: vi.fn(),
    loading: false,
    studentId: 'student-123'
  };

  it('renders material source and WeakPointsPanel', () => {
    render(<MaterialDashboard {...defaultProps} />);

    expect(screen.getByText('Test PDF')).toBeInTheDocument();
    expect(screen.getByTestId('weak-points-panel')).toBeInTheDocument();
  });

  it('has an accessible clear material button', () => {
    render(<MaterialDashboard {...defaultProps} />);

    // Attempt to find the button by its accessible name.
    // This is expected to fail before the fix is applied.
    const clearButton = screen.getByRole('button', { name: /remover matéria/i });

    expect(clearButton).toBeInTheDocument();

    fireEvent.click(clearButton);
    expect(defaultProps.clearMaterial).toHaveBeenCalled();
  });
});
