# Import Libraries
import os
import json
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from agent_files.agent_states import EvaluationOutputState, CentralAgentState
from app.tools.prompt_templates import LLM_EVALUATION_PROMPT
from datetime import datetime
from app.tools import tools as t
import re

# Load environment variables

# Only load .env for local development
if os.getenv("RENDER") is None:
    from dotenv import load_dotenv

    load_dotenv()

# Read Gemini API key and models from environment variables
api_key = os.getenv("OPENAI_API_KEY")
eval_model = os.getenv("EVAL_MODEL")

if not api_key:
    raise ValueError("❌ API_KEY missing — please set it in your environment.")


# Initialise LLM
llm = ChatOpenAI(
    name="meta_evaluator", model=eval_model, temperature=0, api_key=api_key
)


def safe_json_parse(text: str):
    """Clean and safely parse JSON-like LLM output.

    Removes markdown code fences and parses the JSON content into a Python dictionary.
    Provides clear error messages if parsing fails.

    Args:
        text (str): Raw text output from LLM, potentially containing JSON wrapped in markdown.

    Returns:
        dict: Parsed JSON as a Python dictionary.

    Raises:
        ValueError: If the text is empty or contains invalid JSON.
    """
    if not text or not text.strip():
        raise ValueError("❌ Empty response content from LLM.")

    cleaned = re.sub(r"^```json|```$", "", text.strip(), flags=re.MULTILINE).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        print("⚠️ Failed to parse JSON. Raw response:\n", text)
        raise ValueError(f"❌ Invalid JSON returned by model: {e}")


def evaluate_model_output_to_json(
    data: CentralAgentState, base_dir: str = "evaluations"
):
    """Evaluate IELTS grading model output against official standards and save results.

    Performs meta-evaluation of the model's feedback by comparing it against IELTS band
    descriptors and assessment criteria. Results are saved as a timestamped JSON file.

    Args:
        data (CentralAgentState): Central state containing all scores, comments, and essay details.
        base_dir (str): Directory path for saving evaluation results. Defaults to "evaluations".

    Returns:
        EvaluationOutputState: Structured evaluation metrics including quality assessments
            for each criterion and usage metadata.
    """
    if isinstance(data.track_id, tuple):
        track_id = track_id[0]

    else:
        track_id = data.track_id

    agent_names = {
        1: "task_agent",
        2: "grammar_agent",
        3: "lexical_agent",
        4: "coherence_agent",
    }

    descritors_task = (
        t.get_target_band_descriptors_by_criteria.func(
            data.essay_type, agent_names[1], int(data.task_score)
        ),
    )
    descritors_grammar = (
        t.get_target_band_descriptors_by_criteria.func(
            data.essay_type, agent_names[2], int(data.grammar_score)
        ),
    )
    descritors_lexical = (
        t.get_target_band_descriptors_by_criteria.func(
            data.essay_type, agent_names[3], int(data.lexical_score)
        ),
    )
    descritors_coherence = t.get_target_band_descriptors_by_criteria.func(
        data.essay_type, agent_names[4], int(data.coherence_score)
    )

    prompt = LLM_EVALUATION_PROMPT.format(
        track_id=track_id,
        essay=data.essay,
        question=data.question,
        essay_type=data.essay_type,
        grammar_comment=data.grammar_comment,
        coherence_comment=data.coherence_comment,
        lexical_comment=data.lexical_comment,
        task_comment=data.task_comment,
        overall_feedback=data.overall_feedback,
        task_description=t.task_description_tool.func(essay_type=data.essay_type),
        assessment_criteria=t.all_assessment_criteria_tool.func(data.essay_type),
        descritors_for_actual_band_task=descritors_task,
        descritors_for_actual_band_grammar=descritors_grammar,
        descritors_for_actual_band_lexical=descritors_lexical,
        descritors_for_actual_band_coherence=descritors_coherence,
    )

    reponse = llm.invoke(prompt)

    response_content = safe_json_parse(reponse.content)

    response_metadata = reponse.response_metadata

    response_metadata_summary = {
        "completion_tokens": response_metadata["token_usage"]["completion_tokens"],
        "prompt_tokens": response_metadata["token_usage"]["prompt_tokens"],
        "total_tokens": response_metadata["token_usage"]["total_tokens"],
        "model_name": response_metadata["model_name"],
    }

    output = EvaluationOutputState(
        Task_Accuracy=response_content["task_accuracy"],
        Grammar_Evaluation_Quality=response_content["grammar_eval_qualy"],
        Lexical_Evaluation_Quality=response_content["lexical_eval_qualy"],
        Coherence_Evaluation_Quality=response_content["coherence_eval_qualy"],
        Feedback_Quality=response_content["feedback_qualy"],
        meta_summary=response_content["meta_summary"],
        usage_metadata=response_metadata_summary,
    )

    json_output_dict = {**output.__dict__, **data.model_dump()}

    os.makedirs(base_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"meta_eval_{data.track_id}_{timestamp}.json"
    output_path = os.path.join(base_dir, filename)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(json_output_dict, f, indent=4, ensure_ascii=False)

    print(f"✅ Meta-evaluation saved to {output_path}")

    return output


# Build SubGraph
subgraph_builder = StateGraph(
    EvaluationOutputState,
    input_schema=CentralAgentState,
    output_schema=EvaluationOutputState,
)

# Add tool nodes
subgraph_builder.add_node("Meta Evaluation", evaluate_model_output_to_json)

# Connect nodes
subgraph_builder.add_edge(START, "Meta Evaluation")
subgraph_builder.add_edge("Meta Evaluation", END)

# Compile the subgraph
graph = subgraph_builder.compile()


def meta_eval_agent(data):
    """Execute the meta evaluation agent workflow.

    Args:
        data: Input data for meta evaluation assessment.

    Returns:
        Meta evaluation results from the graph execution.
    """
    return graph.invoke(data)
