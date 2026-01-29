import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import MaterialLibrary from './MaterialLibrary';

describe('MaterialLibrary', () => {
    const mockMaterials = [
        { id: 1, source: 'Physics.pdf', created_at: '2023-01-01', total_xp: 100 },
        { id: 2, source: 'History.txt', created_at: '2023-01-02', total_xp: 50 },
    ];
    const mockOnActivate = vi.fn();
    const mockOnDelete = vi.fn();

    it('renders list of materials', () => {
        render(
            <MaterialLibrary
                materials={mockMaterials}
                onActivate={mockOnActivate}
                onDelete={mockOnDelete}
                currentId={1}
            />
        );
        expect(screen.getByText('Physics.pdf')).toBeInTheDocument();
        expect(screen.getByText('History.txt')).toBeInTheDocument();
    });

    it('has accessible delete buttons', () => {
        render(
            <MaterialLibrary
                materials={mockMaterials}
                onActivate={mockOnActivate}
                onDelete={mockOnDelete}
                currentId={1}
            />
        );
        // Expecting specific aria-labels
        expect(screen.getByRole('button', { name: 'Remover Physics.pdf' })).toBeInTheDocument();
        expect(screen.getByRole('button', { name: 'Remover History.txt' })).toBeInTheDocument();
    });

    it('allows keyboard activation via Enter key', () => {
        render(
            <MaterialLibrary
                materials={mockMaterials}
                onActivate={mockOnActivate}
                onDelete={mockOnDelete}
                currentId={2}
            />
        );

        // Find the inactive item (Physics.pdf) which should be a button
        // Since it contains the text "Physics.pdf", this selector should work if it has role="button"
        // Note: The delete button is inside, so we need to be careful with selection.
        // We look for the container that is a button and contains the text.

        // This query might be ambiguous because the delete button is also a button.
        // But the delete button name is "Remover Physics.pdf".
        // The item button name will be the text content roughly.

        // Let's rely on finding the container by text, then checking its role.
        const titleElement = screen.getByText('Physics.pdf');
        const listRow = titleElement.closest('[role="button"]');

        expect(listRow).toBeInTheDocument();

        fireEvent.keyDown(listRow, { key: 'Enter', code: 'Enter' });
        expect(mockOnActivate).toHaveBeenCalledWith(1);
    });

    it('allows keyboard activation via Space key', () => {
        render(
            <MaterialLibrary
                materials={mockMaterials}
                onActivate={mockOnActivate}
                onDelete={mockOnDelete}
                currentId={2}
            />
        );
        const titleElement = screen.getByText('Physics.pdf');
        const listRow = titleElement.closest('[role="button"]');

        expect(listRow).toBeInTheDocument();

        fireEvent.keyDown(listRow, { key: ' ', code: 'Space' });
        expect(mockOnActivate).toHaveBeenCalledWith(1);
    });
});
