"""混合检索：向量召回与 BM25 召回经 RRF 融合，再用 CrossEncoder 重排。"""

import sys
from dataclasses import dataclass

import re
import jieba
from rank_bm25 import BM25Okapi

import numpy as np
from langchain_core.documents import Document
from sentence_transformers import CrossEncoder

from knowledge_base import DB_DIR, open_store


@dataclass
class RetrievalHit:
    """单个候选块及其在各阶段的排名/分数，供调试和结果展示。"""

    document: Document
    vector_rank: int | None = None
    vector_distance: float | None = None
    bm25_rank: int | None = None
    rrf_score: float = 0.0
    rerank_score: float = 0.0


# 英文和技术词尽量保留为整体；连续中文交给 jieba 进一步切词。
TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9_.+#/-]*|[\u4e00-\u9fff]+", re.I)
CHINESE_RE = re.compile(r"[\u4e00-\u9fff]+")


def tokenize(text: str) -> list[str]:
    """为 BM25 生成词项；索引文档和处理查询时必须使用同一规则。"""

    tokens = []
    for part in TOKEN_RE.findall(text.lower()):
        if CHINESE_RE.fullmatch(part):
            tokens.extend(jieba.cut_for_search(part))
        else:
            tokens.append(part)
    return tokens


class KnowledgeRetriever:
    """持有 Chroma、内存中的 BM25 索引和重排模型，避免每次查询重复加载。"""

    def __init__(self):
        if not DB_DIR.is_dir():
            raise RuntimeError("正式知识库不存在，请先运行 knowledge_base.py")

        self.store = open_store()
        # BM25 从 Chroma 已入库的原文构建，确保词法和向量分支使用同一批文档。
        # 这是启动时的内存快照：知识库同步后需重新创建 Retriever/重启服务。
        stored = self.store.get(include=["documents", "metadatas"])
        self.bm25_docs = [
            Document(page_content=content, metadata=meta or {})
            for content, meta in zip(stored["documents"], stored["metadatas"])
        ]
        if not self.bm25_docs:
            raise RuntimeError("知识库为空，请先运行 knowledge_base.py")

        self.bm25 = BM25Okapi([
            tokenize(doc.page_content) for doc in self.bm25_docs
        ])

        self.reranker = CrossEncoder(
            "BAAI/bge-reranker-v2-m3",
            device="cpu",
            local_files_only=True,
        )

    def search(
            self,
            question: str,
            fetch_k: int = 10,
            top_k: int = 3,
            fusion_k: int = 10,
    ) -> list[RetrievalHit]:
        """两路各取 fetch_k，RRF 选 fusion_k 个候选，最后重排并返回 top_k。"""

        # Chroma 返回的是距离（越小越近），BM25 返回的是词项匹配分数。
        # 两者量纲不同，因此融合时使用排名，而不是直接相加原始分数。
        vector_results = self.store.similarity_search_with_score(
            question, k=fetch_k
        )
        bm25_results = self.search_bm25(question, k=fetch_k)

        def chunk_key(doc: Document) -> tuple[str, int]:
            # 同一文本块可能被两路同时召回，以来源和块序号去重。
            return (
                str(doc.metadata["source"]),
                int(doc.metadata["chunk_index"]),
            )

        by_key: dict[tuple[str, int], RetrievalHit] = {}
        # RRF：每路排名 r 贡献 1 / (k + r)；未命中的一路不贡献分数。
        # k=60 可减弱极靠前名次的优势，避免某一路单独主导候选集。
        rrf_k = 60

        for rank, (doc, distance) in enumerate(vector_results, start=1):
            # 同一块若随后也被 BM25 命中，会在同一个 RetrievalHit 上累计 RRF。
            key = chunk_key(doc)
            hit = by_key.setdefault(key, RetrievalHit(document=doc))
            hit.vector_rank = rank
            hit.vector_distance = float(distance)
            hit.rrf_score += 1.0 / (rrf_k + rank)

        for rank, (doc, _) in enumerate(bm25_results, start=1):
            key = chunk_key(doc)
            hit = by_key.setdefault(key, RetrievalHit(document=doc))
            hit.bm25_rank = rank
            hit.rrf_score += 1.0 / (rrf_k + rank)

        if not by_key:
            return []

        candidates = sorted(
            by_key.values(),
            key=lambda hit: hit.rrf_score,
            reverse=True,
        )[:fusion_k]

        # CrossEncoder 同时看“问题 + 候选原文”，比单独的向量/BM25 排名更细。
        # RRF 只负责筛候选；最终顺序由重排分决定，分数不要当作概率。
        pairs = [(question, hit.document.page_content) for hit in candidates]
        scores = np.asarray(
            self.reranker.predict(pairs, batch_size=4),
            dtype=float,
        ).reshape(-1)

        for hit, score in zip(candidates, scores):
            hit.rerank_score = float(score)

        candidates.sort(key=lambda hit: hit.rerank_score, reverse=True)
        return candidates[:top_k]

    def search_bm25(self, question: str, k: int = 10) -> list[tuple[Document, float]]:
        """按词法匹配分数取前 k 个；零分文档不参与后续融合。"""

        scores = self.bm25.get_scores(tokenize(question))
        order = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        return [
            (self.bm25_docs[i], float(scores[i]))
            for i in order if scores[i] > 0
        ][:k]


if __name__ == "__main__":
    question = (
        " ".join(sys.argv[1:])
        if len(sys.argv) > 1
        else "select 和 poll 有什么区别？"
    )

    print("正在加载模型并检索……", flush=True)
    retriever = KnowledgeRetriever()
    hits = retriever.searc
    h(question)

    print(f"\n问题：{question}")
    for rank, hit in enumerate(hits, start=1):
        meta = hit.document.metadata
        vector_rank = hit.vector_rank if hit.vector_rank is not None else "-"
        bm25_rank = hit.bm25_rank if hit.bm25_rank is not None else "-"
        distance = (
            f"{hit.vector_distance:.4f}"
            if hit.vector_distance is not None else "-"
        )
        print(
            f"\n重排第{rank}名 | 向量排名={vector_rank} "
            f"| BM25排名={bm25_rank} | RRF={hit.rrf_score:.4f} "
            f"| 重排分={hit.rerank_score:.4f} | 向量距离={distance}"
        )

        print(f"来源：{meta['source']}，第{meta['chunk_index']}块")
        print(hit.document.page_content.replace("\n", " ")[:250])

    assert hits, "没有检索到文档"
    print("\n1D OK")
