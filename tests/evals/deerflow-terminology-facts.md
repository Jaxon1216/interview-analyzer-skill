# DeerFlow 术语评测原始材料

以下是已核验的源码事实，非参考简历或推荐措辞。源码基线为 `5ecc1c2ac2de624af354bc515d5cb04f80df226c`，本机仓库只读，开始评测时 SHA 相同且工作区干净。没有个人职责、历史升级或实测收益材料。

1. **运行与传输**：Gateway 受理独立 run，由后台 worker 执行；SSE 连接订阅运行事件，客户端分别消费消息、状态更新和自定义事件。初次创建 POST 不自动重试，恢复既有运行走 GET；回放缺口时重载持久状态，不保证补回每个丢失事件。
   - `frontend/src/core/api/api-client.ts`：`createCompatibleClient`、`recoverStreamReplayGaps`
   - `backend/app/gateway/services.py`：`start_run`、`sse_consumer`
2. **模型与工具执行约束**：模型和工具的输入净化、工具输出预算、授权与错误规范化由有顺序要求的中间件组装。工具需要更新会话状态时可返回 LangGraph 的 `Command`，由对应 reducer 合并；中间件数量受配置影响。
   - `backend/packages/harness/deerflow/agents/lead_agent/agent.py`：`build_middlewares`
   - `backend/packages/harness/deerflow/agents/middlewares/tool_error_handling_middleware.py`：`_build_runtime_middlewares`
3. **执行环境持有**：按用户和线程身份复用或获取沙箱，执行前重新检查权限与归属；最后一个执行持有者退出后由 provider 释放环境。释放不一定销毁环境，本地路径映射不等于容器级隔离。
   - `backend/packages/harness/deerflow/sandbox/lease.py`：`SandboxLeaseManager`
   - `backend/packages/harness/deerflow/sandbox/local/local_sandbox_provider.py`
4. **技能加载与工具声明**：技能是含 `SKILL.md` 的目录包。默认系统提示提供元数据，可选名称索引模式默认关闭；正文由显式选择或 `read_file` 按需加载。轻量引用保存已加载技能，活跃技能的 `allowed-tools` 在模型可见工具与实际调用两处落实。
   - `backend/packages/harness/deerflow/config/skills_config.py`：`deferred_discovery=False`
   - `backend/packages/harness/deerflow/agents/lead_agent/prompt.py`：`get_skills_prompt_section`
   - `backend/packages/harness/deerflow/agents/middlewares/skill_tool_policy_middleware.py`
5. **文件交付**：线程输出文件通过 `present_files` 登记为规范产物引用，列表按增量合并并去重；正式内容通过受权文件接口读取，文本默认按字节预算请求预览，结束后刷新内容。登记路径不证明文件存在或内容正确。
   - `backend/packages/harness/deerflow/tools/builtins/present_file_tool.py`
   - `frontend/src/core/artifacts/loader.ts`：`loadArtifactContent`
   - `backend/app/gateway/routers/artifacts.py`：`get_artifact`

源码中的类名、方法名和字段仅帮助取证，不指定它们必须出现在简历。术语与句子由待测 Skill 自行选择。
