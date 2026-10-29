"""早期 OpenAI API/工具调用验证脚本；正式 Agent 当前使用 DeepSeek。"""

import os
from getpass import getpass

from langchain_core.tools import tool
from langchain_openai import ChatOpenAI


@tool
def lookup_fact(topic: str) -> str:
    """查询本地测试知识中某个主题的说明。"""
    return f"{topic}：Chroma 是向量数据库，用于保存和检索文本向量。"


api_key = os.getenv("OPENAI_API_KEY") or getpass("输入 OpenAI API Key（不会回显）：")
if not api_key:
    raise SystemExit("未提供 OpenAI API Key")

llm = ChatOpenAI(
    model="gpt-6-sol",
    api_key=api_key,
    use_responses_api=True,
    reasoning_effort="low",
)

# 1. 验证普通回复
reply = llm.invoke("请只回答：连接成功")
print("普通回复：", reply.text)
assert reply.text

# 2. 验证模型能发起工具调用
llm_with_tools = llm.bind_tools([lookup_fact], tool_choice="required")
message = llm_with_tools.invoke("请调用 lookup_fact 查询 Chroma。")
print("工具调用：", message.tool_calls)

assert message.tool_calls
call = message.tool_calls[0]
assert call["name"] == "lookup_fact"

# tool_calls 是模型生成的调用请求，工具仍需由本地代码显式执行。
print("工具执行结果：", lookup_fact.invoke(call["args"]))
print("0E OK")
