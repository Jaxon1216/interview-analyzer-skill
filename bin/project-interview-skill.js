#!/usr/bin/env node
'use strict';

const fs = require('fs');
const os = require('os');
const path = require('path');

const PACKAGE_NAME = 'project-interview-skill';
const SKILL_DIR_NAME = 'project-interview-skill';
const SUPPORTED_PRODUCTS = ['agents', 'trae', 'cursor', 'vscode', 'claude-code', 'codex'];
const COLORS = {
  reset: '\x1b[0m',
  bold: '\x1b[1m',
  dim: '\x1b[2m',
  green: '\x1b[32m',
  blue: '\x1b[34m',
  red: '\x1b[31m',
};
const BUNDLE_ENTRIES = [
  'SKILL.md',
  'references',
  'scripts',
  'README.md',
  'LICENSE',
];

function main() {
  const args = process.argv.slice(2);
  const command = args[0] && !args[0].startsWith('-') ? args.shift() : 'install';

  try {
    if (args.includes('--help') || args.includes('-h')) {
      printHelp();
      return;
    }

    if (command === 'install') {
      install(parseArgs(args));
    } else if (command === 'doctor') {
      doctor(parseArgs(args));
    } else if (command === 'help' || command === '--help' || command === '-h') {
      printHelp();
    } else {
      throw new Error(`Unknown command: ${command}`);
    }
  } catch (error) {
    errorLog(error.message);
    process.exit(1);
  }
}

function parseArgs(args) {
  const options = {
    product: '',
    project: false,
    dryRun: false,
    installAll: false,
    customPath: '',
  };

  for (let index = 0; index < args.length; index += 1) {
    const arg = args[index];

    if (arg === '--project') {
      options.project = true;
    } else if (arg === '--dry-run') {
      options.dryRun = true;
    } else if (arg === '--all') {
      options.installAll = true;
    } else if (arg === '--path') {
      options.customPath = requireValue(args, index, '--path');
      index += 1;
    } else if (arg === '--platform' || arg === '--product') {
      options.product = normalizeProduct(requireValue(args, index, arg));
      index += 1;
    } else if (arg.startsWith('--')) {
      const product = normalizeProduct(arg.slice(2));
      if (SUPPORTED_PRODUCTS.includes(product)) {
        options.product = product;
      } else {
        throw new Error(`Unknown option: ${arg}`);
      }
    } else {
      throw new Error(`Unexpected argument: ${arg}`);
    }
  }

  if (options.installAll && options.product) {
    throw new Error('Use either --all or one product flag, not both.');
  }

  return options;
}

function requireValue(args, index, flag) {
  const value = args[index + 1];
  if (!value || value.startsWith('-')) {
    throw new Error(`Missing value for ${flag}`);
  }
  return value;
}

function normalizeProduct(value) {
  const normalized = value.toLowerCase();
  const aliases = {
    agent: 'agents',
    universal: 'agents',
    claude: 'claude-code',
    claudecode: 'claude-code',
    'claude_code': 'claude-code',
    vs: 'vscode',
    'vs-code': 'vscode',
    code: 'vscode',
  };
  return aliases[normalized] || normalized;
}

function install(options) {
  validatePackage();

  const products = options.installAll
    ? SUPPORTED_PRODUCTS
    : [options.product || 'agents'];
  const installedTargets = new Set();
  const installedProducts = [];

  for (const product of products) {
    validateProduct(product);
    const target = resolveTarget(product, options);
    if (installedTargets.has(target.displayPath)) {
      info(`Skipping ${product}; target already handled: ${target.displayPath}`);
      continue;
    }
    installedTargets.add(target.displayPath);
    installProduct(product, target, options);
    installedProducts.push(product);
  }

  if (!options.dryRun && installedProducts.length > 0) {
    printNextSteps(installedProducts, options);
  }
}

function doctor(options) {
  const cwd = process.cwd();
  const home = os.homedir();

  info(`Package root: ${packageRoot()}`);
  info(`Current project: ${cwd}`);
  info(`Home: ${home}`);
  console.log('');
  console.log('Product targets:');

  for (const product of SUPPORTED_PRODUCTS) {
    const userTarget = resolveTarget(product, { ...options, project: false });
    const projectTarget = resolveTarget(product, { ...options, project: true });
    console.log(`- ${product}`);
    console.log(`  user:    ${userTarget.displayPath}`);
    console.log(`  project: ${projectTarget.displayPath}`);
  }
}

