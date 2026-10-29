"""最小 DeepSeek 连通性测试；不涉及知识库或工具调用。"""

from getpass import getpass
from langchain_deepseek import ChatDeepSeek

llm = ChatDeepSeek(
    model="deepseek-flash",
    api_key=getpass("DeepSeek API Key: "),
    extra_body={"thinking": {"type": "disabled"}},
)

# 只验证配置、鉴权和普通文本回复能否跑通。
reply = llm.invoke("请只回答：连接成功")
print(reply.content)
print("0E OK")
