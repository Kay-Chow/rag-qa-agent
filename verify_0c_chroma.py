"""分开执行 write/read，验证 Chroma 落盘后能在新进程中读出数据。"""

from pathlib import Path
import sys

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from sentence_transformers import SentenceTransformer

PREFIX = "为这个句子生成表示以用于检索相关文章："
# 与正式知识库分开，避免验证数据混入业务 collection。
DB_PATH = Path(__file__).resolve().parent / "data" / "chroma_stage0"


class BGEEmbeddings(Embeddings):
    def __init__(self):
        self.model = SentenceTransformer("BAAI/bge-large-zh-v1.5", device="cpu")

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self.model.encode(texts, normalize_embeddings=True).tolist()

    def embed_query(self, text: str) -> list[float]:
        return self.model.encode(
            [PREFIX + text], normalize_embeddings=True
        )[0].tolist()


if len(sys.argv) != 2 or sys.argv[1] not in {"write", "read"}:
    raise SystemExit("请指定 write 或 read")

mode = sys.argv[1]
if mode == "write":
    DB_PATH.mkdir(parents=True, exist_ok=True)
else:
    assert DB_PATH.is_dir(), "数据库目录不存在，请先执行 write"

store = Chroma(
    collection_name="stage0_chroma",
    embedding_function=BGEEmbeddings(),
    persist_directory=str(DB_PATH),
)

if mode == "write":
    # 固定 ID 使测试数据可定位；此模式负责首次写入。
    documents = [
        Document(
            page_content="Chroma 是向量数据库，负责保存文本向量并进行相似度检索。",
            metadata={"source": "chroma"},
        ),
        Document(
            page_content="BGE Reranker 用于对召回的候选文档重新排序。",
            metadata={"source": "reranker"},
        ),
        Document(
            page_content="LangChain 可以组织大模型、工具和工作流。",
            metadata={"source": "langchain"},
        ),
    ]
    store.add_documents(
        documents,
        ids=["stage0-chroma", "stage0-reranker", "stage0-langchain"],
    )
    print("写入完成")
else:
    # 在另一个进程运行 read，检查持久化目录和向量检索结果。
    results = store.similarity_search_with_score(
        "哪个组件负责保存向量并进行检索？", k=3
    )
    for document, distance in results:
        print(f"{distance:.4f}  {document.metadata['source']}  {document.page_content}")

    assert len(results) == 3
    assert results[0][0].metadata["source"] == "chroma"
    print("0C OK")
