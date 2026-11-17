const fs = require('node:fs');
const path = require('node:path');
const { spawnSync } = require('node:child_process');

const args = process.argv.slice(2);
const forwarded = [];
const env = { ...process.env };
for (let i = 0; i < args.length; i++) {
  if (args[i] === '--topic-root') {
    if (!args[i + 1] || args[i + 1].startsWith('--')) {
      console.error('--topic-root requires a directory');
      process.exit(1);
    }
    const root = path.resolve(args[++i]);
    if (!fs.existsSync(root) || !fs.statSync(root).isDirectory()) {
      console.error(`Topic directory does not exist: ${root}`);
      process.exit(1);
    }
    env.TOPIC_ROOT = root;
  } else if (args[i] === '--update-snapshots') {
    forwarded.push('--update-snapshots');
  } else {
    console.error(`Unknown option: ${args[i]}`);
    process.exit(1);
  }
}

// Never open a browser or HTML report, including after failure.
const result = spawnSync(process.execPath, [
  require.resolve('@playwright/test/cli'), 'test',
  '--config', path.join(__dirname, 'playwright.config.cjs'), ...forwarded,
], { stdio: 'inherit', env });
if (result.error) console.error(result.error.message);
process.exit(result.status ?? 1);
