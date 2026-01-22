import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import ComboCounter from './ComboCounter';

describe('ComboCounter', () => {
    it('does not render anything when combo is 0', () => {
        const { container } = render(<ComboCounter combo={0} />);
        expect(container).toBeEmptyDOMElement();
    });

    it('renders combo count when greater than 1', () => {
        render(<ComboCounter combo={5} />);
        expect(screen.getByText('5x')).toBeInTheDocument();
        expect(screen.getByText(/Combo/i)).toBeInTheDocument();
    });

    it('shows purple color when combo is high enough (>= 5)', () => {
        render(<ComboCounter combo={5} />);
        const comboText = screen.getByText('5x');
        expect(comboText.className).toContain('text-purple-500');
    });

    it('does not show anything when combo is low (< 2)', () => {
        const { container } = render(<ComboCounter combo={1} />);
        expect(container).toBeEmptyDOMElement();
    });

    it('applies different colors based on combo intensity', () => {
        const { rerender } = render(<ComboCounter combo={3} />);
        let comboText = screen.getByText('3x');
        // Orange for low combo (2-4)
        expect(comboText.className).toContain('text-orange-500');

        rerender(<ComboCounter combo={5} />);
        comboText = screen.getByText('5x');
        // Purple for medium combo (5-9)
        expect(comboText.className).toContain('text-purple-500');

        rerender(<ComboCounter combo={10} />);
        comboText = screen.getByText('10x');
        // Red for high combo (10+)
        expect(comboText.className).toContain('text-red-600');
    });
});
