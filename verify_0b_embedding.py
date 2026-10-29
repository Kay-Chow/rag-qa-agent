"""验证 BGE 文档/问题编码的维度、归一化和最简单的相似度排序。"""

import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("BAAI/bge-large-zh-v1.5", device="cpu")

passages = [
    "Chroma 是向量数据库，负责保存文本向量并进行相似度检索。",
    "BGE Reranker 用于对召回的候选文档重新排序。",
    "LangChain 可以组织大模型、工具和工作流。",
]
query = "哪个组件负责保存向量并进行检索？"
instruction = "为这个句子生成表示以用于检索相关文章："

doc_vectors = model.encode(passages, normalize_embeddings=True)
# BGE 的检索指令只加在问题侧；文档侧直接编码原文。
query_vector = model.encode(
    [instruction + query], normalize_embeddings=True
)[0]

# 向量已经归一化，点积可用于比较余弦相似度。
scores = doc_vectors @ query_vector

print("文档向量形状：", doc_vectors.shape)
print("问题向量形状：", query_vector.shape)
print("问题向量长度：", np.linalg.norm(query_vector))
print("相似度排序：")
for i in np.argsort(-scores):
    print(f"{scores[i]:.4f}  {passages[i]}")

assert doc_vectors.shape == (3, 1024)
assert query_vector.shape == (1024,)
assert np.isclose(np.linalg.norm(query_vector), 1.0, atol=1e-3)
assert int(np.argmax(scores)) == 0
print("0B OK")
