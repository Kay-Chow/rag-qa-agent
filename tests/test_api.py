"""验证知识库的只读检索接口可独立于 DeepSeek 问答使用。"""

import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from fastapi.testclient import TestClient

import api


class FakeRetriever:
    def search(self, query, top_k):
        assert query == "反馈列表优先级"
        assert top_k == 2
        document = SimpleNamespace(
            page_content="GET /feedback 目前不支持优先级筛选。",
            metadata={"source": "demo/产品反馈列表背景.md", "chunk_index": 0},
        )
        return [SimpleNamespace(document=document, rerank_score=0.88)]


class ApiTests(unittest.TestCase):
    def test_retrieve_returns_source_without_llm_key(self):
        with patch.dict(os.environ, {"DEEPSEEK_API_KEY": ""}), patch.object(
            api, "KnowledgeRetriever", return_value=FakeRetriever()
        ), TestClient(api.app) as client:
            response = client.post("/retrieve", json={
                "query": "反馈列表优先级", "top_k": 2,
            })
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["collection"], "tech_notes_v1")
            self.assertEqual(response.json()["hits"][0]["source"],
                             "demo/产品反馈列表背景.md")
            self.assertEqual(client.post("/ask", json={
                "question": "反馈列表优先级",
            }).status_code, 503)


if __name__ == "__main__":
    unittest.main()
