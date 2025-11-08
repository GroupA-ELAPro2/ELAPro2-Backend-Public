# Import Libraries

import os
from agent_files.agent_states import InputState, TaskOutputState, ToolState, TaskAgentOutput
from agent_files.helper_functions import get_llm
from langgraph.graph import StateGraph, START, END
import app.tools.tools as t
from app.tools.prompt_templates import IELTS_TASK_IMG_PROMPT, IELTS_EVALUATION_PROMPT
import requests
from langchain_core.messages import HumanMessage
from agent_files.image_description_agent import image_agent

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
model = os.getenv("TASK_MODEL")

# ----------------------------
# Initialize LLM
# ----------------------------
llm = get_llm(model=model,
              gemini_key=gemini_api_key,
              openai_key=openai_api_key,
              name="task_agent",
              temperature=0.1)

task_structured = llm.with_structured_output(TaskAgentOutput)

# ----------------------------
# Image URL Validation Functions
# ----------------------------

def is_image_url(url):
    #Checks if a given URL points to an image by inspecting the Content-Type header.
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        # Use requests.head() for efficiency as it only retrieves headers
        # allow_redirects=True handles redirects, timeout prevents hanging
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        content_type = response.headers.get('Content-Type', '')
        return content_type.startswith('image/') and (200 <= response.status_code < 300)
    except requests.exceptions.RequestException as e:
        # Catch various request-related exceptions (e.g., connection errors, timeouts)
        return False


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
# Task evaluation function
# ----------------------------

def task_evaluation(input_state: ToolState) -> TaskAgentOutput:

    """
    input_state will contain outputs from the connected tool nodes automatically.
    """
    task_output = input_state.task_tool_output
    criteria_output = input_state.criteria_tool_output
    band_output = input_state.band_tool_output
    
    prompt_img = IELTS_TASK_IMG_PROMPT.format(
        essay=input_state.essay,
        question=input_state.question,
        criteria="Task Response",
        output_score="task_score",
        output_comments="task_comment",
        task_description_output=task_output,
        criteria_tool_output=criteria_output,
        band_tool_output=band_output,
        image_description = input_state.image_description
    )

    prompt_no_img = IELTS_EVALUATION_PROMPT.format(
        essay=input_state.essay,
        question=input_state.question,
        criteria="Task Response",
        output_score="task_score",
        output_comments="task_comment",
        task_description_output=task_output,
        criteria_tool_output=criteria_output,
        band_tool_output=band_output,
    )


    # Call LLM with image
    if is_image_url(input_state.image_url):
        response = task_structured.invoke([HumanMessage(content=[{"type":"text","text":prompt_img},{"type":"image_url","image_url":{"url":input_state.image_url}}])])
    else:
        response = task_structured.invoke(prompt_no_img)
    
    return response


# Build SubGraph

subgraph_builder = StateGraph(ToolState, input_schema=InputState, output_schema=TaskOutputState)

# Add tool nodes
subgraph_builder.add_node("tools", tools)

subgraph_builder.add_node("Image_Desc_Tool",image_agent)

# Add lexical evaluation node (receives outputs from tool nodes)
subgraph_builder.add_node("Task Evaluator",task_evaluation)

# Connect nodes
subgraph_builder.add_edge(START, "tools")    
subgraph_builder.add_edge("tools", "Image_Desc_Tool")
subgraph_builder.add_edge("Image_Desc_Tool", "Task Evaluator")
subgraph_builder.add_edge("Image_Desc_Tool", END)
subgraph_builder.add_edge("Task Evaluator", END)

graph = subgraph_builder.compile()

# Call the agent
def task_agent(data):
    return graph.invoke(data)