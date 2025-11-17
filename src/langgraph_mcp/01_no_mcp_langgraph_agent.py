from langchain_core.messages import HumanMessage, AnyMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import tools_condition, ToolNode
from pydantic import BaseModel, Field
from typing import Annotated, List
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.prompts import PromptTemplate
from langgraph_mcp.configuration import get_llm

"""
LangGraph ReAct Agent with Local Tools

Flow: Human Question → Assistant (calls tool) → Tool Execution → Assistant (final answer (summarizing the tool execution))

Example:
  Human: "Add 3 and 4"
  Assistant: *calls add(3, 4)*
  Tool: returns 7
  Assistant: "The result of adding 3 and 4 is 7"
"""


def multiply(a: int, b: int) -> int:
    """Multiply a and b.

    Args:
        a: first int
        b: second int
    """
    return a * b


def add(a: int, b: int) -> int:
    """Adds a and b.

    Args:
        a: first int
        b: second int
    """
    return a + b


def divide(a: int, b: int) -> float:
    """Divide a and b.

    Args:
        a: first int
        b: second int
    """
    return a / b


# Define the state of the graph.
class MessageState(BaseModel):
    messages: Annotated[List[AnyMessage], add_messages]
    is_math_question: bool = False


class MathQuestion(BaseModel):
    """MathQuestion validates if a question is about math operations."""
    is_math_question: bool = Field(
        description="True if the question is about math operations (addition, multiplication, division), False otherwise"
    )


def assistant(state: MessageState):
    state.messages = llm_with_tools.invoke(state.messages)
    return state


def validate_math_question(state: MessageState):
    """Check if the question is about math using Pydantic structured output."""
    last_message = state.messages[-1]
    
    # Create prompt template
    template_math_validator = PromptTemplate.from_template(
        "Determine if this is a math question about addition, multiplication, or division: {current_question}"
    )
    
    # Format with current question
    prompt = template_math_validator.format(current_question=last_message.content)
    
    # Use structured output to validate
    llm_structured = llm.with_structured_output(MathQuestion)
    validation_result = llm_structured.invoke(prompt)
    
    # Store validation result in state
    state.is_math_question = validation_result.is_math_question
    
    # Check validation result
    if not validation_result.is_math_question:
        state.messages.append(
            AIMessage(
                content="I can only help with math questions (addition, multiplication, or division). Please ask a math question."
            )
        )
    
    return state


def route_after_validation(state: MessageState):
    """Route to assistant if math question, otherwise to END."""
    if state.is_math_question:
        return "assistant"
    return END


def build_graph(tools):
    builder = StateGraph(MessageState)
    # Define nodes in the graph
    builder.add_node("validate_math", validate_math_question)
    builder.add_node("assistant", assistant)
    builder.add_node("tools", ToolNode(tools))
    # Define edges
    builder.add_edge(START, "validate_math")
    builder.add_conditional_edges(
        "validate_math",
        route_after_validation,
        {
            "assistant": "assistant",
            END: END,
        },
    )
    builder.add_conditional_edges(
        "assistant",
        tools_condition,
    )
    # Note: The tool call output will be sent back to the assistant node (to 'summarize' the tool call)
    builder.add_edge("tools", "assistant")

    memory = MemorySaver()
    react_graph_memory = builder.compile(checkpointer=memory)

    # Visualise the graph
    png_bytes = react_graph_memory.get_graph().draw_mermaid_png()
    with open("src/langgraph_mcp/graph_visualisation/model_graph_check.png", "wb") as f:
        f.write(png_bytes)
    return react_graph_memory


if __name__ == "__main__":
    llm = get_llm("openai")
    tools = [
        add,
        multiply,
        divide,
    ]  # when using mcp threse tools are initialized from an mcp server
    llm_with_tools = llm.bind_tools(tools)  # this binds the tools to the llm

    # build graph
    react_graph_memory = build_graph(tools=tools)

    # setup config
    config = {"configurable": {"thread_id": "1"}}

    # setup input state for the graph
    input_state = MessageState(
        messages=[
            HumanMessage(content="Please, can you add 3 and 4")
        ]
    )

    # Run the graph with the input state and the config from the langraph
    result = react_graph_memory.invoke(input_state, config)

    for m in result["messages"]:
        m.pretty_print()
