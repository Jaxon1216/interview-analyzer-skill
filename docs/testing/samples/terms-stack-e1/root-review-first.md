# 主会话首稿补充审读

- B3：惰性获取需限定默认共享视图；sandbox/middleware.py 的 before_agent 在 projection 存在时可提前 acquire。
- 技术栈：将 SandboxProvider/StreamBridge 私有类型换成实际技术或通用职责，依赖版本核验说明放交付说明。
- C05 手机初始首次操作 y=1033.90625，视口844，高于首屏；需前移操作入口，保留同一实例及图形反馈。实测记录见 checks/layout-metrics-first.json。

上述修改与独立报告的 C07/Q6 gap 边界一并交给原生成者；首次完整输出和首次浏览器结果保留。
