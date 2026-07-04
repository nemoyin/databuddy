# JWBuddy MVP 测试用例

基于 PRD 设计文档 (`2026-06-23-jwbuddy-agent-platform-design.md`) 和 MVP 实施计划，覆盖全部功能模块。

---

## 1. 后端基础框架

| 编号 | 模块 | 用例 | 步骤 | 预期结果 | PRI |
|------|------|------|------|----------|-----|
| TC-1.1 | 配置系统 | 启动服务健康检查 | `curl http://localhost:8000/health` | 返回 `{"status":"ok","app":"JWBuddy"}` | P0 |
| TC-1.2 | 配置系统 | 环境变量加载 | 设置 `JWB_DEBUG=true`，检查 `/health` 响应头 | debug 模式启用 | P1 |
| TC-1.3 | 配置系统 | 缺失可选配置的默认值 | 不配置 `JWB_LLM_CLOUD_API_KEY`，启动服务 | 服务正常启动，使用默认值 | P1 |
| TC-1.4 | CORS | 允许的来源跨域 | `curl -H "Origin: http://localhost:3000"` 请求 | 返回 `access-control-allow-origin: http://localhost:3000` | P0 |
| TC-1.5 | CORS | 未允许的来源跨域 | `curl -H "Origin: http://evil.com"` 请求 | 返回 `Disallowed CORS origin` | P2 |
| TC-1.6 | 配置系统 | 所有环境变量前缀为 JWB_ | 配置任意参数 | 只识别 `JWB_` 前缀的变量 | P2 |

## 2. LLM 网关

| 编号 | 模块 | 用例 | 步骤 | 预期结果 | PRI |
|------|------|------|------|----------|-----|
| TC-2.1 | 路由 | 敏感数据走内网 | `gateway.route(is_sensitive=True)` | 返回 internal backend | P0 |
| TC-2.2 | 路由 | 复杂推理走内网 | `gateway.route(requires_reasoning=True)` | 返回 internal backend | P1 |
| TC-2.3 | 路由 | 普通请求云端优先 | `gateway.route(is_sensitive=False)` ，cloud 已配置 | 返回 cloud backend | P1 |
| TC-2.4 | 路由 | 云端未配置回退内网 | `gateway.route(is_sensitive=False)` ，cloud API key 为空 | 返回 internal backend | P0 |
| TC-2.5 | Chat | 基本对话 | 发送 `messages=[{"role":"user","content":"你好"}]` | 返回 LLMResult 含非空 content | P0 |
| TC-2.6 | Chat | 工具调用输出 | 发送含 tools 定义的请求 | 返回结果含 tool_calls 或文本 | P1 |
| TC-2.7 | Chat | 最大迭代次数 | Agent 循环超过 10 次 | 返回 "已达到最大迭代次数" | P2 |

## 3. 工具框架

| 编号 | 模块 | 用例 | 步骤 | 预期结果 | PRI |
|------|------|------|------|----------|-----|
| TC-3.1 | 注册表 | 注册工具 | `registry.register(tool)` | 工具加入注册表 | P0 |
| TC-3.2 | 注册表 | 重复注册报错 | 注册同名工具两次 | 抛出 ValueError | P2 |
| TC-3.3 | 注册表 | 执行已注册工具 | `registry.execute("tool_name", **args)` | 返回 ToolResult | P0 |
| TC-3.4 | 注册表 | 执行未注册工具 | `registry.execute("not_exist")` | 返回 success=False | P1 |
| TC-3.5 | OpenAI 格式 | 导出为 OpenAI function calling | `registry.openai_tools()` | 返回 `[{type:"function", function:{...}}]` 列表 | P0 |
| TC-3.6 | 基类 | 自定义工具扩展 | 实现 BaseTool 子类 | spec/execute 正常工作 | P1 |

## 4. ReAct Agent 运行时

