"""用假检索工具验证 DeepSeek 的完整工具调用往返。"""

from getpass import getpass

from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool
from langchain_deepseek import ChatDeepSeek


@tool
def search_kb(query: str) -> str:
    """根据问题检索本地知识库。"""
    return "知识库命中：Chroma 是向量数据库，负责保存文档向量并支持相似度检索。"


llm = ChatDeepSeek(
    model="deepseek-flash",
    api_key=getpass("DeepSeek API Key: "),
    extra_body={"thinking": {"type": "disabled"}},
)

messages = [HumanMessage(content="请先检索知识库，再回答：Chroma 有什么作用？")]

first = llm.bind_tools([search_kb], tool_choice="required").invoke(messages)
print("模型请求：", first.tool_calls)
assert first.tool_calls, "模型没有请求调用工具"

# 模型只提出工具名与参数；本地执行后，用 call ID 将结果回填到对话。
call = first.tool_calls[0]
assert call["name"] == "search_kb"
result = search_kb.invoke(call["args"])
print("工具结果：", result)

messages.extend([
    first,
    ToolMessage(content=result, tool_call_id=call["id"]),
])

# 工具结果进入消息列表后，再让模型生成不继续调用工具的最终回复。
reply = llm.bind_tools([search_kb], tool_choice="none").invoke(messages)
print("最终回答：", reply.content)
print("0F OK")
