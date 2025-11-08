# Import Libraries

import os
from agent_files.agent_states import InputState, LexicalOutputState, ToolState
from agent_files.helper_functions import get_llm
from langgraph.graph import StateGraph, START, END
import app.tools.tools as t
from app.tools.prompt_templates import IELTS_EVALUATION_PROMPT

# ----------------------------
# Load environment variables
# ----------------------------
# Only load .env for local development
if os.getenv("RENDER") is None:
    from dotenv import load_dotenv
    load_dotenv()

# Read API keys and models from environment variables
gemini_api_key = os.getenv("GEMINI_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("LEXICAL_MODEL")


# ----------------------------
# Initialize LLM
# ----------------------------
llm = get_llm(model=model,
              gemini_key=gemini_api_key,
              openai_key=openai_api_key,
              name="lexical_agent",
              temperature=0.1)

lexical_structured = llm.with_structured_output(LexicalOutputState)

# ----------------------------
# Runs the tools first
# ----------------------------

def tools(input_state: InputState) -> ToolState:
    out_dict = {
        "band_tool_output":t.get_all_band_descriptors_by_criteria.func(input_state.essay_type, llm.name),
        "task_tool_output":t.task_description_tool.func(input_state.essay_type),
        "criteria_tool_output":t.assessment_criteria_tool.func(input_state.essay_type, llm.name)
    }
    return out_dict

# ----------------------------
# Evaluate Lexical Resourcs using assessment criteria tool
# ----------------------------

def lexical_evaluation(input_state: ToolState) -> LexicalOutputState:
    """
    input_state will contain outputs from the connected tool nodes automatically.
    """
    task_output = input_state.task_tool_output
    criteria_output = input_state.criteria_tool_output
    band_output = input_state.band_tool_output

    prompt = IELTS_EVALUATION_PROMPT.format(
        essay=input_state.essay,
        question=input_state.question,
        criteria="Lexical Resource",
        output_score="lexical_score",
        output_comments="lexical_comment",
        task_description_output=task_output,
        criteria_tool_output=criteria_output,
        band_tool_output=band_output
    )

    response = lexical_structured.invoke(prompt)
    return response


# Build SubGraph

subgraph_builder = StateGraph(ToolState, input_schema=InputState, output_schema=LexicalOutputState)

# Add tool nodes
subgraph_builder.add_node("tools", tools)

# Add lexical evaluation node (receives outputs from tool nodes)
subgraph_builder.add_node("Lexical Evaluator",lexical_evaluation)

# Connect nodes
subgraph_builder.add_edge(START, "tools")    

subgraph_builder.add_edge("tools", "Lexical Evaluator")

subgraph_builder.add_edge("Lexical Evaluator", END)

graph = subgraph_builder.compile()

# Call the agent

def lexical_agent(data):
    return graph.invoke(data)

