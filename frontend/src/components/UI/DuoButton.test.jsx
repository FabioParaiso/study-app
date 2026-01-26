import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import DuoButton from './DuoButton';
import { describe, it, expect, vi } from 'vitest';

describe('DuoButton', () => {
    it('renders children correctly', () => {
        render(<DuoButton>Click Me</DuoButton>);
        expect(screen.getByText('Click Me')).toBeInTheDocument();
    });

    it('handles onClick', () => {
        const handleClick = vi.fn();
        render(<DuoButton onClick={handleClick}>Click Me</DuoButton>);
        fireEvent.click(screen.getByText('Click Me'));
        expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('applies disabled style', () => {
        render(<DuoButton disabled>Disabled</DuoButton>);
        const button = screen.getByText('Disabled');
        expect(button).toBeDisabled();
        expect(button).toHaveClass('cursor-not-allowed');
    });
});
