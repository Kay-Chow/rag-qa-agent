"""FastAPI 接口：复用命令行 Agent 的单轮问答逻辑。"""

import os
from contextlib import asynccontextmanager
from threading import Lock

from fastapi import FastAPI, HTTPException
from langchain_deepseek import ChatDeepSeek
from pydantic import BaseModel, Field

from rag_agent import LLM_MODEL, ask_question
from retrieval import KnowledgeRetriever
from knowledge_base import COLLECTION


class AskRequest(BaseModel):
    """/ask 的请求体；长度上限用于阻止异常长的问题直接进入模型。"""

    question: str = Field(min_length=1, max_length=2000)


class Reference(BaseModel):
    """引用编号到知识库块位置的映射。"""

    number: int
    source: str


class AskResponse(BaseModel):
    """/ask 的响应体。"""

    answer: str
    references: list[Reference]


class RetrieveRequest(BaseModel):
    """只读检索请求；不经过大模型生成答案。"""

    query: str = Field(min_length=1, max_length=1000)
    top_k: int = Field(default=3, ge=1, le=5)


class RetrieveHit(BaseModel):
    """带文档位置的原始检索片段，供其他 Agent 自行引用。"""

    source: str
    chunk_index: int
    content: str
    rerank_score: float


class RetrieveResponse(BaseModel):
    collection: str
    hits: list[RetrieveHit]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """进程启动时加载共享资源，避免每个请求重复构建 BM25/加载模型。"""

    app.state.retriever = KnowledgeRetriever()
    # /retrieve 只做本地检索，不需要 DeepSeek Key；/ask 则仍需提供 Key。
    key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    app.state.llm = (
        ChatDeepSeek(
            model=LLM_MODEL,
            api_key=key,
            extra_body={"thinking": {"type": "disabled"}},
        ) if key else None
    )
    # 当前同步问答会用到共享的本地模型；串行处理以避免并发竞争和 CPU 争用。
    app.state.lock = Lock()
    yield


app = FastAPI(title="技术笔记 RAG Agent", lifespan=lifespan)


@app.get("/health")
def health():
    """返回服务存活状态，不执行检索或 LLM 调用。"""

    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    """处理独立的单轮提问；当前没有服务端会话历史。"""

    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=422, detail="问题不能为空")
    if app.state.llm is None:
        raise HTTPException(status_code=503, detail="/ask 需要 DEEPSEEK_API_KEY；/retrieve 无需此 Key")

    # 锁覆盖完整问答过程（包括远端 LLM 调用），因此当前请求会串行执行。
    # 传入空 history：即使 CLI 支持多轮，HTTP 接口也不会延续前一次请求。
    with app.state.lock:
        answer, refs = ask_question(
            question, app.state.retriever, app.state.llm, []
        )

    return AskResponse(
        answer=answer,
        references=[
            Reference(number=n, source=s)
            for n, s in sorted(refs.items())
        ],
    )


@app.post("/retrieve", response_model=RetrieveResponse)
def retrieve(request: RetrieveRequest):
    """只返回本地 Chroma + BM25 + Reranker 的命中，不生成答案。"""

    query = request.query.strip()
    if not query:
        raise HTTPException(status_code=422, detail="检索词不能为空")
    with app.state.lock:
        hits = app.state.retriever.search(query, top_k=request.top_k)

    return RetrieveResponse(
        collection=COLLECTION,
        hits=[
            RetrieveHit(
                source=str(hit.document.metadata["source"]),
                chunk_index=int(hit.document.metadata["chunk_index"]),
                content=hit.document.page_content,
                rerank_score=hit.rerank_score,
            )
            for hit in hits
        ],
    )