| 编号 | 模块 | 用例 | 步骤 | 预期结果 | PRI |
|------|------|------|------|----------|-----|
| TC-4.1 | 循环 | 无需工具的直接回答 | 发送 "你好" | Agent 返回文本回复，不调用工具 | P0 |
| TC-4.2 | 循环 | 需要工具的任务 | 发送 "查询数据库" | Agent 调用 sql_query → 返回查询结果 → 总结 | P0 |
| TC-4.3 | 循环 | tool_call_id 正确传递 | 检查工具调用后 LLM 请求 | messages 中 tool 消息含 tool_call_id | P0 |
| TC-4.4 | 循环 | 错误处理 | 工具执行返回错误 | 向用户报告错误，不崩溃 | P1 |
| TC-4.5 | 循环 | 多轮对话 | 连续发送多个问题 | 保持上下文，正确引用历史 | P1 |
| TC-4.6 | 循环 | 解析 JSON 格式工具调用 | LLM 返回 `{"name":"xxx","args":{...}}` | 正确解析并执行 | P1 |
| TC-4.7 | 循环 | 解析 code block 格式 | LLM 返回 ` ```json\n{...}\n``` ` | 正确解析并执行 | P1 |
| TC-4.8 | 记忆 | 滑动窗口 | 超过 max_messages 的消息 | 保留 system prompt + 最近 N 条 | P1 |
| TC-4.9 | 记忆 | 系统提示注入 | 上传文件后调用 agent.run(files=[...]) | system prompt 含文件列表 | P0 |

## 5. Chat API (SSE)

| 编号 | 模块 | 用例 | 步骤 | 预期结果 | PRI |
|------|------|------|------|----------|-----|
| TC-5.1 | 会话 | 创建会话 | `POST /sessions {"title":"测试"}` | 返回 `{id, title, created_at, message_count:0}` | P0 |
| TC-5.2 | 会话 | 列出会话 | `GET /sessions` | 返回会话列表 | P0 |
| TC-5.3 | 聊天 | SSE 流式对话 | `POST /chat {"session_id":"xxx","message":"你好"}` | 返回 `text/event-stream`，含 thinking/text/done 事件 | P0 |
| TC-5.4 | 聊天 | 会话不存在 | 使用无效 session_id 发消息 | 返回 404 | P1 |
| TC-5.5 | 聊天 | 上传文件上下文 | `POST /chat {"files":["xxx.xlsx"]}` | Agent 系统提示含文件信息，可调用 query_file | P0 |
| TC-5.6 | 聊天 | 流式事件类型完整 | 检查 SSE 事件 | 含 thinking/tool_call/tool_result/text/done/error | P1 |

## 6. 文件上传

| 编号 | 模块 | 用例 | 步骤 | 预期结果 | PRI |
|------|------|------|------|----------|-----|
| TC-6.1 | 上传 | 上传 Excel | `POST /upload` with .xlsx | 返回 `{filename, file_path, size}` | P0 |
| TC-6.2 | 上传 | 上传 PDF | `POST /upload` with .pdf | 返回文件信息 | P0 |
| TC-6.3 | 上传 | 上传 CSV | `POST /upload` with .csv | 返回文件信息 | P1 |
| TC-6.4 | 上传 | 上传 Word | `POST /upload` with .docx | 返回文件信息 | P1 |
| TC-6.5 | 上传 | 上传图片 | `POST /upload` with .png/.jpg | 返回文件信息 | P2 |
| TC-6.6 | 上传 | 拒绝不支持格式 | `POST /upload` with .exe | 返回 400 "不支持的文件类型" | P1 |
| TC-6.7 | 上传 | 文件大小限制 | 上传超过 10MB 文件 | 返回 400 "文件大小超过 10MB" | P1 |
| TC-6.8 | 上传 | 文件路径安全性 | 上传后检查路径 | 无路径遍历风险，文件正确保存到 data/uploads/ | P1 |

