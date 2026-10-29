"""验证 CrossEncoder 能直接对“问题—候选文本”配对打分并重新排序。"""

import numpy as np
from sentence_transformers import CrossEncoder

query = "哪个组件负责保存文本向量并进行相似度检索？"
passages = [
    "LangChain 可以组织大模型、工具和工作流。",
    "今天天气晴朗，适合出门散步。",
    "Chroma 是向量数据库，负责保存文本向量并进行相似度检索。",
]

model = CrossEncoder("BAAI/bge-reranker-v2-m3", device="cpu")
# 重排模型逐对阅读问题和候选文本，不负责从整个知识库召回候选。
scores = np.asarray(
    model.predict([(query, passage) for passage in passages]),
    dtype=float,
).reshape(-1)

order = np.argsort(-scores)
print("重排结果：")
for i in order:
    print(f"{scores[i]:.4f}  {passages[i]}")

assert len(scores) == 3
assert np.isfinite(scores).all()
assert int(order[0]) == 2
print("0D OK")
