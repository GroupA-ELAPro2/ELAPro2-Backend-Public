# Import Libraries
import os
from agent_files.agent_states import InputState, CoherenceOutputState, ToolState
from agent_files.helper_functions import get_llm
from langgraph.graph import StateGraph, START, END
import app.tools.tools as t
from app.tools.prompt_templates import IELTS_EVALUATION_PROMPT


# Load environment variables

# Only load .env for local development
if os.getenv("RENDER") is None:
    from dotenv import load_dotenv

    load_dotenv()

# Read API keys and models from environment variables
gemini_api_key = os.getenv("GEMINI_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("COHERENCE_MODEL")


# Initialise LLM
llm = get_llm(
    model=model,
    gemini_key=gemini_api_key,
    openai_key=openai_api_key,
    name="coherence_agent",
    temperature=0.1,
)

# Initialise LLM with structured output
coherence_structured = llm.with_structured_output(CoherenceOutputState)


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


# Evaluate Coherence & Cohesion using assessment criteria tool


def coherence_evaluation(input_state: ToolState) -> CoherenceOutputState:
    """Evaluate essay coherence and cohesion using IELTS criteria.

    Args:
        input_state (ToolState): Tool state containing essay, question, and assessment tools.

    Returns:
        CoherenceOutputState: Coherence band score and feedback comments.
    """
    task_output = input_state.task_tool_output
    criteria_output = input_state.criteria_tool_output
    band_output = input_state.band_tool_output

    if "\n" or "\n\n" not in input_state.essay:
        note_paragraphing = """ATTENTION: The essay contains NO line breaks. The Coherence and Cohesion score MUST be reduced by 1–2 bands, depending on the overall cohesion quality. Words signalling paragraph starts (e.g., 'Firstly', 'In conclusion') do not count as paragraph breaks."""
    else:
        note_paragraphing = """No paragraph breaks (no '\n' or '\n\n') in the text should result in a 1–2 band reduction in Coherence and Cohesion, depending on overall cohesion. Words signalling paragraph starts (e.g., 'Firstly', 'In conclusion') do not count as paragraph breaks."""

    prompt = IELTS_EVALUATION_PROMPT.format(
        essay=input_state.essay,
        question=input_state.question,
        criteria="Coherence & Cohesion",
        output_score="coherence_score",
        output_comments="coherence_comment",
        task_description_output=task_output,
        criteria_tool_output=criteria_output,
        band_tool_output=band_output,
        goal_aditional="Do NOT comment on grammar, vocabulary, spelling, or task achievement.",
        notes=note_paragraphing +"\nResponses of 20 words or fewer are rated at Band 1."
    )

    # Call LLM
    response = coherence_structured.invoke(prompt)

    return response


# Build subgraph
subgraph_builder = StateGraph(
    ToolState, input_schema=InputState, output_schema=CoherenceOutputState
)

# Add node to fetch assessment tools and band descriptors
subgraph_builder.add_node("tools", tools)

# Add node to evaluate criteria
subgraph_builder.add_node("Coherence Evaluator", coherence_evaluation)

# Define workflow: START -> tools -> evaluator -> END
subgraph_builder.add_edge(START, "tools")
subgraph_builder.add_edge("tools", "Coherence Evaluator")
subgraph_builder.add_edge("Coherence Evaluator", END)

# Compile the subgraph
graph = subgraph_builder.compile()


def coherence_agent(data):
    """Execute the coherence evaluation agent workflow.

    Args:
        data: Input data for coherence assessment.

    Returns:
        Coherence evaluation results from the graph execution.
    """
    return graph.invoke(data)
