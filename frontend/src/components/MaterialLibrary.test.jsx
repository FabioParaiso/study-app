import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import MaterialLibrary from './MaterialLibrary';
import React from 'react';

// Mock lucide-react icons
vi.mock('lucide-react', () => ({
    Book: () => <div data-testid="icon-book" />,
    CheckCircle: () => <div data-testid="icon-check-circle" />,
    Clock: () => <div data-testid="icon-clock" />,
    Trash2: () => <div data-testid="icon-trash-2" />,
}));

// Mock Modal component
vi.mock('./UI/Modal', () => ({
    default: ({ isOpen, children, onClose, title }) => (
        isOpen ? (
            <div data-testid="modal">
                <h1>{title}</h1>
                <button onClick={onClose} data-testid="modal-close">Close</button>
                {children}
            </div>
        ) : null
    )
}));

describe('MaterialLibrary', () => {
    const mockMaterials = [
        { id: 1, source: 'Material 1', created_at: '2023-01-01', total_xp: 100 },
        { id: 2, source: 'Material 2', created_at: '2023-01-02', total_xp: 200 },
    ];
    const mockOnActivate = vi.fn();
    const mockOnDelete = vi.fn();

    it('renders nothing when materials list is empty', () => {
        const { container } = render(<MaterialLibrary materials={[]} />);
        expect(container.firstChild).toBeNull();
    });

    it('renders list of materials', () => {
        render(
            <MaterialLibrary
                materials={mockMaterials}
                onActivate={mockOnActivate}
                onDelete={mockOnDelete}
                currentId={1}
            />
        );

        expect(screen.getByText('Material 1')).toBeInTheDocument();
        expect(screen.getByText('Material 2')).toBeInTheDocument();
        expect(screen.getByText('Biblioteca de Estudo')).toBeInTheDocument();
    });

    it('calls onActivate when clicking an inactive material', () => {
        render(
            <MaterialLibrary
                materials={mockMaterials}
                onActivate={mockOnActivate}
                onDelete={mockOnDelete}
                currentId={1}
            />
        );

        // Click Material 2 (inactive)
        fireEvent.click(screen.getByText('Material 2'));
        expect(mockOnActivate).toHaveBeenCalledWith(2);

        // Click Material 1 (active)
        fireEvent.click(screen.getByText('Material 1'));
        expect(mockOnActivate).not.toHaveBeenCalledWith(1);
    });

    it('opens delete modal when clicking trash icon', () => {
        render(
            <MaterialLibrary
                materials={mockMaterials}
                onActivate={mockOnActivate}
                onDelete={mockOnDelete}
                currentId={1}
            />
        );

        // Find all trash icons (buttons really)
        // The component uses title="Remover ficheiro"
        const deleteButtons = screen.getAllByTitle('Remover ficheiro');
        fireEvent.click(deleteButtons[0]);

        expect(screen.getByTestId('modal')).toBeInTheDocument();
        expect(screen.getByText('Apagar Material')).toBeInTheDocument();
    });

    it('calls onDelete when confirming deletion', () => {
        render(
            <MaterialLibrary
                materials={mockMaterials}
                onActivate={mockOnActivate}
                onDelete={mockOnDelete}
                currentId={1}
            />
        );

        const deleteButtons = screen.getAllByTitle('Remover ficheiro');
        fireEvent.click(deleteButtons[0]); // Material 1

        const confirmButton = screen.getByText('Apagar');
        fireEvent.click(confirmButton);

        expect(mockOnDelete).toHaveBeenCalledWith(1);
    });
});
