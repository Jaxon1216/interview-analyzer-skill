# 面经内部名词与口播抽象

**适用范围：口播正文。** 简历简介与 bullet 的名词策略见 [oral-and-resume-patterns.md](oral-and-resume-patterns.md)：允许外部可检索的范式名；禁止私有函数、路径、枚举。不要用本节黑名单把简历支柱剥成「对接了某某接口」。

面经读者是**外部面试官**（不在你团队、不熟悉你项目）。以下**七类名词**属于"内部私名 / 团队黑话"，一律禁止在口播正文里直接堆叠，必须先翻译成通用技术抽象。约束按**形态**判定，不锁死到任何具体项目。

### 黑名单（按形态识别，禁止在口播里堆叠）

| 类别 | 识别形态（不是具体名） |
|---|---|
| 1. 私有框架组件 / hook / API | 只在本公司/本项目能搜到的自研标签、自研 hook、自研 runtime 函数 |
| 2. 项目内部函数名 | 团队仓库里定义、外部搜索无结果的私有函数（如 `fetchXxxData` / `updateXxxStore` / `getXxxVersion` / `xxxAssert`） |
| 3. 后端字段与私有枚举值 | 蛇形命名的接口字段（`user_status`、`ext_info` 等）+ 复合大写枚举（`SOME_MODULE_XXX_STATE`） |
| 4. 打点事件名 | 以业务/产品前缀开头的下划线拼接串（`biz_module_stage_event`） |
| 5. 端能力 / 容器私名 | 首字母大写 + 特殊后缀的容器名、私有 JSBridge 命名空间（`x.xxx`、`bridge.xxx`） |
| 6. 动态配置键 / 灰度开关 | 全小写下划线开关名（`enable_xxx_yyy`）、URL query flag（`abc=1`） |
| 7. 上下游业务黑话 | 3~5 字中文缩写、产品代号、内部俗称（只在本团队内部通用的业务名） |

### 白名单（通用工程语言，鼓励使用）

React / Vue / TypeScript / SSR / CSR / Hydration / Streaming SSR / `<Suspense>` / Service Worker / Web Worker / Prefetch / Preload / Fallback / Error Boundary / State Machine / Reducer / Selector / Immutable Update / Single Source of Truth / JSBridge（泛称）/ Feature Toggle / A/B Testing / CDN / Cache Invalidation / Idempotency / Race Condition / Timeout / Circuit Breaker / Rate Limiting / Graceful Degradation / Observability / SLO / SLI / P95 Latency / FMP / CLS / Message Queue / Eventual Consistency / Transaction / Sharding。以及**当前项目领域内、外部可检索**的范式名（不要因为不在本列表就从简历上剥掉）。

### 翻译原则（必用）

| 内部名的形态 | 通用抽象的表达 |
|---|---|
| 私有 hook / action | "store 的 read hook / write action" |
| 分层决策函数 | "一级路由决策 / 二级视图状态机" |
| 后端下划线字段 | 用**语义化描述**代替字段名（如"授信信息"而不是 `xx_auth_info`） |
| 复合枚举 `MODULE_STATE_SUB` | 用中文语义（"某模块的 X 状态"），不搬枚举原名 |
| 具体打点事件名 | "水合成功率打点""预取生命周期打点" |
| 私有 JSB namespace | "端内 JSBridge" / "容器 native call" |
| 灰度开关键名 | "配置中心下发的 feature toggle" |
| 业务黑话 | 直接省略，或换成"某营销活动""某信贷子产品"这类中性描述 |

### 预算（用于自检 / 质量门禁）

- 每道主问口播内部私名通常不超过 2 次，且**每次出现必须紧跟一句通用抽象说明**。
- 每道追问口播内部私名通常不超过 1 次。
- 发现私名堆叠时重写成通用机制；回答长度与结构按题型决定，见 [问题契约](star-framework.md)。

### 抽象层级样例（默认目标 = 样例风格 B）

- 见 `../examples/oral-style-samples.md`，内含**前端**与**后端**两份完整口播样例（含 STAR + 追问）+ 反例（私名堆叠型）+ **题干正反例**（简历展开型 vs 源码巡检型）。
- 生成面经时**每一道题的口播都要对齐样例风格 B 的抽象层级**：通用工程语言为主 + 极少量内部私名兜底证据。
- 反例（样例中的"私名堆叠型"口播、"源码巡检型"题干）**禁止出现**在最终面经里。

### 证据下沉

- 所有具体函数名、文件路径、私有打点事件名、私有容器名统一收敛到面经文末的「**源码证据索引**」表格。
- 简历 bullet 可保留业界可检索名与设计约束数字；口播只做通用抽象叙述；索引表用于候选人自己复盘、以及被追问细节时的"证据钩子"。
