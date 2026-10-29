"""预览 Markdown 分块结果；仅本地读取，不写入 Chroma。"""

from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

ROOT = Path(__file__).resolve().parent
DOCS_DIR = ROOT / "data" / "docs"

paths = sorted(DOCS_DIR.rglob("*.md"))
if not paths:
    raise SystemExit(f"没有找到 Markdown 文档：{DOCS_DIR}")

splitter = RecursiveCharacterTextSplitter(
    # 与正式入库脚本保持相同参数，方便入库前检查切片粒度。
    chunk_size=400,
    chunk_overlap=60,
    separators=["\n\n", "\n", "。", "；", "，", " ", ""],
)

all_chunks = []

for path in paths:
    source = path.relative_to(DOCS_DIR).as_posix()
    content = path.read_text(encoding="utf-8-sig").strip()
    if not content:
        continue

    document = Document(
        page_content=content,
        metadata={"source": source},
    )
    chunks = splitter.split_documents([document])

    # 给每篇文档的分块单独编号，后续可用于定位来源。
    for index, chunk in enumerate(chunks):
        chunk.metadata["chunk_index"] = index

    all_chunks.extend(chunks)
    print(f"{source}：{len(content)} 字符 → {len(chunks)} 块")

if not all_chunks:
    raise SystemExit("文档均为空，未生成分块")

print(f"\n总分块数：{len(all_chunks)}")
for chunk in all_chunks[:3]:
    print(f"\n来源：{chunk.metadata}")
    print(chunk.page_content[:200])
