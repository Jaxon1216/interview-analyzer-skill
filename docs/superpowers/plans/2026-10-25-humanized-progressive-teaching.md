# 自然表达与按需 HTML 教学实施计划

> **For agentic workers:** 使用 subagent-driven-development 执行独立任务，并在完成后复核事实、范围与安装产物。

**Goal:** 在现有 Skill 内适配 Humanizer 和 teach，保留首轮完整 Markdown，增加按文档/课程/小节生成 HTML 的后续入口。

**Architecture:** 主 Skill 提前路由默认资料与 HTML 深化；共同表达规则和 HTML 专属规则分置 references。文档尾部提示词传递真实路径和基线；HTML 成功生成后才登记链接。

**Tech Stack:** Markdown Skill Bundle、现有 Node.js 安装器、Python unittest；生成的 HTML 使用内联 CSS/JavaScript。

## Global Constraints

- 首次继续生成导学、面经与全部核心 Markdown 课程；用户指定部分范围时服从该范围。
- HTML 仅按明确请求生成；不强制测验、练习、访谈或学习档案，不把生成过当作学会。
- 保留事实、指标口径、证据限定、代码、链接、既有 B/Q/C 编号与用户笔记。
- Bundle 自包含，上游固定来源和 MIT 许可随 references 发布；不依赖另装 Skill。
- 单文件 HTML 默认离线，无 CDN、远程字体或构建依赖；浏览器验证与结构校验分别报告。
- 不改变既有 build_prompt CLI 参数，不增加平台、发布、部署或全局配置。

## Task 1：行为基线与教学规则

**Files:** `skill/project-interview-skill/SKILL.md`；新增 `references/rules/writing-style.md`、`interactive-teaching.md`、`references/upstream/`；更新 `course-design.md`、`oral-and-resume-patterns.md`、`output-templates.md`、`scripts/build_prompt.py`。

- [x] 先在独立上下文用当前 Skill 生成指定课学习入口，保存首次产物，核对缺少 HTML 模式与跨聊天入口的基线问题。
- [x] 写共同表达规则：直接表达、删空泛总结、事实与结构守恒、区分简历/口播/课程文体，提供中文改写对照。
- [x] 写 HTML 规则：解析已有文档与范围、读取源码和基线、教学深化、离线页面、稳定路径、笔记保护、独立尾部登记与实际检查；不复制上游独立教学仓库模式。
- [x] 主 Skill 在整套生成前路由，description 可发现 HTML 请求；引用两份规则，默认流程保留完整课程。
- [x] 课程模板加入来源基线和实际路径提示词；HTML 入口在独立尾部，不混入原 B/Q/C 映射字段；更新 build_prompt 摘要。
- [x] 运行现有 Bundle 相对链接与 prompt 测试；独立行为复跑并对照基线，检查入口不再依赖聊天记忆。

## Task 2：VS Code 安装自包含修复

**Files:** `bin/project-interview-skill.js`、新增 `tests/test_installer.py`。

**Interface:** 既有命令 `node bin/project-interview-skill.js install --vscode --project`、用户级 `--vscode` 与 `doctor` 保持可用。项目级伴随 Bundle 为 `.github/instructions/project-interview-skill/`；用户级为 `.copilot/instructions/project-interview-skill/`。instructions 引导读取相邻 Bundle 的 `SKILL.md`，该 Bundle 内相对引用保持不变。

- [x] 用临时目录跑真实安装器，先写失败测试：instructions 的实际入口可解析，references 与 scripts 可访问，安装不会删除旁边其他文件。
- [x] 仅修复 VS Code 分支：复制完整 Bundle 到独立伴随目录，写薄 instructions 入口，不将 references 平铺到共享目录。更新 doctor 与必要说明。
- [x] 定向测试安装、重复安装、dry-run、既有通用安装；不改动真实用户目录。
- [x] 运行完整 unittest，保存红/绿证据并独立代码复核。

## Task 3：用法、行为评测与交付

**Files:** `README.md`、`README_EN.md`、`tests/README.md`、新增 `tests/evals/progressive-teaching.json`、`docs/testing/2026-10-25-progressive-teaching.md` 与必要评测产物。

- [x] 文档解释默认 Markdown 与后续 HTML 的关系，给出实际使用提示词，说明 /teach 是方法来源而非新增命令。
- [x] 行为用例覆盖默认交付、跨聊天单课/小节、普通追问、重复生成与笔记、多项目、源码漂移、自然表达事实守恒；执行者只拿请求与 Skill，审读者再看 checks。
- [x] 在独立临时材料上生成真实 HTML，检查静态链接/依赖及脚本路径，核对教学模型与实测边界；浏览器 file:// 打开被 URL 安全策略拒绝，实际渲染、原生键盘/焦点、控制台/网络及导航均如实记为未验证，未绕过限制。
- [x] 运行 `npm test`、`npm run pack:check`、Skill quick_validate、`git diff --check`；另行审读中文正文，不将结构测试当作语义通过。
- [x] 整体独立复核，修复重要问题后再报告完成；记录未执行或环境限制，不自动发布 npm 或推送远程。

## 执行记录

- 2026-10-25：设计已获用户批准；仓库基线 29 项测试通过；VS Code 支持文件缺失已在临时目录复现。
- 开发分支：`codex/humanized-progressive-teaching`。托管 worktree 的写入受沙箱限制，按工作流回退原目录；未使用的 worktree 已归档。

- 验收：H1、H2、H3、H4、W1 的独立首稿已保存并审读；H5 消歧/源码漂移未实跑。整体独立审阅的一项评测准备问题已解决；浏览器限制见验证记录。
