"""只测试 Chroma 的向量召回，不经过 BM25、RRF、重排或大模型。"""

import sys

from knowledge_base import DB_DIR, open_store

if not DB_DIR.is_dir():
    raise SystemExit("正式知识库不存在，请先完成入库")

question = (
    " ".join(sys.argv[1:])
    if len(sys.argv) > 1
    else "select 和 poll 有什么区别？"
)

store = open_store()
# 此处的 score 是向量距离，不是“相关概率”；数值越小通常越接近。
results = store.similarity_search_with_score(question, k=5)

print(f"问题：{question}")
for rank, (doc, distance) in enumerate(results, start=1):
    source = doc.metadata["source"]
    chunk_index = doc.metadata["chunk_index"]
    preview = doc.page_content.replace("\n", " ")[:260]
    print(f"\n{rank}. 距离={distance:.4f}  {source}  第{chunk_index}块")
    print(preview)

assert results, "没有检索到结果"
print("\n1C OK")
