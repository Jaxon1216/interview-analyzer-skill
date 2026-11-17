const fs = require('node:fs');
const path = require('node:path');
const { fileURLToPath, pathToFileURL } = require('node:url');
const { test, expect } = require('@playwright/test');
const renderFixture = require('./fixture.cjs');

async function loadOffline(page, file) {
  const errors = [];
  page.on('pageerror', error => errors.push(error.message));
  page.on('console', message => { if (message.type() === 'error') errors.push(message.text()); });
  await page.route(/^https?:\/\//, route => {
    errors.push(`Unexpected network dependency: ${route.request().url()}`);
    return route.abort();
  });
  await page.goto(pathToFileURL(file).href);
  await page.evaluate(() => document.fonts.ready);
  await expect(page.locator('h1')).toBeVisible();
  await expect(page.locator('body')).not.toContainText(/\{\{[A-Z_]+\}\}/);
  return errors;
}

async function expectNoOverflow(page) {
  const dimensions = await page.evaluate(() => ({
    width: document.documentElement.clientWidth,
    content: document.documentElement.scrollWidth,
  }));
  expect(dimensions.content, 'Document must fit its viewport').toBeLessThanOrEqual(dimensions.width + 1);
}

async function checkLinks(page, file) {
  for (const href of await page.locator('a[href]').evaluateAll(nodes => nodes.map(node => node.href))) {
    if (!href.startsWith('file:')) continue;
    expect(fs.existsSync(fileURLToPath(href)), `Missing local link: ${href}`).toBe(true);
    const url = new URL(href);
    if (url.hash && fileURLToPath(url) === file) {
      const id = decodeURIComponent(url.hash.slice(1));
      const exists = await page.evaluate(anchor => Boolean(document.getElementById(anchor)) || document.getElementsByName(anchor).length > 0, id);
      expect(exists, `Missing in-page anchor: ${href}`).toBe(true);
    }
  }
}

async function capture(page, testInfo, name) {
  await expectNoOverflow(page);
  const screenshot = testInfo.outputPath(`${name}.png`);
  await page.screenshot({ path: screenshot, fullPage: true, animations: 'disabled' });
  await testInfo.attach(name, { path: screenshot, contentType: 'image/png' });
}

async function cases(page) {
  const controls = await page.locator('.choices input[type="radio"][aria-controls]').evaluateAll(nodes => (
    nodes.map(node => ({ id: node.id, group: node.name, target: node.getAttribute('aria-controls') }))
  ));
  expect(controls.length, 'Legacy radio adapter requires at least two cases').toBeGreaterThanOrEqual(2);
  return controls;
}

async function choose(page, id) {
  const controls = await cases(page);
  const selected = controls.find(control => control.id === id);
  expect(selected, `Missing radio case: ${id}`).toBeTruthy();
  const primaryLabel = page.locator(`.choices > label[for=${JSON.stringify(id)}]`);
  await expect(primaryLabel).toHaveCount(1);
  await primaryLabel.click();
  await expect(page.locator(`input[id=${JSON.stringify(id)}]`)).toBeChecked();
  for (const control of controls.filter(control => control.group === selected.group)) {
    const panel = page.locator(`[id=${JSON.stringify(control.target)}]`);
    if (control.id === id) await expect(panel).toBeVisible();
    else await expect(panel).toBeHidden();
  }
  await expectNoOverflow(page);
}

async function printLesson(page) {
  await page.evaluate(() => window.dispatchEvent(new Event('beforeprint')));
  await page.emulateMedia({ media: 'print' });
  await expect(page.locator('#mechanism, .mechanism, .takeaway').first()).toBeVisible();
  await expect(page.locator('#evidence, .evidence, .reference').first()).toBeVisible();
}

const action = (page, name) => page.locator(`[data-action="${name}"]`);
const state = (page, name) => page.locator(`[data-state="${name}"]`);

