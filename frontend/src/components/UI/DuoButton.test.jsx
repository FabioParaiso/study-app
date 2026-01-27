import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import DuoButton from './DuoButton';

describe('DuoButton', () => {
    it('renders children correctly', () => {
        render(<DuoButton>Click Me</DuoButton>);
        expect(screen.getByText('Click Me')).toBeInTheDocument();
    });

    it('calls onClick handler when clicked', () => {
        const handleClick = vi.fn();
        render(<DuoButton onClick={handleClick}>Click Me</DuoButton>);

        fireEvent.click(screen.getByText('Click Me'));
        expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('applies disabled style and prevents click when disabled', () => {
        const handleClick = vi.fn();
        render(<DuoButton disabled onClick={handleClick}>Disabled</DuoButton>);

        const button = screen.getByText('Disabled');
        expect(button).toBeDisabled();

        fireEvent.click(button);
        expect(handleClick).not.toHaveBeenCalled();
    });

    it('applies custom className', () => {
        render(<DuoButton className="custom-class">Custom</DuoButton>);
        const button = screen.getByText('Custom');
        expect(button).toHaveClass('custom-class');
    });

    it('passes extra props to button element', () => {
        render(<DuoButton aria-label="test-label">Label</DuoButton>);
        const button = screen.getByText('Label');
        expect(button).toHaveAttribute('aria-label', 'test-label');
    });
});
