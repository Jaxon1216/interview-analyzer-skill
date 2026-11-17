const fs = require('node:fs');
const path = require('node:path');

module.exports = function renderFixture() {
  // Synthetic stateful lesson: null preserves the current value, including an empty list.
  const fields = {
    TOPIC_TITLE: '同样是空，为什么一次保留、一次清空？',
    COURSE_LABEL: 'C08 · 状态归并', LESSON_KIND: 'updates',
    GUIDE_HREF: '#mechanism', COURSE_HREF: '#evidence',
    LEARNING_OUTCOME: '看着同一份待办连续接收更新，学会区分“这次没更新”和“新列表为空”。',
    DEMO_TITLE: '这份待办接下来会怎样？',
    SCENE: '页面已经有两条任务。接收一次节点更新，再继续接收下一次，旧值始终是当前画面。',
    EXTRA_STYLES: `
      .todo-sheet { max-width: 30rem; padding: 1.2rem 1.4rem; background: #fafbf8; border-left: 2px solid #acc5b4; }
      .todo-sheet ul { padding-left: 1.25rem; }
      .todo-sheet li { padding: .35rem 0; border-bottom: 1px solid var(--line); }
      .input-line { margin: 1rem 0 0; color: var(--muted); font-size: .88rem; }
      .state-count { margin: 0; color: var(--muted); font-size: .82rem; }
    `,
    DEMO_HTML: `
      <div class="todo-sheet" aria-label="当前待办">
        <p class="state-count">当前 <span data-state="count">2</span> 项</p>
        <ul data-state="todos"><li>收集资料</li><li>整理结果</li></ul>
        <p data-state="empty" hidden>列表已清空</p>
      </div>
      <p class="input-line">最近输入：<code data-state="input">尚未接收</code></p>
      <div class="controls" aria-label="接收更新">
        <button data-action="set-null">接收 null</button>
        <button data-action="set-empty">接收 []</button>
        <button class="secondary" data-action="reset">重新开始</button>
      </div>
      <div class="feedback" role="status" aria-live="polite" data-state="feedback">先选一次输入，观察同一份列表。</div>
    `,
    MODEL_NOTE: '示意数据；只演示字段归并，不执行项目请求。',
    RULE_TITLE: '先问有没有更新，再看新值是什么',
    RULE_HTML: '<p><code>null</code> 在这个契约中表示跳过本次写入；<code>[]</code> 是有效的新列表，替换当前值。因此清空后再收到 null，列表仍然为空。</p><pre><code>if new is None:\n    return current\nreturn new</code></pre>',
    TAKEAWAY: '保留的是当前值，不一定是最开始的两条任务。',
    SOURCE_BASELINE: '稳定的合成教学夹具，验证展示与交互，不证明 DeerFlow 业务逻辑。',
    REFERENCE_HTML: '<ul class="reference-list"><li><code>example/very-long-source-path/streaming-state/merge-thread-state-with-explicit-field-contracts.ts · mergeTodos</code>：示意定位，用于检查长路径布局。</li></ul>',
    DEMO_SCRIPT: `
      (() => {
        const root = document.querySelector('[data-lesson="updates"]');
        const initial = ['收集资料', '整理结果'];
        let current = [...initial];
        const find = name => root.querySelector('[data-state="' + name + '"]');
        function show(input, feedback) {
          const list = find('todos');
          list.replaceChildren(...current.map(title => { const node = document.createElement('li'); node.textContent = title; return node; }));
          find('empty').hidden = current.length !== 0;
          find('count').textContent = current.length;
          find('input').textContent = input;
          find('feedback').textContent = feedback;
        }
        root.querySelector('[data-action="set-null"]').addEventListener('click', () => {
          show('{ todos: null }', '收到 null：跳过写入，保留当前的 ' + current.length + ' 项。');
        });
        root.querySelector('[data-action="set-empty"]').addEventListener('click', () => {
          current = [];
          show('{ todos: [] }', '收到空数组：用新列表替换，当前待办被清空。');
        });
        root.querySelector('[data-action="reset"]').addEventListener('click', () => {
          current = [...initial];
          show('尚未接收', '恢复两条初始任务，可以再换一种输入顺序。');
        });
      })();
    `,
  };
  const template = fs.readFileSync(path.resolve(__dirname, '../../skill/project-interview-skill/assets/topic.html'), 'utf8');
  return template.replace(/\{\{([A-Z_]+)\}\}/g, (_, key) => {
    if (!(key in fields)) throw new Error(`Fixture value missing for ${key}`);
    return fields[key];
  });
};