function validateProduct(product) {
  if (!SUPPORTED_PRODUCTS.includes(product)) {
    throw new Error(`Unsupported product "${product}". Supported: ${SUPPORTED_PRODUCTS.join(', ')}`);
  }
}

function resolveTarget(product, options) {
  if (options.customPath) {
    return {
      type: 'bundle',
      product,
      root: path.resolve(options.customPath),
      displayPath: path.resolve(options.customPath),
    };
  }

  const base = options.project ? process.cwd() : os.homedir();

  if (product === 'agents' || product === 'codex') {
    const root = path.join(base, '.agents', 'skills', SKILL_DIR_NAME);
    return { type: 'bundle', product, root, displayPath: root };
  }

  if (product === 'claude-code') {
    const root = path.join(base, '.claude', 'skills', SKILL_DIR_NAME);
    return { type: 'bundle', product, root, displayPath: root };
  }

  if (product === 'trae') {
    const root = options.project
      ? path.join(base, '.trae', 'rules', SKILL_DIR_NAME)
      : path.join(base, '.trae', 'skills', SKILL_DIR_NAME);
    return { type: 'bundle-with-plain-rule', product, root, displayPath: root };
  }

  if (product === 'cursor') {
    const root = path.join(base, '.cursor', 'rules', SKILL_DIR_NAME);
    return { type: 'bundle-with-cursor-rule', product, root, displayPath: root };
  }

  const instructionsFile = options.project
    ? path.join(base, '.github', 'instructions', `${SKILL_DIR_NAME}.instructions.md`)
    : path.join(base, '.copilot', 'instructions', `${SKILL_DIR_NAME}.instructions.md`);
  return {
    type: 'vscode-instructions',
    product,
    root: instructionsFile,
    displayPath: instructionsFile,
  };
}

function installProduct(product, target, options) {
  if (options.dryRun) {
    info(`[dry-run] ${product}: ${target.displayPath}`);
    return;
  }

  if (target.type === 'vscode-instructions') {
    writeVsCodeInstructions(target.root);
    ok(`Installed for ${productLabel(product)}`);
    console.log(`     ${dim(target.root)}`);
    return;
  }

  replaceDirectory(target.root);
  copyBundle(target.root);

  if (target.type === 'bundle-with-cursor-rule') {
    writeCursorRule(path.join(target.root, `${SKILL_DIR_NAME}.mdc`));
  }

  if (target.type === 'bundle-with-plain-rule') {
    writePlainRule(path.join(target.root, `${SKILL_DIR_NAME}.md`));
  }

  ok(`Installed for ${productLabel(product)}`);
  console.log(`     ${dim(target.root)}`);
}

function validatePackage() {
  const skillPath = path.join(packageRoot(), 'SKILL.md');
  if (!fs.existsSync(skillPath)) {
    throw new Error(`Missing SKILL.md at ${skillPath}`);
  }

  const firstLine = fs.readFileSync(skillPath, 'utf8').split(/\r?\n/, 1)[0];
  if (firstLine !== '---') {
    throw new Error('SKILL.md must start with YAML frontmatter (---).');
  }
}

function copyBundle(destination) {
  fs.mkdirSync(destination, { recursive: true });

  for (const entry of BUNDLE_ENTRIES) {
    const source = path.join(packageRoot(), entry);
    if (!fs.existsSync(source)) {
      continue;
    }
    const target = path.join(destination, entry);
    copyRecursive(source, target);
  }
}

function copyRecursive(source, target) {
  const stat = fs.statSync(source);
  if (stat.isDirectory()) {
    fs.mkdirSync(target, { recursive: true });
    for (const child of fs.readdirSync(source)) {
      copyRecursive(path.join(source, child), path.join(target, child));
    }
    return;
  }
  fs.mkdirSync(path.dirname(target), { recursive: true });
  fs.copyFileSync(source, target);
}

function replaceDirectory(directory) {
  const absolute = path.resolve(directory);
  const home = path.resolve(os.homedir());
  if (absolute === path.parse(absolute).root || absolute === home || absolute === process.cwd()) {
    throw new Error(`Refusing to replace unsafe directory: ${absolute}`);
  }
  fs.rmSync(absolute, { recursive: true, force: true });
  fs.mkdirSync(absolute, { recursive: true });
}

function writeCursorRule(filePath) {
  const description = extractDescription();
  const body = skillBody();
  const content = [
    '---',
    `description: ${description}`,
    'globs:',
    'alwaysApply: true',
    '---',
    body,
  ].join('\n');
  writeFile(filePath, content);
}

