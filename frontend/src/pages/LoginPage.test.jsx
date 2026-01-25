import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import LoginPage from './LoginPage';

// Mock assets
vi.mock('../assets/mascot.png', () => ({ default: 'mascot.png' }));

// Mock services
vi.mock('../services/authService', () => ({
    authService: {
        loginStudent: vi.fn(),
        registerStudent: vi.fn(),
    }
}));

describe('LoginPage', () => {
    it('should have an accessible toggle for password visibility', () => {
        render(<LoginPage onLogin={() => {}} />);

        // Initial state: Password hidden -> Button should say "Mostrar chave de acesso"
        // This will fail until the aria-label is added
        const toggleButton = screen.getByRole('button', { name: /mostrar chave de acesso/i });
        expect(toggleButton).toBeInTheDocument();

        // Click it
        fireEvent.click(toggleButton);

        // State: Password shown -> Button should say "Ocultar chave de acesso"
        expect(toggleButton).toHaveAttribute('aria-label', 'Ocultar chave de acesso');
    });
});