## 7. 数据分析 (query_file)

| 编号 | 模块 | 用例 | 步骤 | 预期结果 | PRI |
|------|------|------|------|----------|-----|
| TC-7.1 | 查询 | 探索数据结构 | Agent 调用 `query_file(sql="SELECT * FROM data LIMIT 3")` | 返回列名 + 前 3 行样例 | P0 |
| TC-7.2 | 查询 | 聚合分析 | Agent 调用 `SELECT 列, SUM/COUNT... FROM data GROUP BY 列 ORDER BY` | 返回正确的聚合结果 | P0 |
| TC-7.3 | 查询 | WHERE 过滤 | Agent 调用 `SELECT * FROM data WHERE 条件` | 返回过滤后的数据 | P0 |
| TC-7.4 | 查询 | 禁止写操作 | `sql="DROP TABLE data"` | 返回 error "禁止的操作: DROP" | P1 |
| TC-7.5 | 查询 | 禁止 INSERT | `sql="INSERT INTO data VALUES (...)"` | 返回 error "仅允许 SELECT" | P1 |
| TC-7.6 | 查询 | 不存在的文件 | `file_path="nonexistent.xlsx"` | 返回 error "文件不存在" | P1 |
| TC-7.7 | 查询 | 路径遍历防护 | `file_path="../etc/passwd"` | 返回 error "文件路径不允许" | P1 |
| TC-7.8 | 查询 | Excel 多 Sheet | 上传含多个 Sheet 的 Excel | 正确读取活跃 Sheet | P2 |
| TC-7.9 | 查询 | CSV UTF-8 BOM | 上传含 BOM 的 CSV | 正确解析列名 | P2 |

## 8. 图表生成 (chart_generate)

| 编号 | 模块 | 用例 | 步骤 | 预期结果 | PRI |
|------|------|------|------|----------|-----|
| TC-8.1 | 图表 | 生成柱状图 | Agent 调用 `chart_generate(data=..., question="对比数据")` | 返回 `format:"chart"`, 含 ECharts option | P0 |
| TC-8.2 | 图表 | 生成饼图 | Agent 调用 `chart_generate(chart_type="pie")` | 返回饼图配置 | P1 |
| TC-8.3 | 图表 | 生成折线图 | Agent 调用 `chart_generate(chart_type="line")` | 返回折线图配置 | P1 |
| TC-8.4 | 图表 | 解析 JSON 块 | LLM 返回 ` ```json\n{chart_config}\n``` ` | 正确解析出 chart_config | P1 |
| TC-8.5 | 图表 | 解析失败回退 | LLM 返回无效 JSON | 返回默认表格配置，不崩溃 | P2 |
| TC-8.6 | 渲染 | ECharts 渲染 | 前端收到 `format:"chart"` 消息 | ChartRenderer 渲染 ECharts 图表 | P0 |
| TC-8.7 | 渲染 | 图表 + 表格共存 | 同一轮对话先后返回 query_file + chart_generate | 表格正确渲染，图表跟随显示 | P1 |

## 9. 文档解析 (document_parse)

| 编号 | 模块 | 用例 | 步骤 | 预期结果 | PRI |
|------|------|------|------|----------|-----|
| TC-9.1 | PDF | 提取 PDF 文本 | `document_parse(file_path="xxx.pdf")` | 返回 PDF 文本内容 | P1 |
| TC-9.2 | Word | 提取 DOCX 文本 | `document_parse(file_path="xxx.docx")` | 返回段落文本 | P1 |
| TC-9.3 | Excel | 提取 XLSX 表格 | `document_parse(file_path="xxx.xlsx")` | 返回 Sheet 名 + 表头 + 数据 | P1 |
| TC-9.4 | 文本 | 读取 TXT/MD/CSV/JSON | `document_parse(file_path="xxx.txt")` | 返回文件文本内容 | P1 |
| TC-9.5 | 图片 | 图片文件处理 | `document_parse(file_path="xxx.png")` | 返回 "[图片文件] 需要 OCR 服务" | P2 |
| TC-9.6 | 错误 | 不存在的文件 | `document_parse(file_path="not_exist")` | 返回 error | P1 |

