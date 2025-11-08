# Import Libraries
import os
from agent_files.agent_states import (
    InputState,
    TaskOutputState,
    ToolState,
    TaskAgentOutput,
)
from agent_files.helper_functions import get_llm
from langgraph.graph import StateGraph, START, END
import app.tools.tools as t
from app.tools.prompt_templates import IELTS_TASK_IMG_PROMPT, IELTS_EVALUATION_PROMPT
from langchain_core.messages import HumanMessage
from agent_files.image_description_agent import image_agent

# Load environment variables

# Only load .env for local development
if os.getenv("RENDER") is None:
    from dotenv import load_dotenv

    load_dotenv()

# Read API keys and models from environment variables
gemini_api_key = os.getenv("GEMINI_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("TASK_MODEL")

# Initialise LLM
llm = get_llm(
    model=model,
    gemini_key=gemini_api_key,
    openai_key=openai_api_key,
    name="task_agent",
    temperature=0.1,
)

# Initialise LLM with structured output
task_structured = llm.with_structured_output(TaskAgentOutput)


# Runs the tools first
def tools(input_state: InputState) -> ToolState:
    """Retrieve IELTS assessment tools and descriptors for the given essay type.

    Args:
        input_state (InputState): Input state containing essay type and submission details.

    Returns:
        ToolState: Tool outputs including band descriptors, task descriptions, and assessment criteria.
    """
    out_dict = {
        "band_tool_output": t.get_all_band_descriptors_by_criteria.func(
            input_state.essay_type, llm.name
        ),
        "task_tool_output": t.task_description_tool.func(input_state.essay_type),
        "criteria_tool_output": t.assessment_criteria_tool.func(
            input_state.essay_type, llm.name
        ),
    }
    return out_dict


# Evaluate Task Response or Task Achievement using assessment criteria tool
def task_evaluation(input_state: ToolState) -> TaskAgentOutput:
    """Evaluate essay task achievement/response using IELTS criteria.

    Supports both text-only and image-based prompts (e.g., Academic Writing Task 1
    with charts/graphs). Uses different prompt templates depending on whether a
    valid image URL is provided.

    Args:
        input_state (ToolState): Tool state containing essay, question, image data,
            and assessment tools.

    Returns:
        TaskAgentOutput: Task achievement band score and feedback comments.
    """
    task_output = input_state.task_tool_output
    criteria_output = input_state.criteria_tool_output
    band_output = input_state.band_tool_output
    word_count_penalty = str(
        t.word_count_penalties_tool.func(input_state.essay_type, input_state.essay),
    )

    image_description = (
        f"**This is the description of the image in the question:\n**\n{input_state.image_description}\n"
        if input_state.image_description
        else ""
    )

    prompt_img = IELTS_TASK_IMG_PROMPT.format(
        essay=input_state.essay,
        question=input_state.question,
        criteria="Task Response",
        output_score="task_score",
        output_comments="task_comment",
        task_description_output=task_output,
        criteria_tool_output=criteria_output,
        band_tool_output=band_output,
        image_description=image_description,
        notes=word_count_penalty
        + "\nResponses of 20 words or fewer are rated at Band 1.",
        goal_aditional="Do NOT comment on sentence structure, coherence and cohesion; vocabulary range, accuracy, appropriacy, sophistication; and grammatical accuracy.",
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
        notes=word_count_penalty,
        goal_aditional="Do NOT comment on sentence structure, coherence and cohesion; vocabulary range, accuracy, appropriacy, sophistication; and grammatical accuracy.",
    )

    if input_state.is_image_url():
        response = task_structured.invoke(
            [
                HumanMessage(
                    content=[
                        {"type": "text", "text": prompt_img},
                        {
                            "type": "image_url",
                            "image_url": {"url": input_state.image_url},
                        },
                    ]
                )
            ]
        )
    else:
        response = task_structured.invoke(prompt_no_img)

    return response


# Build SubGraph
subgraph_builder = StateGraph(
    ToolState, input_schema=InputState, output_schema=TaskOutputState
)

# Add node to fetch assessment tools and band descriptors
subgraph_builder.add_node("tools", tools)

# Add node to generate image description for Academic Writing Task 1 visuals
subgraph_builder.add_node("Image_Desc_Tool", image_agent)

# Add node to evaluate criteria
subgraph_builder.add_node("Task Evaluator", task_evaluation)

# Define workflow: START -> tools -> evaluator -> END
subgraph_builder.add_edge(START, "tools")
subgraph_builder.add_edge("tools", "Image_Desc_Tool")
subgraph_builder.add_edge("Image_Desc_Tool", "Task Evaluator")
subgraph_builder.add_edge("Image_Desc_Tool", END)
subgraph_builder.add_edge("Task Evaluator", END)

# Compile the subgraph
graph = subgraph_builder.compile()


def task_agent(data):
    """Execute the task response evaluation agent workflow.

    Args:
        data: Input data for task response assessment.

    Returns:
        Task response evaluation results from the graph execution.
    """
    return graph.invoke(data)
