from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
import math


def get_task_type_string(task_int: int) -> str:
    """Convert IELTS task type integer to human-readable string.

    Args:
        task_int (int): Task type identifier (1-4).

    Returns:
        str: Descriptive task type name.
    """
    types = {
        1: "General Writing Task 1",
        2: "General Writing Task 2",
        3: "Academic Writing Task 1",
        4: "Academic Writing Task 2",
    }
    return types[task_int]


def map_essay_type(essay_type: int):
    """Map essay type integer to exam type and task type components.

    Args:
        essay_type (int): Essay type identifier (1-4).
            1 = General Training Task 1
            2 = General Training Task 2
            3 = Academic Task 1
            4 = Academic Task 2

    Returns:
        tuple: (exam_type, task_type_str, task_type_int)
            - exam_type (str): "General Training" or "Academic"
            - task_type_str (str): "Task 1" or "Task 2"
            - task_type_int (int): 1 or 2

    Raises:
        ValueError: If essay_type is not between 1 and 4.
    """
    if essay_type in [1, 2]:
        exam_type = "General Training"
    elif essay_type in [3, 4]:
        exam_type = "Academic"
    else:
        raise ValueError("Invalid essay_type, must be 1-4")

    task_type = 1 if essay_type in [1, 3] else 2
    return exam_type, f"Task {task_type}", task_type


def map_agent_to_criteria(agent_name: str, task_number: int = None) -> str:
    """
    Map a LangGraph agent name to the corresponding IELTS criterion in the JSON.

    For Task agent, the mapping depends on task_number:
        Task 1 -> "Task Achievement"
        Task 2 -> "Task Response"

    Args:
        agent_name (str): Name of the agent (e.g., 'grammar_agent')
        task_number (int, optional): Required for task_agent (1 or 2)

    Returns:
        str: Corresponding JSON criterion
    """
    agent_name_lower = agent_name.lower()

    if agent_name_lower == "task_agent":
        if task_number is None:
            raise ValueError("task_number is required for task_agent")
        if task_number == 1:
            return "Task Achievement"
        elif task_number == 2:
            return "Task Response"
        else:
            raise ValueError("task_number must be Task 1 or Task 2")

    mapping = {
        "grammar_agent": "Grammatical Range & Accuracy",
        "lexical_agent": "Lexical Resource",
        "coherence_agent": "Coherence & Cohesion",
    }

    if agent_name_lower not in mapping:
        raise ValueError(f"Unknown agent name: {agent_name}")

    return mapping[agent_name_lower]


def map_criteria_to_agent(criterion: str) -> str:
    """
    Map an IELTS scoring criterion to the corresponding LangGraph agent name.

    For criteria related to task performance:
        "Task Achievement" -> task_agent (Task 1)
        "Task Response"    -> task_agent (Task 2)

    Args:
        criterion (str): The IELTS criterion name (e.g., 'Lexical Resource')

    Returns:
        str: Corresponding agent name (e.g., 'lexical_agent' or 'task_agent')
    """
    criterion_normalised = criterion.strip().lower()

    task_mapping = {"task achievement": "task_agent", "task response": "task_agent"}

    mapping = {
        "grammatical range & accuracy": "grammar_agent",
        "lexical resource": "lexical_agent",
        "coherence & cohesion": "coherence_agent",
        **task_mapping,
    }

    if criterion_normalised not in mapping:
        raise ValueError(f"Unknown criterion: {criterion}")

    return mapping[criterion_normalised]


def map_criteria_to_comment(criterion: str) -> str:
    """
    Map an IELTS scoring criterion to the corresponding LangGraph comment name.

    For criteria related to task performance:
        "Task Achievement" -> task_comment (Task 1)
        "Task Response"    -> task_comment (Task 2)

    Args:
        criterion (str): The IELTS criterion name (e.g., 'Lexical Resource')

    Returns:
        str: Corresponding comment name (e.g., 'lexical_comment' or 'task_comment')
    """
    criterion_normalised = criterion.strip().lower()

    task_mapping = {"task achievement": "task_comment", "task response": "task_comment"}

    mapping = {
        "grammatical range & accuracy": "grammar_comment",
        "lexical resource": "lexical_comment",
        "coherence & cohesion": "coherence_comment",
        **task_mapping,
    }

    if criterion_normalised not in mapping:
        raise ValueError(f"Unknown criterion: {criterion}")

    return mapping[criterion_normalised]


### Functions used in the Gap Analysis Agent


def calculate_overall_band(band_scores: list[int]) -> int:
    """Calculate the IELTS band score across all criteria.

    Args:
        band_scores (list[int]): List of band scores (0-9) for each criterion.

    Returns:
        int: Average band score, capped at maximum of 9.
    """
    if len(band_scores) != 4:
        raise ValueError("4 band scores required to calculate overall score")
    for score in band_scores:
        if score < 0 or score > 9:
            raise ValueError(
                "Individual band scores must be an integer between 0 and 9"
            )
    average = sum(band_scores) / len(band_scores)
    score = math.floor(average * 2) / 2
    return score


def has_hit_target(actual: int, target: int) -> bool:
    """Check if the actual band score meets or exceeds the target.

    Args:
        actual (int): Actual band score achieved.
        target (int): Target band score.

    Returns:
        bool: True if actual >= target, False otherwise.
    """
    return actual >= target


def get_weak_bands(band_scores: dict[str, int], target: int) -> dict[str, int]:
    """Identify criteria with band scores below the target.

    Args:
        band_scores (dict[str, int]): Mapping of criteria names to their band scores.
        target (int): Target band score.

    Returns:
        dict[str, int]: Criteria that scored below target with their scores.
    """
    return {k: v for k, v in band_scores.items() if v < target}


def get_strong_bands(band_scores: dict[str, int], target: int) -> dict[str, int]:
    """Identify criteria with band scores meeting or exceeding the target.

    Args:
        band_scores (dict[str, int]): Mapping of criteria names to their band scores.
        target (int): Target band score.

    Returns:
        dict[str, int]: Criteria that met or exceeded target with their scores.
    """
    return {k: v for k, v in band_scores.items() if v >= target}


def get_llm(
    model: str,
    name: str,
    temperature: float,
    gemini_key: str | None = None,
    openai_key: str | None = None,
):
    """Initialize and return an LLM instance based on model type.

    Supports Google Gemini and OpenAI GPT models. Automatically selects the
    appropriate provider based on model name prefix.

    Args:
        model (str): Model identifier (must start with "gemini-" or "gpt-").
        name (str): Name identifier for the LLM instance.
        temperature (float): Sampling temperature for response generation.
        gemini_key (str | None): Google Gemini API key. Required for Gemini models.
        openai_key (str | None): OpenAI API key. Required for GPT models.

    Returns:
        ChatGoogleGenerativeAI | ChatOpenAI: Configured LLM instance.

    Raises:
        ValueError: If model prefix is invalid or required API key is missing.
    """

    if model.startswith("gemini-"):

        if not gemini_key:
            raise ValueError(
                "GEMINI_API_KEY not found in environment variables. "
                "Make sure to set it in your local .env file or on Render."
            )
        llm = ChatGoogleGenerativeAI(
            model=model, api_key=gemini_key, name=name, temperature=temperature
        )
    elif model.startswith("gpt-"):

        if not openai_key:
            raise ValueError(
                "OPENAI_API_KEY not found in environment variables. "
                "Make sure to set it in your local .env file or on Render."
            )
        llm = ChatOpenAI(
            model=model, api_key=openai_key, name=name, temperature=temperature
        )
    else:
        raise ValueError("LLM Model must be either 'gemini-' or 'gpt-'")
    return llm