## 10. 安全审计

| 编号 | 模块 | 用例 | 步骤 | 预期结果 | PRI |
|------|------|------|------|----------|-----|
| TC-10.1 | 审计 | 操作记录 | Agent 执行任何工具调用 | 审计日志记录（who/when/action/result） | P1 |
| TC-10.2 | 审计 | 日志格式 | 检查 audit.jsonl | JSONL 格式，每行一条记录 | P2 |
| TC-10.3 | SQL 安全 | 只允许 SELECT | 传入 INSERT/UPDATE/DELETE/DROP SQL | validate_readonly 返回 False | P0 |
| TC-10.4 | SQL 安全 | 字符串中的关键字 | `SELECT * FROM t WHERE name='DROP TABLE'` | validate_readonly 返回 True（不算写操作） | P1 |

## 11. Skill 系统

| 编号 | 模块 | 用例 | 步骤 | 预期结果 | PRI |
|------|------|------|------|----------|-----|
| TC-11.1 | 加载 | 扫描 skills 目录 | `SkillManager.discover()` | 发现并加载所有 skill 目录 | P1 |
| TC-11.2 | 加载 | 解析 skill.yaml | `SkillLoader.load_from_dir(path)` | 返回 SkillDefinition 含 name/triggers/tools/workflow | P1 |
| TC-11.3 | 匹配 | 触发词匹配 | `manager.match_trigger("示例分析")` | 返回匹配的 skill 列表 | P1 |
| TC-11.4 | 匹配 | 无匹配触发词 | `manager.match_trigger("你好")` | 返回空列表 | P2 |
| TC-11.5 | 加载 | 不存在的目录 | `SkillLoader.load_from_dir("/nonexistent")` | 返回 None | P2 |

## 12. MCP 协议

| 编号 | 模块 | 用例 | 步骤 | 预期结果 | PRI |
|------|------|------|------|----------|-----|
| TC-12.1 | Server | tools/list | `MCPServer().list_tools()` | 返回已注册工具的 MCP 格式列表 | P1 |
| TC-12.2 | Server | tools/call 成功 | `MCPServer().call_tool("query_file", {...})` | 返回 `{content:[{type:"text",text:"..."}], isError:false}` | P1 |
| TC-12.3 | Server | tools/call 失败 | `MCPServer().call_tool("not_exist", {})` | 返回 `{isError:true}` | P1 |
| TC-12.4 | Server | 未知 method | `handle_request({method:"unknown"})` | 返回 error -32601 | P2 |
| TC-12.5 | Client | 获取远程工具列表 | `MCPClient.list_tools()` | 返回远程 MCP 服务工具列表 | P1 |
| TC-12.6 | Client | 调用远程工具 | `MCPClient.call_tool(name, args)` | 返回远程执行结果 | P1 |

## 13. Desktop 前端

