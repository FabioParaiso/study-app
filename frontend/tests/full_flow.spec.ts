import { test, expect } from '@playwright/test';
import path from 'path';

test('Full Study App Flow: Login -> Upload -> Multiple Choice -> Open Ended', async ({ page }) => {
    // 1. Initial Load & Login
    await page.goto('/');

    // Handle Login if we are at login page
    const loginInput = page.getByPlaceholder('Como te chamas?');
    if (await loginInput.isVisible()) {
        const uniqueName = `E2E User ${Date.now()}`;
        await loginInput.fill(uniqueName);
        await page.getByRole('button', { name: 'CONTINUAR' }).click();
    }

    // 2. Upload File
    // Since we are a new user, we should be at Upload Section immediately.
    // However, just in case "E2E User" logic persists (if backend finds similar name?), we keep check simple.
    // But with timestamp it should be unique.

    // Wait for upload section
    const uploadIndicator = page.getByText('Carregar Apontamentos');
    await expect(uploadIndicator).toBeVisible({ timeout: 10000 });

    // Define dashboard indicator for later use
    const dashboardIndicator = page.getByText('Matéria Ativa');


    // Now we should be at Upload section
    await expect(uploadIndicator).toBeVisible();

    // Set input file
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles(path.join(__dirname, '../../backend/sample.txt'));

    // Click Analyze
    await page.getByRole('button', { name: 'COMEÇAR A ESTUDAR' }).click();

    // 3. Material Dashboard & Multiple Choice Quiz
    // Wait for analysis to complete and dashboard to appear (takes time for AI)
    // We look for "Matéria Ativa" again which confirms analysis is done
    // We explicitly wait for the loading spinner to be GONE if it existed, but better to wait for positive state.
    await expect(dashboardIndicator).toBeVisible({ timeout: 60000 });

    // Start Multiple Choice Quiz
    console.log("Starting Multiple Choice Quiz...");
    const classicModeButton = page.locator('button').filter({ hasText: 'Modo Clássico' }).getByText('Começar');
    await classicModeButton.click();

    // Answer Questions (Loop until results)
    while (true) {
        if (await page.getByText('Pontuação Final').isVisible()) {
            break;
        }

        // Check if we need to answer (Option A is visible and enabled)
        // We pick the first option that looks like a choice
        const options = page.getByRole('button').filter({ hasText: /^[ABCD]$/ });

        if (await options.count() > 0) {
            const optionA = options.first();
            // Retry ensuring it's stable
            if (await optionA.isVisible()) {
                await optionA.click();

                // Wait for next/continue button
                const nextBtn = page.getByRole('button', { name: /Continuar|Ver Nota/ });
                await expect(nextBtn).toBeVisible();
                await nextBtn.click();
                continue;
            }
        }

        // Check if we missed the button or it's just transition
        await page.waitForTimeout(500);
    }

    // 4. Results Page (Multiple Choice)
    await expect(page.getByText('MENU PRINCIPAL')).toBeVisible();
    await page.getByRole('button', { name: 'MENU PRINCIPAL' }).click();

    // 5. Material Dashboard & Open Ended Quiz
    await expect(dashboardIndicator).toBeVisible();

    // Start Open Ended Quiz
    console.log("Starting Open Ended Quiz...");
    const writingModeButton = page.locator('button').filter({ hasText: 'Modo Escrita' }).getByText('Praticar');
    await writingModeButton.click();

    // Answer Questions (Open Ended)
    while (true) {
        if (await page.getByText('Pontuação Final').isVisible()) {
            break;
        }

        // Input text
        const textArea = page.getByPlaceholder('Escreve a tua resposta aqui...');
        if (await textArea.isVisible()) {
            if (!await textArea.isDisabled()) {
                await textArea.fill('Esta é uma resposta de teste gerada automaticamente.');
                await page.getByRole('button', { name: 'Enviar Resposta' }).click();

                // Wait for evaluation result
                await expect(page.locator('button').filter({ hasText: /Próxima|Ver Nota/ })).toBeVisible({ timeout: 60000 });
                await page.locator('button').filter({ hasText: /Próxima|Ver Nota/ }).click();
            }
        } else {
            await page.waitForTimeout(500);
        }
    }

    // 6. Results Page (Open Ended)
    await expect(page.getByText('Pontuação Final')).toBeVisible();
    await expect(page.getByText('MENU PRINCIPAL')).toBeVisible();
});
