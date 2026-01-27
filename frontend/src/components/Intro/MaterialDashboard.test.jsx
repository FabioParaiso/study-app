import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import MaterialDashboard from './MaterialDashboard';

// Mock dependencies
vi.mock('../WeakPointsPanel', () => ({
  default: () => <div data-testid="weak-points-panel" />
}));

vi.mock('lucide-react', () => ({
  BookOpen: () => <svg data-testid="icon-book-open" />,
  XCircle: () => <svg data-testid="icon-x-circle" />,
  Trophy: () => <svg data-testid="icon-trophy" />,
  PenTool: () => <svg data-testid="icon-pen-tool" />,
  Lock: () => <svg data-testid="icon-lock" />
}));

describe('MaterialDashboard', () => {
  const mockProps = {
    savedMaterial: {
      id: 1,
      source: 'Test Material',
      total_xp: 0
    },
    availableTopics: ['Topic 1'],
    selectedTopic: 'all',
    setSelectedTopic: vi.fn(),
    clearMaterial: vi.fn(),
    startQuiz: vi.fn(),
    loading: false,
    studentId: 123
  };

  it('renders the clear material button with accessible label', () => {
    render(<MaterialDashboard {...mockProps} />);

    // This expects the element to exist. It will throw if not found.
    const clearButton = screen.getByLabelText('Remover matéria');
    expect(clearButton).toBeInTheDocument();

    // Also verify it has the title for mouse users
    expect(clearButton).toHaveAttribute('title', 'Remover matéria');
  });
});