test('template: evolving state, cause feedback, keyboard and print', async ({ page }, testInfo) => {
  const file = testInfo.outputPath('fixture.html');
  fs.writeFileSync(file, renderFixture(), 'utf8');
  const errors = await loadOffline(page, file);
  await expect(state(page, 'todos').locator('li')).toHaveCount(2);
  const start = await action(page, 'set-null').boundingBox();
  expect(start.y, 'A meaningful action must appear in the first viewport').toBeLessThan(page.viewportSize().height);
  await expect(page).toHaveScreenshot('initial.png', { fullPage: true });
  await action(page, 'set-null').click();
  await expect(state(page, 'todos').locator('li')).toHaveCount(2);
  await expect(state(page, 'feedback')).toContainText('保留当前的 2 项');
  await action(page, 'set-empty').click();
  await expect(state(page, 'todos').locator('li')).toHaveCount(0);
  await expect(state(page, 'empty')).toBeVisible();
  await expect(state(page, 'feedback')).toContainText('清空');
  await expect(page).toHaveScreenshot('cleared.png', { fullPage: true });
  // A real state transition: null preserves the empty current list, not a canned initial answer.
  await action(page, 'set-null').click();
  await expect(state(page, 'todos').locator('li')).toHaveCount(0);
  await expect(state(page, 'feedback')).toContainText('保留当前的 0 项');
  await action(page, 'reset').focus();
  await page.keyboard.press('Space');
  await expect(state(page, 'todos').locator('li')).toHaveCount(2);
  await expect(state(page, 'feedback')).toContainText('恢复');
  await expectNoOverflow(page);
  await printLesson(page);
  await expect(page.locator('#evidence .reference-list')).toBeVisible();
  expect(errors).toEqual([]);
});

test('legacy adapter: extra branches and secondary labels', async ({ page }) => {
  await page.setContent(`<style>.case{display:none} #case-a:checked~.case-a,#case-b:checked~.case-b,#case-c:checked~.case-c{display:block}</style>
    <div class="choices">
      <input type="radio" name="case" id="case-a" aria-controls="result-a" checked><label for="case-a">A</label>
      <input type="radio" name="case" id="case-b" aria-controls="result-b"><label for="case-b">B</label>
      <input type="radio" name="case" id="case-c" aria-controls="result-c"><label for="case-c">C</label>
      <div class="case case-a" id="result-a">A result</div><div class="case case-b" id="result-b">B result</div>
      <div class="case case-c" id="result-c">C result<label for="case-a">Return to A</label></div>
    </div>`);
  expect(await cases(page)).toHaveLength(3);
  await choose(page, 'case-c');
  await choose(page, 'case-a');
});

async function checkSkills(page, testInfo) {
  const root = page.locator('[data-lesson="skills"]');
  const tools = state(page, 'available-tools');
  const result = page.locator('[data-status="call-result"]');
  const mode = name => page.locator(`button[data-mode="${name}"]`);
  await expect(mode('slash')).toHaveAttribute('aria-pressed', 'true');
  await expect(root).toHaveAttribute('data-b-read', 'false');
  await expect(tools).toContainText('bash');
  await expect(tools).toHaveAttribute('data-tools', 'bash');
  await action(page, 'load-b').click();
  await expect(root).toHaveAttribute('data-b-read', 'true');
  await expect(state(page, 'b-contribution')).toHaveAttribute('data-included', 'false');
  await expect(tools).toHaveAttribute('data-tools', 'bash');
  await action(page, 'call-write').click();
  await expect(result).toHaveAttribute('data-outcome', 'blocked');
  await capture(page, testInfo, 'slash-read-b-write-blocked');
  // Keep B and the attempted tool fixed; change only A's activation source.
  await mode('autonomous').click();
  await expect(root).toHaveAttribute('data-b-read', 'true');
  await expect(state(page, 'b-contribution')).toHaveAttribute('data-included', 'true');
  await expect(tools).toContainText('write_file');
  await expect(tools).toHaveAttribute('data-tools', 'bash,write_file');
  await expect(result).toHaveAttribute('data-tool', 'write_file');
  await expect(result).toHaveAttribute('data-outcome', 'allowed');
  await capture(page, testInfo, 'autonomous-same-b-write-allowed');
  await mode('slash').click();
  await expect(result).toHaveAttribute('data-outcome', 'blocked');
  await action(page, 'call-bash').click();
  await expect(result).toHaveAttribute('data-outcome', 'allowed');
  await expect(result).toHaveAttribute('data-tool', 'bash');
  await action(page, 'reset').focus();
  await page.keyboard.press('Space');
  await expect(root).toHaveAttribute('data-b-read', 'false');
  await expect(mode('slash')).toHaveAttribute('aria-pressed', 'true');
  await expect(result).toHaveAttribute('data-outcome', 'idle');
  await capture(page, testInfo, 'reset');
}

