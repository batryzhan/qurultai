export default {
  testDir: './e2e',
  timeout: 30000,
  fullyParallel: false,
  workers: 1,
  use: { baseURL: 'http://127.0.0.1:5173', trace: 'retain-on-failure' },
  reporter: 'list',
};
