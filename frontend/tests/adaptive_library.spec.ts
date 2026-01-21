import { test, expect } from '@playwright/test';
import path from 'path';

test('Library and Adaptive Learning Flow', async ({ page }) => {
    // 1. Initial Load & Login
    await page.goto('/');

    // Wait for either login input or dashboard/upload to avoid race
    // We expect login for a fresh session
    const loginInput = page.getByPlaceholder('Como te chamas?');
    try {
        await expect(loginInput).toBeVisible({ timeout: 10000 });
        const uniqueName = `Adaptive Tester ${Date.now()}`;
        await loginInput.fill(uniqueName);
        await page.getByRole('button', { name: 'CONTINUAR' }).click();
    } catch (e) {
        console.log("Login input not found within timeout, checking if we are already logged in...");
    }

    // 2. Upload First File (Topic A)
    const fileInput = page.locator('input[type="file"]');
    try {
        await expect(page.getByText('Carregar Apontamentos')).toBeVisible({ timeout: 10000 });
    } catch (e) {
        console.log("Carregar Apontamentos not visible. Dumping page text:");
        const text = await page.innerText('body');
        console.log(text);
        throw e;
    }

    // We reuse sample.txt logic, assuming it produces "General" or similar topics.
    // Ideally we'd have two diff files.
    // We will simulate uploading the same file twice but it will be treated as distinct if we could rename it,
    // but browser file upload sends the filename.
    // So we will upload sample.txt.
    await fileInput.setInputFiles(path.join(__dirname, '../../backend/sample.txt'));
    await page.getByRole('button', { name: 'COMEÇAR A ESTUDAR' }).click();
    await expect(page.getByText('Matéria Ativa')).toBeVisible({ timeout: 60000 });

    // 3. Verify Library has 1 item
    // "Biblioteca de Estudo" header check
    await expect(page.getByText('Biblioteca de Estudo')).toBeVisible();
    await expect(page.getByText('sample.txt')).toBeVisible();

    // 4. Act as if we are failing a topic to trigger Adaptive Button
    // This is hard to simulate without taking a quiz.
    // Let's take a quick quiz and FAIL it.
    console.log("Starting Quiz to fail...");
    await page.locator('button').filter({ hasText: 'Modo Clássico' }).getByText('Começar').click();

    // Fail loop
    while (true) {
        if (await page.getByText('Pontuação Final').isVisible()) break;

        // Click WRONG answer (usually B for sample.txt if A is correct, but randomness...)
        // We actually just need to pick *an* answer.
        const options = page.getByRole('button').filter({ hasText: /^[ABCD]$/ });
        if (await options.count() > 0) {
            if (await options.first().isVisible()) {
                await options.nth(1).click(); // Pick B (likely wrong if A is right) or just random
                await page.getByRole('button', { name: /Continuar|Ver Nota/ }).click();
                continue;
            }
        }
        await page.waitForTimeout(100);
    }

    // Return to dashboard
    await page.getByRole('button', { name: 'MENU PRINCIPAL' }).click();
    await expect(page.getByText('Matéria Ativa')).toBeVisible();

    // 5. Verify "Treinar Pontos Fracos" button appears
    // It appears if success < 60%. If we got 0%, it should be there.
    // Note: WeakPointsPanel might need a refresh or is passing props?
    // It fetches on mount. So we might need to rely on auto-refetch or reload?
    // Our App doesn't force refetch of weak points on navigation back to intro... 
    // Wait, WeakPointsPanel uses `useAnalytics` which does `useEffect` on mount.
    // When we switch gameState from 'results' to 'intro', IntroPage remounts?
    // Yes, because `App.jsx` conditionally renders.

    const trainBtn = page.getByRole('button', { name: 'Treinar Pontos Fracos' });
    await expect(trainBtn).toBeVisible({ timeout: 10000 });

    // 6. Click Train
    await trainBtn.click();

    // 7. Verify Quiz Starts
    await expect(page.getByText('Questão 1')).toBeVisible();

    console.log("Adaptive Quiz started successfully.");
});
