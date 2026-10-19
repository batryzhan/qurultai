import { test, expect } from '../frontend/node_modules/@playwright/test/index.mjs';
import fs from 'node:fs';
import path from 'node:path';

test('first-run onboarding, simulated council, stored evidence and synthesis', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByRole('heading', { name: 'Үш би. Үш көзқарас.' })).toBeVisible();
  await page.getByLabel('Language', { exact: true }).selectOption('en');
  await page.getByRole('button', { name: /Start exploring/ }).click();
  await expect(page.getByText('Meet your council')).toBeVisible();
  await expect(page.locator('.role-card img')).toHaveCount(3);
  expect(await page.locator('.role-card img').evaluateAll(imgs => imgs.every(img => (img as HTMLImageElement).complete && (img as HTMLImageElement).naturalWidth > 0))).toBe(true);
  await page.getByRole('button', { name: 'Continue', exact: true }).click();
  await expect(page.getByText('From question to understanding')).toBeVisible();
  await page.getByRole('button', { name: 'Continue', exact: true }).click();
  await page.getByRole('button', { name: /Enter workspace/ }).click();
  await page.getByLabel('Your question', { exact: true }).fill('What is the Transformer attention architecture?');
  await page.getByRole('button', { name: /Convene the council/ }).click();
  await expect(page).toHaveURL(/\/sessions\/[^/]+$/);
  await expect(page.locator('.session-meta')).toContainText('completed');
  await expect(page.locator('.session-meta')).toContainText('Demo / Simulated');
  await expect(page.locator('.argument')).toHaveCount(12);
  await page.getByRole('link', { name: /^Evidence/ }).click();
  await expect(page.getByText('Attention Is All You Need')).toBeVisible();
  await page.getByRole('link', { name: 'Disagreements', exact: true }).click();
  await expect(page.getByText('No disagreements recorded')).toBeVisible();
  await page.getByRole('link', { name: 'Synthesis', exact: true }).click();
  await expect(page.locator('.synthesis-panel')).toContainText('SIMULATED');
  await page.reload();
  await expect(page.locator('.synthesis-panel')).toContainText('SIMULATED');
});

test('imports fixture, runs every benchmark strategy and exports stored results', async ({ page, request }) => {
  await page.addInitScript(() => {
    localStorage.setItem('qurultai.onboarded', 'true');
    localStorage.setItem('qurultai.language', 'en');
  });
  const fixture = JSON.parse(fs.readFileSync(path.join(process.cwd(), '../datasets/examples/arithmetic_fixture.json'), 'utf8'));
  fixture.name = 'Browser fixture ' + Date.now();
  const imported = await request.post('/api/v1/datasets/import', { data: fixture });
  expect(imported.status()).toBe(201);
  const dataset = await imported.json();
  await page.goto('/benchmarks');
  const datasetSelect = page.getByRole('combobox', { name: 'Dataset', exact: true });
  await expect(datasetSelect).toBeVisible();
  await datasetSelect.selectOption(dataset.id);
  await page.getByRole('button', { name: /Run experiment/ }).click();
  await expect(page.locator('.benchmark-results')).toBeVisible();
  const runs = await (await request.get('/api/v1/benchmarks')).json();
  const run = runs.find((r: {dataset_id: string}) => r.dataset_id === dataset.id);
  expect(run.simulated).toBe(true);
  await expect.poll(async () => (await (await request.get('/api/v1/benchmarks/' + run.id)).json()).status).toBe('completed');
  const saved = await (await request.get('/api/v1/exports/benchmarks/' + run.id)).json();
  expect(saved.results.length).toBe(12);
  expect(Object.keys(saved.metrics).sort()).toEqual(['debate', 'majority', 'single']);
  const csv = await request.get('/api/v1/exports/benchmarks/' + run.id + '?format=csv');
  expect(await csv.text()).toContain('question_id,strategy,raw_answer');
});

test('mobile council has no horizontal document overflow', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.addInitScript(() => {
    localStorage.setItem('qurultai.onboarded', 'true');
    localStorage.setItem('qurultai.language', 'kk');
  });
  await page.goto('/council');
  await expect(page.locator('#question')).toBeVisible();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
});
