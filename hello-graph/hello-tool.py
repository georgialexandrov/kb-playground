import os
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode
from tools import enrich_structured_data, enrich_unstructured_data

from langgraph.graph import StateGraph, MessagesState, START, END


def should_continue(state: MessagesState):
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return END

llm = ChatOpenAI(model_name=os.getenv("OPENAI_MODEL"), temperature=0.0)

tools = [enrich_structured_data, enrich_unstructured_data]
tool_node = ToolNode(tools)

model_with_tools = llm.bind_tools(tools)

def call_model(state: MessagesState):
    messages = state["messages"]
    response = model_with_tools.invoke(messages)
    return {"messages": [response]}

workflow = StateGraph(MessagesState)

# Define the two nodes we will cycle between
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)

workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue, ["tools", END])
workflow.add_edge("tools", "agent")

app = workflow.compile()
response = app.invoke({"messages": [HumanMessage(content="What is the focus of the AI Chatbot project, who works on the project?")]})
print(response['messages'][-1].content)