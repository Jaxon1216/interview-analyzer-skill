const path = require('node:path');
const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  testDir: __dirname,
  testMatch: '*.spec.cjs',
  outputDir: path.resolve(__dirname, '../../.test-runs/html'),
  snapshotPathTemplate: path.join(__dirname, 'snapshots', `{projectName}-{platform}-${process.arch}`, '{arg}{ext}'),
  // Missing baselines must fail; accepting a new appearance is an explicit step.
  updateSnapshots: 'none',
  reporter: [['list']],
  workers: 1,
  retries: 0,
  timeout: 30000,
  expect: { toHaveScreenshot: { animations: 'disabled', maxDiffPixels: 0 } },
  use: {
    browserName: 'chromium', headless: true, locale: 'zh-CN',
    timezoneId: 'Asia/Shanghai', colorScheme: 'light', reducedMotion: 'reduce',
    trace: 'retain-on-failure', screenshot: 'only-on-failure',
  },
  projects: [
    { name: 'desktop', use: { viewport: { width: 1440, height: 1000 } } },
    { name: 'mobile', use: { viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true } },
  ],
});
