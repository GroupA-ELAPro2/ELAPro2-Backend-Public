#Function to return the string output of the task type
def get_task_type_string(task_int:int) -> str:
    types = {
        1:"General Writing Task 1",
        2:"General Writing Task 2",
        3:"Academic Writing Task 1",
        4:"Academic Writing Task 2"
    }
    return types[task_int]


def map_essay_type(essay_type: int):
    """
    Map essay_type integer (1-4) to exam_type and task_type.
    Returns a tuple: (exam_type, task_type)
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
        "coherence_agent": "Coherence & Cohesion"
    }
    
    if agent_name_lower not in mapping:
        raise ValueError(f"Unknown agent name: {agent_name}")
    
    return mapping[agent_name_lower]

from typing import Optional

class task_maps():
    #Class to generate various outputs based on the essay type index

    def __init__(self,task_int:int,agent:Optional[str]=None):
        if not isinstance(task_int,int):
            raise TypeError("Value must be an integer from 1-4")
        if not (isinstance(agent,str) or isinstance(agent,None)):
            raise TypeError("agent must be a string")
        if task_int < 1 or task_int > 4:
            raise ValueError("Invalid essay_type, must be 1-4")
        self.__task_int = task_int
        self.__exam_type = "General Training" if task_int in [1, 2] else "Academic"
        self.__task_number = 1 if task_int in [1, 3] else 2
        self.__exam_task_str = f"{self.__exam_type} Writing Task {self.__task_number}"
        self.set_agent(agent)
        self.__mapping = {
        "grammar_agent": "Grammatical Range & Accuracy",
        "lexical_agent": "Lexical Resource",
        "coherence_agent": "Coherence & Cohesion"}
        if self.__agent ==" task_agent":
            match self.__task_number:
                case 1:
                    self.__criteria = "Task Achievement"
                case 2:
                    self.__criteria = "Task Response"
        elif self.__agent in self.__mapping.keys():
            self.__criteria = self.__mapping[self.__agent]
        else:
            raise ValueError(f"Unknown agent name: {self.__agent}")           
        
    def get_task_int(self):
        return self.__task_int
        
    def exam_type(self):
        return self.__exam_type

    def task_number(self):
        return self.__task_number

    def string(self):
        return self.__exam_task_str
    
    def set_agent(self,agent:str):
        if not (isinstance(agent,str) or isinstance(agent,None)):
            raise TypeError("agent must be a string")
        self.__agent = agent
        return None


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
    
    task_mapping = {
        "task achievement": "task_agent",
        "task response": "task_agent"
    }
    
    mapping = {
        "grammatical range & accuracy": "grammar_agent",
        "lexical resource": "lexical_agent",
        "coherence & cohesion": "coherence_agent",
        **task_mapping
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
    
    task_mapping = {
        "task achievement": "task_comment",
        "task response": "task_comment"
    }
    
    mapping = {
        "grammatical range & accuracy": "grammar_comment",
        "lexical resource": "lexical_comment",
        "coherence & cohesion": "coherence_comment",
        **task_mapping
    }
    
    if criterion_normalised not in mapping:
        raise ValueError(f"Unknown criterion: {criterion}")
    
    return mapping[criterion_normalised]


### Functions used in the Gap Analysis Agent

def calculate_overall_band(band_scores: list[int]) -> int:
    """Calculate the average IELTS band (rounded, max 9)."""
    # avg = round(sum(band_scores) / len(band_scores))
    avg = sum(band_scores) / len(band_scores) 
    return min(avg, 9)


def has_hit_target(actual: int, target: int) -> bool:
    """Return whether actual score ≥ target."""
    return actual >= target


def get_weak_bands(band_scores: dict[str, int], target: int) -> dict[str, int]:
    """Return only bands below the target."""
    return {k: v for k, v in band_scores.items() if v < target}


def get_strong_bands(band_scores: dict[str, int], target: int) -> dict[str, int]:
    """Return only bands ≥ target."""
    return {k: v for k, v in band_scores.items() if v >= target}

def get_llm(model:str,name:str,temperature:float,gemini_key:str|None=None,openai_key:str|None=None):
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_openai import ChatOpenAI
    if model.startswith('gemini-'):
        # Raise clear error if the key is missing
        if not gemini_key:
            raise ValueError(
                "GEMINI_API_KEY not found in environment variables. "
                "Make sure to set it in your local .env file or on Render."
            )
        llm = ChatGoogleGenerativeAI(model=model,api_key=gemini_key,name=name,temperature=temperature)
    elif model.startswith('gpt-'):
        # Raise clear error if the key is missing
        if not openai_key:
            raise ValueError(
                "OPENAI_API_KEY not found in environment variables. "
                "Make sure to set it in your local .env file or on Render."
            )
        llm = ChatOpenAI(model=model,api_key=openai_key,name=name,temperature=temperature)
    else:
        raise ValueError("LLM Model must be either 'gemini-' or 'gpt-'")
    return llm
        