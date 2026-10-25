# 默认首轮独立行为试跑报告

本次按 `skill/project-interview-skill/SKILL.md` 及其阶段路由规则执行真实请求。只将给定 fixture 的 `task.py` 复制到临时项目；未读取项目设计、实现计划、评测 JSON 检查项或其他试跑输出。所有新增文件均在本临时目录，未改主仓库、未提交。

## 请求与交付

- 项目：`project/`，简称“任务样本”，后端方向，源码只读。
- 默认范围：导学、面经和完整核心课程。
- 实际范围：单个 27 行 Python 文件，任务数据对象和同步执行函数；没有代理、持久化或退避。
- 课程数量：两课，由成功状态链路、失败与重试链路决定，没有凑到通用建议课数。
- 关联：两个简历支柱 B1/B2、两个主问 Q1/Q2，均有核心课程和源码反向关联。
- 每课完整包含重点、主链、源码阅读、机制与边界、需要懂什么、需要记住什么及填好的 HTML 深化提示词；没有提前创建 HTML，也没有增加练习或作业。

第一次完整 Markdown 交付保存于 `output/`，快照为 `first-delivery.tar.gz`，校验清单为 `first-delivery.sha256`。快照包含四份 Markdown 与只读源码副本；快照形成后没有修改教学正文。

## 文件树

```text
interview-default-forward-20261025/
├── project/
│   └── task.py
├── output/
│   └── interview-prep/
│       ├── 任务样本/
│       │   ├── 导学.md
│       │   └── 面经.md
│       └── guide-backend/
│           ├── 01-同步执行与任务状态.md
│           └── 02-有限重试与异常边界.md
├── first-delivery.tar.gz
├── first-delivery.sha256
├── runtime_checks.py
├── runtime-checks.json
├── validation.log
├── write_materials.py
└── report.md
```

## 已实际运行的检查

1. 在 Python 3.11.15 执行 `PYTHONDONTWRITEBYTECODE=1 python3 runtime_checks.py`。八组断言全部通过：
   - 正常成功：同一对象返回、一次处理调用、完成态和结果。
   - 第一次 `ValueError`、第二次成功：调用两次、累计次数二、完成态。
   - 持续 `ValueError`：两次耗尽、失败态。
   - 上限零：直接参数异常、处理函数未调用、任务字段未变化。
   - 已耗尽预算：处理函数未调用、原状态保持。
   - `RuntimeError`：异常传播，任务保留运行态和增加后的次数。
   - 完成任务再次调用：剩余预算允许再执行，结果被覆盖。
   - 失败保留旧结果：失败分支不会清空历史结果。

   观测值保存在 `runtime-checks.json`，运行脚本保存在 `runtime_checks.py`。脚本不写入源码目录，不生成字节码。

2. 按 SKILL 指定命令运行结构校验：

   ```text
   python3 /Users/eastonjiang/code/ideas/interview-analyzer-skill/skill/project-interview-skill/scripts/validate_output.py /private/tmp/interview-default-forward-20261025/output/interview-prep/任务样本/面经.md --guide /private/tmp/interview-default-forward-20261025/output/interview-prep/任务样本/导学.md
   ```

   输出 `Delivery structure: OK`，退出码 0。完整命令与输出保存在 `validation.log`。

3. 核对源码目录只有 `task.py`。执行前后 SHA-256 相同：`c66c61af304b3ca40086a3e7c3c559744e675700298d650a056d2abac3119953`。

4. 对照完整源码人工审读机制与内容：没有把初始状态写成消息队列，没有把回调传入写成线程隔离，没有将有限重试写成幂等、超时或持久化；主问来自最终 bullet，追问来自前序回答，未来增强单列为未实现。没有个人经历、历史选型或性能收益主张。

## 未检查项与适用限制

- 未生成 HTML，因此未执行 HTML、JavaScript、浏览器渲染或交互检查。
- 未做性能、压测、并发、进程中断恢复、网络或存储集成检查；源码没有这些实现，也未据此作保证。
- 未穷举非整数、负次数等异常参数组合；课程按源码说明缺少运行时校验，预算推导限定在正常整数输入。
- 未查个人作者或真实贡献，未验证任何上线或个人经历；请求为合成教学项目。
- 结构校验不能代替学习者理解效果评估；本次未做真实学习者试教。

## 入口

- [导学](output/interview-prep/任务样本/导学.md)
- [面经](output/interview-prep/任务样本/面经.md)
- [C01](output/interview-prep/guide-backend/01-同步执行与任务状态.md)
- [C02](output/interview-prep/guide-backend/02-有限重试与异常边界.md)
