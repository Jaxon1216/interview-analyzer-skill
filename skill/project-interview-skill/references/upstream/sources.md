# 上游来源与本地适配

这些记录用于溯源，不需要每次生成时加载；运行时读取对应的本地规则即可。不要求另外安装、联网加载或激活上游 Skill。

## Humanizer

- 来源：[blader/humanizer SKILL.md v3.1.0](https://github.com/blader/humanizer/blob/d4b81278e6604e237bf32f0f7ce5c217aee94269/SKILL.md)。固定 commit：`d4b81278e6604e237bf32f0f7ce5c217aee94269`。
- 本地：[自然表达规则](../rules/writing-style.md)。吸收直接表达、删除无信息铺垫/总结、事实守恒与嵌入式成稿审读，增加中文工程文体与结构保护。
- 不照搬去加粗/列表/箭头、添加主观经历、展示多轮审计等要求；现有简历格式、教学深度、证据限定和用户范围优先。不以绕过 AI 检测为目标。
- 许可：MIT，Copyright (c) 2025 Siqi Chen。保留[许可全文](humanizer-LICENSE.txt)。

## teach

- 来源：[mattpocock/skills — skills/productivity/teach/SKILL.md](https://github.com/mattpocock/skills/blob/5beb35b040e3de97e54fa9e386d7e42d15c295c2/skills/productivity/teach/SKILL.md)。固定 commit：`5beb35b040e3de97e54fa9e386d7e42d15c295c2`。
- 本地：[HTML 教学深化](../rules/interactive-teaching.md)。吸收目标驱动、聚焦范围、可信来源、持久上下文和生成不等于掌握。
- 不照搬独立教学仓库、强制 Mission 访谈、默认练习和学习记录。首次仍完整 Markdown；默认单文件内联资源是本项目的便携性选择，上游默认共享 assets。
- 上游名为 `/teach`，不是 `/tech`；这里没有新增同名命令。上游是教学指令及格式说明，不是 HTML 渲染框架，也未附现成 CSS、模板或模拟器。
- 许可：MIT，Copyright (c) 2026 Matt Pocock。保留[许可全文](teach-LICENSE.txt)。

查证日期：2026-10-25。后续更新上游时重新核对行为差异与本地契约，不直接覆盖适配规则。