function writePlainRule(filePath) {
  writeFile(filePath, skillBody());
}

function writeVsCodeInstructions(filePath) {
  const body = skillBody();
  const content = [
    '---',
    "applyTo: '**'",
    '---',
    body,
  ].join('\n');
  writeFile(filePath, content);
}

function writeFile(filePath, content) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, `${content.replace(/\s+$/, '')}\n`, 'utf8');
}

function skillBody() {
  const content = fs.readFileSync(path.join(packageRoot(), 'SKILL.md'), 'utf8');
  const lines = content.split(/\r?\n/);
  let delimiterCount = 0;
  const body = [];

  for (const line of lines) {
    if (line === '---') {
      delimiterCount += 1;
      continue;
    }
    if (delimiterCount >= 2) {
      body.push(line);
    }
  }

  return body.join('\n').trim();
}

function extractDescription() {
  const content = fs.readFileSync(path.join(packageRoot(), 'SKILL.md'), 'utf8');
  const lines = content.split(/\r?\n/);
  let inFrontmatter = false;
  let inDescriptionBlock = false;
  const description = [];

  for (let index = 0; index < lines.length; index += 1) {
    const line = lines[index];
    if (index === 0 && line === '---') {
      inFrontmatter = true;
      continue;
    }
    if (inFrontmatter && line === '---') {
      break;
    }
    if (!inFrontmatter) {
      continue;
    }
    if (inDescriptionBlock) {
      if (/^\s+/.test(line)) {
        description.push(line.trim());
        continue;
      }
      break;
    }
    if (line.startsWith('description:')) {
      const value = line.replace(/^description:\s*/, '').trim();
      if (value === '>-' || value === '>' || value === '') {
        inDescriptionBlock = true;
      } else {
        return value;
      }
    }
  }

  return description.join(' ') || PACKAGE_NAME;
}

function packageRoot() {
  return path.resolve(__dirname, '..');
}

function printHelp() {
  console.log(`${bold(PACKAGE_NAME)}

Usage:
  npx ${PACKAGE_NAME} install [--agents|--trae|--cursor|--vscode|--claude-code|--codex]
  npx ${PACKAGE_NAME} install --project [--trae|--cursor|--vscode|--claude-code|--codex]
  npx ${PACKAGE_NAME} install --all [--project]
  npx ${PACKAGE_NAME} doctor

Options:
  --agents         Install to ~/.agents/skills/ (default user-level target)
  --trae           Install for Trae
  --cursor         Install for Cursor
  --vscode         Install VS Code Copilot instructions
  --claude-code    Install for Claude Code
  --codex          Install to .agents/skills for Codex
  --project        Install under the current project instead of the user home
  --all            Install every supported target
  --path PATH      Install the full skill bundle to a custom path
  --dry-run        Print target paths without writing files
  -h, --help       Show this help
`);
}

function info(message) {
  console.log(`${color('[info]', 'blue')} ${message}`);
}

function ok(message) {
  console.log(`${color('[ok]', 'green')} ${message}`);
}

function errorLog(message) {
  console.error(`${color('[error]', 'red')} ${message}`);
}

function printNextSteps(products, options) {
  const targetText = products.map(productLabel).join(', ');
  console.log('');
  ok(`${PACKAGE_NAME} is ready for ${targetText}.`);
  console.log('');
  console.log(bold('Next:'));
  console.log(`  1. Restart ${nextStepProductText(products)}.`);
  console.log('  2. Open your project root.');
  console.log(`  3. Start a new chat with ${bold('/project-interview-skill')}.`);
  if (!options.project) {
    console.log(`  4. For one-project-only setup, run ${dim(`npx ${PACKAGE_NAME} install --project --<product>`)} in that project.`);
  }
}

function nextStepProductText(products) {
  if (products.length === 1) {
    return productLabel(products[0]);
  }
  return 'the target IDE or Agent';
}

function productLabel(product) {
  const labels = {
    agents: 'Generic Agent',
    trae: 'Trae',
    cursor: 'Cursor',
    vscode: 'VS Code',
    'claude-code': 'Claude Code',
    codex: 'Codex',
  };
  return labels[product] || product;
}

function bold(text) {
  return color(text, 'bold');
}

function dim(text) {
  return color(text, 'dim');
}

function color(text, colorName) {
  if (process.env.NO_COLOR || !process.stdout.isTTY) {
    return text;
  }
  return `${COLORS[colorName]}${text}${COLORS.reset}`;
}

main();
