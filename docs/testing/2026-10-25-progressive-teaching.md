# 自然表达与渐进式 HTML 教学验证

日期：2026-10-25。起始仓库：`106ea5f`（1.4.2）。评测为本次单次行为观察，不代表所有模型、项目和浏览器均已通过。

## 基线

独立 agent 仅使用旧版 Skill、课程规则与模板，按“C03 重试与状态，提供可在新聊天生成离线 HTML 的学习入口”请求生成[首次结果](samples/progressive-teaching/baseline-entry.md)。旧规则没有明确 HTML 模式、跨聊天课程定位、离线资源及页面检查契约。该 agent 临时补了一段含本机 Skill 绝对路径和输入事实的提示词，无法定位未提供的既有课程。这是本次实际观察到的缺口。

此基线不证明旧模型无法生成 HTML，也不证明原来的中文材料必然有风格问题；它说明现有 Bundle 没有对应的可移植行为契约。

## 结构与安装

- 初始 `npm test`：29/29；安装器新增 8 项真实 Node CLI 回归后：37/37。
- VS Code 回归首次 5 fail / 3 pass：入口未引用 Bundle、支持文件缺失、路径未报告。修复后 8/8；重复安装保留邻居文件，dry-run 无写入，默认、自定义与全部产品安装可达完整 Bundle。
- 用户级只运行 doctor/dry-run 和状态比对，没有写真实 HOME；未启动真实 VS Code Copilot 对话。
- 合成 fixture 的 Markdown 完整交付结构通过 `validate_output.py`；本次 Skill 通过 `quick_validate.py`；Node 语法与 diff 空白检查通过。
- `npm run pack:check` 首次因默认 npm 缓存无写权限失败；使用 `npm --cache /private/tmp/interview-skill-npm-cache run pack:check` 后通过。27 个发布文件包含两份新规则、来源与两份 MIT 许可，不含评测/开发文件。未修改全局缓存权限。

## 行为用例与范围

[用例](../../tests/evals/progressive-teaching.json)将自动结构与模型语义分开。执行者只接收请求、待测 Skill 和原始合成材料，不读取 checks、设计结论或其他输出。H2 使用真实安装器安装到临时路径后调用安装版 Bundle；源码是同步执行器，没有消息队列产品、持久化、退避或指标。

## 已完成的单课与表达试跑

H1 从只含 `task.py` 的无 Git 项目开始，[首次完整交付](samples/progressive-teaching/H1-first/output/interview-prep/任务样本/导学.md)包含导学、面经与两份完整核心课，不按规模建议凑课数。B1/B2、Q1/Q2、C01/C02 关联通过结构校验；两课都填入真实相对定位、C 编号、整课范围与源码哈希的提示词，没有生成 HTML、练习或占位页面。源码与输出分目录，提示词明确从课程位置找到源码根的方式。[原始报告](samples/progressive-teaching/H1-first/report.md)记录八组实际同步场景断言与范围限制；没有真实学习者试教或性能/并发结论。

H2 的[首次 HTML](samples/progressive-teaching/H2-first/interview-prep/guide-backend/html/03-任务状态--有限重试-455e7796.html)与[来源课程](samples/progressive-teaching/H2-first/interview-prep/guide-backend/03-任务状态.md)均保留首次成稿，未为审读重写。页面仅讲“机制与边界 / 有限重试”，解释同一 Task/id 与 attempts 的关系，包含直接成功、失败后成功、两次失败三条可逐步切换的状态轨迹；没有补造队列产品、退避、持久化、幂等或性能收益。

独立生成 agent 实际运行四个 Python 场景，保存[运行结果](samples/progressive-teaching/H2-runtime-checks.json)；另做[静态依赖/链接检查](samples/progressive-teaching/H2-static-checks.json)、[JavaScript 语法及最小 DOM 桩路径检查](samples/progressive-teaching/H2-javascript-checks.json)和[原文保护检查](samples/progressive-teaching/H2-preservation-checks.json)。主 agent 对保存后的目录重新检查：原课程是更新后文档的完整前缀，源码与未选 Markdown 字节不变，10 处本地链接目标存在，无外部运行依赖，HTML 摘要与首稿相同，见[复核结果](samples/progressive-teaching/H2-static-review.json)。这些检查不等于浏览器测试。

W1 的[润色首稿](samples/progressive-teaching/W1-first.md)删除空泛重要性与收益收尾，保留 ValueError、attempts 条件、同一 ID、无持久化、未实测及未实现分类的事实；后两类限定集中到口播，整份输出仍有明确边界。保留技术比较与 bullet 格式，没有新增亲历或数字。本次没有与旧版作双盲语言偏好比较，不声称测得普遍风格提升。

H3 的[普通追问首稿](samples/progressive-teaching/H3-first.md)直接解释状态，明确 failed 的具体含义和转换未给出，未补造幂等或并发保证，也未生成 HTML 或整套课程。

H4 先冻结 H2 首稿，再在独立副本 HTML 的用户区加入手写补充，要求原页增加三时刻静态对照表。[更新后的页面](samples/progressive-teaching/H4-after/interview-prep/guide-backend/html/03-任务状态--有限重试-455e7796.html)沿用同一文件名与范围；表格区分初始 queued/0、第一次失败 failed/1、最终失败 failed/2。主 agent 独立比较确认 HTML 用户区逐字不变，两条笔记均保留、原 Markdown 只留一条入口，源码、导学和面经不变，见[复核结果](samples/progressive-teaching/H4-review.json)。生成 agent 另执行八组静态/脚本检查（含四个真实 Python 场景及三条交互路径），均通过；这些不是浏览器测试，也未覆盖所有可能的用户手工修改方式。

## 浏览器限制

主 agent 尝试通过本次选定的内置浏览器打开首稿 `file://`，被浏览器 URL 安全策略拒绝（仅允许 HTTP/HTTPS）。没有换浏览器、间接执行或绕过该限制。实际离线打开、桌面/窄屏视觉、浏览器原生键盘/焦点、控制台/网络及返回链接实点均未验证，不计为通过。文件结构、无外部依赖和脚本路径的检查结果分别保留。

## 独立审阅

整体只读审阅覆盖模式路由、中文表达适配、模板与辅助提示词、增量身份/笔记、许可和安装器；发现 H4 缺少先运行 H2 并加入 HTML 笔记的前置状态。已在用例 setup 和测试说明中补齐，并经原审阅者复核解决；当前没有遗留须修复发现。H4 实际更新前后产物的验收另记于上文，不用这次静态复核代替。

H5 的多方向消歧与源码漂移尚未执行；规则审查不算这类行为已通过。

## 最终检查日志

- [npm test](samples/progressive-teaching/validation/npm-test.log)：37/37，exit 0。
- [npm pack dry-run](samples/progressive-teaching/validation/npm-pack-check.log)：27 个文件，exit 0，临时缓存；未发布 npm。
- [Skill 与迁移后的三组结构校验](samples/progressive-teaching/validation/structure-and-skill.log)：Skill 有效，H1/H2/H4 目录移入仓库后本地文件关联均通过；Node 语法与 diff 空白检查 exit 0。
- [安装器红绿记录](samples/progressive-teaching/installer-report.md)、[整体审阅与修复复核](samples/progressive-teaching/implementation-review.md)、[H4 详细检查](samples/progressive-teaching/H4-checks.json)。