async function checkLease(page, testInfo) {
  // Contract follows the visible owner graph; assert full lifecycles in both orders.
  const releaseCount = state(page, 'release-count');
  const client = state(page, 'client');
  const simulation = state(page, 'simulation');
  await expect(releaseCount).toHaveText('0');
  await expect(client).toHaveAttribute('data-status', 'available');
  await action(page, 'finish-main').click();
  await expect(releaseCount).toHaveText('0');
  await expect(client).toHaveAttribute('data-status', 'available');
  await expect(simulation).toHaveAttribute('data-holder-count', '1');
  await expect(simulation).toHaveAttribute('data-pending-release', 'true');
  await expect(page.locator('[data-owner="main"]')).toHaveAttribute('data-status', 'done');
  await expect(page.locator('[data-owner="child"]')).toHaveAttribute('data-status', 'running');
  await capture(page, testInfo, 'main-done-child-still-using');
  await state(page, 'counterexample').locator('summary').click();
  await action(page, 'premature-release').click();
  await expect(client).toHaveAttribute('data-status', 'error');
  await expect(page.locator('[data-owner="child"]')).toHaveAttribute('data-status', 'blocked');
  await expect(simulation).toHaveAttribute('data-holder-count', '1');
  await capture(page, testInfo, 'counterfactual-breaks-still-running-child');
  await action(page, 'restore').click();
  await expect(client).toHaveAttribute('data-status', 'available');
  await expect(releaseCount).toHaveText('0');
  await expect(simulation).toHaveAttribute('data-pending-release', 'true');
  await action(page, 'finish-child').click();
  await expect(releaseCount).toHaveText('1');
  await expect(client).toHaveAttribute('data-status', 'released');
  await expect(action(page, 'finish-main')).toBeDisabled();
  await expect(action(page, 'finish-child')).toBeDisabled();
  await capture(page, testInfo, 'last-owner-left-released');
  await action(page, 'reset').click();
  await action(page, 'finish-child').click();
  await expect(releaseCount).toHaveText('0');
  await expect(client).toHaveAttribute('data-status', 'available');
  // This child borrows the parent's client without proposing release itself.
  await expect(simulation).toHaveAttribute('data-pending-release', 'false');
  await action(page, 'finish-main').click();
  await expect(releaseCount).toHaveText('1');
  await expect(client).toHaveAttribute('data-status', 'released');
  await action(page, 'reset').focus();
  await page.keyboard.press('Space');
  await expect(releaseCount).toHaveText('0');
  await expect(client).toHaveAttribute('data-status', 'available');
  await expect(simulation).toHaveAttribute('data-holder-count', '2');
  await capture(page, testInfo, 'reset');
}

function htmlFiles(dir) {
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap(entry => {
    const file = path.join(dir, entry.name);
    if (entry.isDirectory()) return htmlFiles(file);
    return entry.isFile() && entry.name.endsWith('.html') ? [file] : [];
  }).sort();
}

async function checkSandboxLeases(page, testInfo) {
  const root = page.locator('[data-lesson="sandbox-leases"]');
  const model = page.locator('.lesson-stage');
  const next = page.locator('#advance-event');
  const reset = page.locator('#reset-demo');
  const releases = page.locator('#provider-release-count');
  const entry = await next.boundingBox();
  expect(entry.y + entry.height, 'The first sandbox action must be visible without scrolling').toBeLessThanOrEqual(page.viewportSize().height);
  await page.locator('#sandbox-node').evaluate(node => { window.originalSandboxNode = node; });
  for (const order of ['lead-first', 'child-first']) {
    await reset.click();
    await expect(root).toHaveAttribute('data-step', '0');
    await expect(model).toHaveAttribute('data-holders', '');
    await expect(releases).toHaveText('0');
    await next.click();
    await expect(model).toHaveAttribute('data-holders', 'lead');
    await expect(releases).toHaveText('0');
    await next.click();
    await expect(model).toHaveAttribute('data-holders', 'lead,child');
    // Keep both holders and the client fixed; change only the finish order.
    await page.locator(`input[name="end-order"][value="${order}"]`).check();
    await expect(root).toHaveAttribute('data-step', '2');
    await expect(model).toHaveAttribute('data-holders', 'lead,child');
    await capture(page, testInfo, `${order}-both-holders`);
    const first = order === 'lead-first' ? 'lead' : 'child';
    const remaining = first === 'lead' ? 'child' : 'lead';
    await next.click();
    await expect(model).toHaveAttribute('data-holders', remaining);
    await expect(releases).toHaveText('0');
    await expect(page.locator(`#${first}-connection`)).toHaveAttribute('data-state', 'removed');
    await expect(page.locator(`#${remaining}-connection`)).toHaveAttribute('data-state', 'holding');
    await expect(page.locator('#feedback-result')).toContainText(remaining);
    await capture(page, testInfo, `${order}-one-holder-left`);
    await next.click();
    await expect(model).toHaveAttribute('data-holders', '');
    await expect(releases).toHaveText('1');
    await expect(next).toBeDisabled();
    expect(await page.locator('#sandbox-node').evaluate(node => node === window.originalSandboxNode)).toBe(true);
    await capture(page, testInfo, `${order}-last-holder-released`);
  }
  await reset.focus();
  await page.keyboard.press('Space');
  await expect(root).toHaveAttribute('data-step', '0');
  await expect(releases).toHaveText('0');
  await capture(page, testInfo, 'sandbox-leases-reset');
}

