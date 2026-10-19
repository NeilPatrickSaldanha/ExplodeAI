import { defineConfig, devices } from '@playwright/test'

const API_PORT = Number(process.env.E2E_API_PORT ?? 8100)
const WEB_PORT = Number(process.env.E2E_WEB_PORT ?? 5174)

/**
 * E2E runs its own backend (isolated SQLite file) and frontend on separate ports,
 * so it never touches the developer's data. No API keys are needed or used.
 */
export default defineConfig({
  testDir: './e2e',
  timeout: 45_000,
  expect: { timeout: 10_000 },
  fullyParallel: false,
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? 'github' : 'list',
  use: {
    baseURL: `http://127.0.0.1:${WEB_PORT}`,
    trace: 'retain-on-failure',
  },
  projects: [
    { name: 'desktop', use: { ...devices['Desktop Chrome'], viewport: { width: 1360, height: 900 } }, testIgnore: /mobile\.spec\.ts/ },
    { name: 'mobile', use: { ...devices['Pixel 7'] }, testMatch: /mobile\.spec\.ts/ },
  ],
  webServer: [
    {
      command: `rm -f ./data/e2e-${API_PORT}.sqlite3 && uv run uvicorn app.main:app --host 127.0.0.1 --port ${API_PORT}`,
      cwd: '../backend',
      url: `http://127.0.0.1:${API_PORT}/api/health`,
      env: {
        DATABASE_URL: `sqlite:///./data/e2e-${API_PORT}.sqlite3`,
        CORS_ORIGINS: `http://127.0.0.1:${WEB_PORT}`,
        AI_FEATURES_ENABLED: 'false',
        // Never reach a paid provider from e2e, whatever backend/.env holds.
        OPENAI_API_KEY: '',
        GEMINI_API_KEY: '',
        ANTHROPIC_API_KEY: '',
      },
      reuseExistingServer: false,
      timeout: 60_000,
    },
    {
      command: `npx vite --port ${WEB_PORT} --strictPort`,
      url: `http://127.0.0.1:${WEB_PORT}`,
      env: { VITE_API_PROXY: `http://127.0.0.1:${API_PORT}` },
      reuseExistingServer: false,
      timeout: 60_000,
    },
  ],
})
