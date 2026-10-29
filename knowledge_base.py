"""读取 Markdown、切分文档，并将变化过的分块增量同步到 Chroma。"""

from hashlib import sha256
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer


ROOT = Path(__file__).resolve().parent
DOCS_DIR = ROOT / "data" / "docs"
DB_DIR = ROOT / "data" / "chroma_kb"
COLLECTION = "tech_notes_v1"
# BGE 检索模型对查询使用指令前缀，入库文档不加此前缀。
QUERY_PREFIX = "为这个句子生成表示以用于检索相关文章："


class BGEEmbeddings(Embeddings):
    """将 BGE 模型适配为 LangChain/Chroma 所需的 Embeddings 接口。"""

    def __init__(self):
        self.model = SentenceTransformer(
            "BAAI/bge-large-zh-v1.5",
            device="cpu",
            local_files_only=True,
        )

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """批量编码文档；归一化后再交给向量库保存。"""

        return self.model.encode(
            texts,
            batch_size=16,
            normalize_embeddings=True,
            show_progress_bar=True,
        ).tolist()

    def embed_query(self, text: str) -> list[float]:
        """查询使用 BGE 指令前缀，并与文档向量采用相同的归一化。"""

        return self.model.encode(
            [QUERY_PREFIX + text],
            normalize_embeddings=True,
        )[0].tolist()


def load_chunks() -> list[Document]:
    """扫描 data/docs 下的 Markdown，返回带来源和块序号的文本块。"""

    paths = sorted(DOCS_DIR.rglob("*.md"))
    if not paths:
        raise SystemExit(f"没有找到文档：{DOCS_DIR}")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=60,
        separators=["\n\n", "\n", "。", "；", "，", " ", ""],
    )

    all_chunks = []
    for path in paths:
        # utf-8-sig 同时兼容普通 UTF-8 和带 BOM 的 Markdown 文件。
        content = path.read_text(encoding="utf-8-sig").strip()
        if not content:
            continue

        source = path.relative_to(DOCS_DIR).as_posix()
        document = Document(
            page_content=content,
            metadata={"source": source},
        )
        chunks = splitter.split_documents([document])

        # source + chunk_index 同时用于引用展示、检索去重和稳定 ID。
        for index, chunk in enumerate(chunks):
            chunk.metadata["chunk_index"] = index

        all_chunks.extend(chunks)

    if not all_chunks:
        raise SystemExit("没有可入库的文档内容")
    return all_chunks


def open_store() -> Chroma:
    """打开固定 collection；persist_directory 使数据跨进程保留。"""

    return Chroma(
        collection_name=COLLECTION,
        embedding_function=BGEEmbeddings(),
        persist_directory=str(DB_DIR),
    )


def build_index() -> None:
    """比较本地分块与库中内容，只处理新增、正文变化和已删除的块。"""

    chunks = load_chunks()
    # ID 只由相对路径和块序号决定，同位置内容变化时走 update，而非重复新增。
    # 若前面插入内容导致后续块序号变化，受影响的块也会重新比较/更新。
    ids = [
        sha256(
            f"{chunk.metadata['source']}:{chunk.metadata['chunk_index']}".encode("utf-8")
        ).hexdigest()
        for chunk in chunks
    ]
    current_by_id = dict(zip(ids, chunks))

    store = open_store()
    existing = store.get(include=["documents"])
    old_by_id = dict(zip(existing["ids"], existing["documents"]))

    # 当前只比较正文；如果仅修改 metadata 而正文不变，这里不会触发更新。
    add_ids = [item_id for item_id in ids if item_id not in old_by_id]
    update_ids = [
        item_id for item_id in ids
        if item_id in old_by_id
        and old_by_id[item_id] != current_by_id[item_id].page_content
    ]
    stale_ids = list(set(old_by_id) - set(ids))
    unchanged = len(ids) - len(add_ids) - len(update_ids)

    print(
        f"新增 {len(add_ids)}，更新 {len(update_ids)}，"
        f"删除 {len(stale_ids)}，跳过 {unchanged}",
        flush=True,
    )

    if add_ids:
        # 仅 add/update 需要重新生成向量；未变化的块直接跳过。
        store.add_documents(
            documents=[current_by_id[item_id] for item_id in add_ids],
            ids=add_ids,
        )
    if update_ids:
        store.update_documents(
            ids=update_ids,
            documents=[current_by_id[item_id] for item_id in update_ids],
        )
    if stale_ids:
        # 文档被移除或分块数减少时，清理库中不再存在的旧 ID。
        store.delete(ids=stale_ids)

    count = len(store.get()["ids"])
    print(f"库中记录：{count}")
    assert count == len(chunks), "库中记录数与分块数不一致"
    print("知识库同步完成")


if __name__ == "__main__":
    build_index()
