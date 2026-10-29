# 技术笔记 RAG Agent

基于本地 Markdown 知识库的问答 Agent，提供命令行和 FastAPI 接口。使用 BGE 生成向量、Chroma 检索、BGE Reranker 重排，再由 DeepSeek 调用检索工具并根据资料回答。

## 环境

- Python 3.12
- 主要依赖：`langchain-chroma`、`langchain-core`、`langchain-text-splitters`、`langchain-deepseek`、`sentence-transformers`、`numpy`、`fastapi`、`uvicorn`
- 模型：`BAAI/bge-large-zh-v1.5`、`BAAI/bge-reranker-v2-m3`
- DeepSeek API Key 在运行时输入，不写入代码或仓库

当前代码以 `local_files_only=True` 加载两个 BGE 模型，因此首次运行前需要将模型下载到本机缓存。本项目目前在 CPU 环境下运行。

## 使用

将 Markdown 文档放入 `data/docs/`。`data/docs/demo/产品反馈列表背景.md` 是供产品 Agent 测试的演示资料，不是公司内部资料。在已安装依赖的 Python 环境中，从项目根目录运行：

```powershell
python knowledge_base.py
python rag_agent.py "MySQL 索引有什么作用？"
python rag_agent.py
```

第二条是单次提问；第三条进入连续问答模式，输入 `exit` 退出。修改文档后重新运行 `knowledge_base.py`，未变化的分块会跳过。

## HTTP API

本地产品 Agent 只调用 `POST /retrieve`，**不需要 DeepSeek API Key**。从项目根目录启动知识库服务（与反馈演示服务的 8001 端口错开）：

```powershell
python -m uvicorn api:app --host 127.0.0.1 --port 8002
```

`POST /retrieve` 请求体如 `{"query":"反馈列表优先级筛选的现状是什么？","top_k":3}`；返回 collection、原文片段、文档相对路径、分块序号和重排分，不生成答案。索引更新后重启服务，以刷新 BM25 内存快照。该接口仅供可信本机演示，**没有鉴权，不要绑定公网地址**。

如需使用原有的 `POST /ask` 问答接口，启动前在 PowerShell 中安全输入 Key：

```powershell
$secure = Read-Host 'DeepSeek API Key' -AsSecureString
$env:DEEPSEEK_API_KEY = [System.Net.NetworkCredential]::new('', $secure).Password
Remove-Variable secure
python -m uvicorn api:app --host 127.0.0.1 --port 8002
```

- `GET /health`：检查服务是否启动。
- `POST /ask`：请求体为 `{"question": "MySQL 索引有什么作用？"}`；返回答案和引用编号映射；未设置 DeepSeek Key 时返回 503。
- 打开 `http://127.0.0.1:8002/docs` 可在交互文档中测试接口。

服务启动时加载知识库检索模型一次；仅设置 DeepSeek Key 时创建问答模型。当前 API 的每个请求都是独立单轮问答；连续对话仍通过命令行模式使用。

## 工作流程

Markdown 分块 → BGE Embedding → Chroma 向量检索 → BGE Reranker 重排 → Agent 工具调用 → 带来源编号的回答。

回答只依据本轮检索资料；资料不足时应拒答。连续问答保留最近三轮对话用于理解指代，但每轮重新检索并生成引用映射。

## 当前范围

仅支持 Markdown；HTTP API 目前只在本机使用，尚无身份验证、限流、会话存储或网页界面。新增、修改、删除文档的增量同步逻辑已经实现，其中无变化跳过路径已实测，其他路径尚未逐项实测。
