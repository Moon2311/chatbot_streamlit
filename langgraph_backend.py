from typing import TypedDict, Annotated

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver

from langchain_core.messages import BaseMessage
from langchain_ollama import ChatOllama

# -------------------------------
# LLM (Ollama)
# -------------------------------
llm = ChatOllama(
    model="phi3",
    base_url="http://localhost:11434"
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

