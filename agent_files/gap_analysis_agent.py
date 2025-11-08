# Import Libraries
import os
from agent_files.agent_states import CentralAgentState, GapAnalysisOutputState
from langgraph.graph import StateGraph, START, END
from agent_files.helper_functions import get_llm
import app.tools.tools as t
from agent_files.helper_functions import (
    map_criteria_to_agent,
    map_criteria_to_comment,
    calculate_overall_band,
    has_hit_target,
    get_weak_bands,
)
import json
from app.tools.prompt_templates import IELTS_GAP_ANALYSIS_PROMPT


# Load environment variables

# Only load .env for local development
if os.getenv("RENDER") is None:
    from dotenv import load_dotenv

    load_dotenv()

# Read API keys and models from environment variables
gemini_api_key = os.getenv("GEMINI_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("OVERALL_MODEL")

# Initialise LLM
llm = get_llm(
    model=model,
    gemini_key=gemini_api_key,
    openai_key=openai_api_key,
    name="overall_agent",
    temperature=0.5,
)

# Bind assessment tools to LLM for structured retrieval of band descriptors and criteria
tools = [t.get_target_band_descriptors_by_criteria, t.assessment_criteria_tool]
overall_tools = llm.bind_tools(tools)


def gap_analysis(input: CentralAgentState) -> CentralAgentState:
    """Analyse essay performance against target band and generate improvement plan.

    Compares actual band scores across all IELTS criteria to the target band. If the target
    is met, returns congratulatory feedback. Otherwise, identifies weak areas and generates
    a detailed, actionable improvement plan using target band descriptors and assessment criteria.

    Args:
        input (CentralAgentState): Central state with all scores, comments, and target band.

    Returns:
        CentralAgentState: Updated state with gap analysis results including overall band,
            target met status, weak areas, and personalized improvement feedback.
    """

    band_scores = {
        "Grammatical Range & Accuracy": input.grammar_score,
        "Coherence & Cohesion": input.coherence_score,
        "Lexical Resource": input.lexical_score,
        "Task Response": input.task_score,
    }

    overall_band = calculate_overall_band(list(band_scores.values()))
    hit_target = has_hit_target(actual=overall_band, target=input.target_band)
    if hit_target:
        return {
            "overall_feedback": "Well Done. The essay meets or exceeds your target band selected. Maintain current writing quality."
        }

    # Identify weak areas
    weak_bands = dict(get_weak_bands(band_scores=band_scores, target=input.target_band))
    weak_comments = {}
    for criterion in weak_bands.keys():
        comment_name = map_criteria_to_comment(criterion)
        weak_comments[criterion] = getattr(input, comment_name, "No comment available")

    # Fetch descriptors & criteria for weak bands
    descriptor_data = {}
    criteria_data = {}
    for criterion in weak_bands.keys():

        descriptor_output = t.get_target_band_descriptors_by_criteria.invoke(
            {
                "essay_type": input.essay_type,
                "agent": map_criteria_to_agent(criterion),
                "band": input.target_band,
            }
        )
        criteria_output = t.assessment_criteria_tool.invoke(
            {
                "essay_type": input.essay_type,
                "agent": map_criteria_to_agent(criterion),
            }
        )

        descriptor_data[criterion] = {"description": descriptor_output}
        criteria_data[criterion] = {"description": criteria_output}

        # Generate improvement plan using LLM
        prompt = IELTS_GAP_ANALYSIS_PROMPT.format(
            overall_band=overall_band,
            target_band=input.target_band,
            weak_bands=weak_bands,
            weak_comments={json.dumps(weak_comments, indent=2)},
            target_band_descriptor_data={json.dumps(descriptor_data, indent=2)},
            criteria_data={json.dumps(criteria_data, indent=2)},
        )

    improvement_plan = llm.invoke(prompt).content

    return {
        "overall_band": overall_band,
        "met_target": False,
        "weak_bands": weak_bands,
        "descriptors_used": descriptor_data,
        "assessment_criteria_used": criteria_data,
        "overall_feedback": improvement_plan,
    }


def gap_analysis_wrapper(input: CentralAgentState) -> GapAnalysisOutputState:
    """Wrapper for gap analysis node in the parallel workflow.

    Executes gap analysis and returns structured output for the END node.
    Runs in parallel with the meta-evaluation agent.

    Args:
        input (CentralAgentState): Central state with all assessment results.

    Returns:
        GapAnalysisOutputState: Structured gap analysis with improvement plan.
    """
    result = gap_analysis(input)  # returns GapAnalysisOutputState

    return result


# Build SubGraph
subgraph_builder = StateGraph(CentralAgentState)

# Add agent node
subgraph_builder.add_node("Gap Analysis Agent", gap_analysis_wrapper)

# Connect nodes
subgraph_builder.add_edge(START, "Gap Analysis Agent")
subgraph_builder.add_edge("Gap Analysis Agent", END)

# Compile the subgraph
graph = subgraph_builder.compile()


def gap_analysis_agent(data):
    """Execute the gap analysis agent workflow.

    Args:
        data: Input data for gap analysis assessment.

    Returns:
        Gap analysis results from the graph execution.
    """
    return graph.invoke(data)