| 编号 | 模块 | 用例 | 步骤 | 预期结果 | PRI |
|------|------|------|------|----------|-----|
| TC-13.1 | 对话 | 发送消息 | 输入文字 → 点击发送 | 消息显示在对话列表，Agent 回复 | P0 |
| TC-13.2 | 对话 | 流式展示 | 观察 Agent 回复过程 | 文字逐字出现（SSE 流式） | P0 |
| TC-13.3 | 对话 | 加载状态 | 发送消息后 | 显示 loading 动画，禁用发送按钮 | P1 |
| TC-13.4 | 对话 | 空消息拦截 | 不输入内容点发送 | 不发送请求 | P2 |
| TC-13.5 | 上传 | 上传文件 | 点击上传按钮 → 选择 Excel | 文件上传成功，显示 Tag | P0 |
| TC-13.6 | 上传 | 删除已选文件 | 点击文件 Tag 的关闭按钮 | 文件从列表移除 | P1 |
| TC-13.7 | 上传 | 上传进度 | 上传大文件时 | 上传按钮显示禁用状态 | P2 |
| TC-13.8 | 渲染 | Markdown 渲染 | Agent 返回 Markdown 内容 | 正确渲染标题/列表/代码块/粗体 | P0 |
| TC-13.9 | 渲染 | 表格渲染 | 收到 `format:"table"` 消息 | antd Table 正确展示行列 | P0 |
| TC-13.10 | 渲染 | 图表渲染 | 收到 `format:"chart"` 消息 | ECharts 图表正确渲染 | P0 |
| TC-13.11 | 渲染 | 附件标签 | 用户消息含附件 | 显示 FileOutlined + 文件名 Tag | P1 |
| TC-13.12 | 会话 | 新会话自动创建 | 首次发送消息 | 自动创建会话 | P1 |
| TC-13.13 | 会话 | 历史侧边栏 | 左侧显示会话历史 | 列表显示会话标题和时间 | P1 |
| TC-13.14 | 主题 | 暗黑模式 | 切换暗黑模式 | 界面颜色正确切换 | P2 |

## 14. CLI

| 编号 | 模块 | 用例 | 步骤 | 预期结果 | PRI |
|------|------|------|------|----------|-----|
| TC-14.1 | 对话 | 发起提问 | `python -m jwb ask "你好"` | 返回流式 Agent 回复 | P0 |
| TC-14.2 | 对话 | 指定会话 | `python -m jwb ask --session xxx "继续"` | 在已有会话中继续对话 | P1 |
| TC-14.3 | 会话 | 列出会话 | `python -m jwb sessions` | 显示历史会话列表 | P1 |
| TC-14.4 | 连接 | 连接数据源 | `python -m jwb connect` | 交互式输入连接信息 | P2 |

## 15. 端到端集成

| 编号 | 模块 | 用例 | 步骤 | 预期结果 | PRI |
|------|------|------|------|----------|-----|
| TC-15.1 | E2E | 上传 Excel → 分析 → 图表 | 上传 Excel → 问 "5月份最活跃的市州" → 查看结果 | 1.文件上传成功 2.Agent 自动执行 SQL 3.表格展示排名 4.柱状图可视化 | P0 |
| TC-15.2 | E2E | 文档解析 → 问答 | 上传 PDF → 问 "总结文档内容" | Agent 调用 document_parse → 返回摘要 | P1 |
| TC-15.3 | E2E | 多轮追问 | 问 "5月数据" → "哪个月最高" → "画图" | 保持上下文，每轮正确理解 | P1 |
| TC-15.4 | E2E | 错误恢复 | 上传损坏文件 → 提问 | Agent 返回友好错误信息，不崩溃 | P1 |
| TC-15.5 | E2E | 并发会话 | 两个浏览器 Tab 同时对话 | 两路对话互不干扰 | P2 |
| TC-15.6 | E2E | 混合格式 | 同时上传 Excel + PDF | 两个文件都被识别 | P2 |

---

## 测试统计

| 优先级 | 数量 | 说明 |
|--------|------|------|
| P0 | 24 | 核心功能，必须通过 |
| P1 | 35 | 重要功能，影响体验 |
| P2 | 16 | 边界场景，可延后 |
| **合计** | **75** | |

## 当前通过状态

已运行的 54 项自动化测试覆盖模块：agent_runtime, api, audit, chart_tool, data_schema, document_tool, e2e, llm_gateway, main, mcp, orchestrator, skill_loader, sql_query, tool_registry。

手动/集成测试待覆盖：TC-6.x (上传), TC-7.x (query_file), TC-13.x (前端渲染), TC-15.x (E2E)。