async function checkSkillLoading(page, testInfo) {
  const next = page.locator('#next');
  const reset = page.locator('#reset');
  const bodies = page.locator('#body-set');
  const source = page.locator('#chosen-source');
  const web = page.locator('#tool-web_search');
  await expect(bodies).toHaveText('∅');
  await expect(source).toHaveText('无激活来源');
  await expect(web).not.toHaveClass(/removed/);
  await next.click();
  await expect(bodies).toHaveText('{ report }');
  await expect(source).toHaveText('可信 skill_context');
  await expect(web).toHaveClass(/removed/);
  await capture(page, testInfo, 'passive-report-loaded-web-removed');
  await next.click();
  await expect(bodies).toHaveText('{ report, web-help }');
  await expect(web).not.toHaveClass(/removed/);
  await expect(next).toBeDisabled();
  await capture(page, testInfo, 'passive-two-declarations-unioned');
  await page.locator('#slash-start').click();
  await expect(bodies).toHaveText('{ report }');
  await expect(source).toHaveText('slash：report');
  await next.click();
  await expect(bodies).toHaveText('{ report, web-help }');
  await expect(page.locator('#context-set')).toContainText('web-help');
  await expect(web).toHaveClass(/removed/);
  await expect(page.locator('#feedback-text')).toContainText('slash');
  await capture(page, testInfo, 'slash-has-both-bodies-but-keeps-report-policy');
  await reset.click();
  await page.locator('#discovery-option summary').click();
  await page.locator('#deferred').check();
  await expect(page.locator('#report-level')).toHaveText('名称');
  await expect(bodies).toHaveText('∅');
  await expect(next).toBeDisabled();
  await page.locator('#describe').click();
  await expect(page.locator('#report-level')).toHaveText('元信息');
  await expect(next).toBeEnabled();
  await expect(bodies).toHaveText('∅');
  await expect(source).toHaveText('无激活来源');
  await expect(web).not.toHaveClass(/removed/);
  await capture(page, testInfo, 'deferred-description-does-not-activate');
  await next.click();
  await expect(source).toHaveText('可信 skill_context');
  await expect(web).toHaveClass(/removed/);
  await reset.focus();
  await page.keyboard.press('Space');
  await expect(bodies).toHaveText('∅');
  await expect(source).toHaveText('无激活来源');
  await capture(page, testInfo, 'skill-loading-reset');
}

if (process.env.TOPIC_ROOT) {
  const files = htmlFiles(process.env.TOPIC_ROOT);
  if (!files.length) throw new Error(`No HTML files in ${process.env.TOPIC_ROOT}`);
  for (const file of files) {
    test(`generated: ${path.relative(process.env.TOPIC_ROOT, file)}`, async ({ page }, testInfo) => {
      const errors = await loadOffline(page, file);
      await checkLinks(page, file);
      const kind = await page.locator('main').getAttribute('data-lesson');
      if (kind === 'skills') await checkSkills(page, testInfo);
      else if (kind === 'lease') await checkLease(page, testInfo);
      else if (kind === 'sandbox-leases') await checkSandboxLeases(page, testInfo);
      else if (kind === 'skill-loading') await checkSkillLoading(page, testInfo);
      else {
        // Explicitly supported old format. New widgets need a scenario-specific adapter.
        const controls = await cases(page);
        for (const [index, control] of controls.entries()) {
          await choose(page, control.id);
          await capture(page, testInfo, `legacy-case-${index + 1}`);
        }
      }
      await printLesson(page);
      if (!kind) {
        for (const control of await cases(page)) {
          await expect(page.locator(`[id=${JSON.stringify(control.target)}]`)).toBeVisible();
        }
      }
      expect(errors).toEqual([]);
    });
  }
}
