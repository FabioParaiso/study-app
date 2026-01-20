import { test, expect } from '@playwright/test';

test('Student Journey: Login and Check Material', async ({ page }) => {
    // 1. Go to home (Login page)
    await page.goto('/');

    // 2. Login
    // Using exact placeholder from StudentLogin.jsx
    await page.getByPlaceholder('Como te chamas?').fill('E2E Student');
    await page.getByRole('button', { name: 'CONTINUAR' }).click();

    // 3. Verify Intro Screen
    // IntroScreen usually shows "Olá, [Name]" or similar. 
    // Based on IntroScreen code (I read App.jsx which passes student prop), it likely welcomes the user.
    // I'll check for the name visibility.
    await expect(page.getByText('E2E Student')).toBeVisible();

    // 4. Check for key elements of IntroScreen
    // e.g., "Carregar Ficheiro" or "Escolher Tópico"
    await expect(page.getByText('Carregar Ficheiro')).toBeVisible();
});
