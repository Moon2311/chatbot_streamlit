from typing import TypedDict, Annotated

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver

from langchain_core.messages import BaseMessage
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

# -------------------------------
# LLM (Hugging Face – Qwen)
# -------------------------------
# Set HUGGINGFACEHUB_API_TOKEN for Inference API, or use HuggingFacePipeline for local.
llm = ChatHuggingFace(
    llm=HuggingFaceEndpoint(
        repo_id="Qwen/Qwen2-7B-Instruct",
        task="text-generation",
        max_new_tokens=512,
    )
)

# -------------------------------
# LangGraph State
# -------------------------------
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# -------------------------------
# Graph Node
# -------------------------------
def chat_node(state: ChatState) -> ChatState:
    messages = state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response]}

# -------------------------------
# Graph Setup
# -------------------------------
checkpointer = InMemorySaver()

graph = StateGraph(ChatState)
graph.add_node("chat", chat_node)
graph.add_edge(START, "chat")
graph.add_edge("chat", END)

chatbot = graph.compile(checkpointer=checkpointer)

