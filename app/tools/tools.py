from app.tools.band_descriptor_tool import BandDescriptorTool
from app.tools.key_assessment_criteria_tool import KeyAssessmentCriteriaTool
from langchain.tools import Tool, StructuredTool

# Initialise the BandDescriptorTool once
band_tool = BandDescriptorTool("ielts_descriptors_academic.json", "ielts_descriptors_general.json")

# Initialise the BandDescriptorTool once
criteria_tool = KeyAssessmentCriteriaTool("ielts_assessment_criteria_academic.json", "ielts_assessment_criteria_general.json")

### Tools related to the Band Score descriptors ###

get_all_band_descriptors_by_criteria = StructuredTool(
    name="band_descriptors_by_criteria_tool",
    args_schema={"essay_type": (int), "agent": (str), "band": (int)},
    func=band_tool.get_all_band_descriptors_by_criteria,
    description=(
        "Use this tool to get all band descriptors for a specific IELTS essay criterion. "
        "Inputs: essay_type (int) and agent name (str). Returns descriptors including common, specific, and critical negative features."
    )
)

get_target_band_descriptors_by_criteria = StructuredTool(
    name="target_band_descriptors_by_criteria_tool",
    args_schema={"essay_type": (int), "agent": (str), "band": (int)},
    func=band_tool.get_target_band_descriptors_by_criteria,
    description=(
        "Use this tool to get the band descriptors for a specific criterion at a specific band score. "
        "Inputs: essay_type (int), agent name (str), band (int). Useful to align an essay to a target band."
    )
)

get_all_descriptors_by_band = StructuredTool(
    name="band_descriptors_by_band_tool",
    args_schema={"essay_type": (int), "band": (int)},
    func=band_tool.get_all_descriptors_by_band,
    description=(
        "Use this tool to get all criteria descriptors for a given band score. "
        "Inputs: essay_type (int), band (int). Returns descriptors including common, specific, and critical negative features for all criteria."
    )
)

get_all_descriptors = StructuredTool(
    name="all_band_descriptors_tool",
    args_schema={"essay_type": (int)},
    func=band_tool.get_all_descriptors,
    description=(
        "Use this tool to get all band descriptors for all criteria and all bands of an IELTS essay. "
        "Input: essay_type (int). Useful for full overview of the descriptors."
    )
)

get_hierarchy_description = Tool(
    name="hierarchy_band_descriptors_tool",
    func=band_tool.get_hierarchy_description,
    description=(
        "Use this tool to understand the hierarchical structure of the Band Descriptor JSON file. "
        "No inputs required."
    )
)

### Tools related to Key Assessment Criteria ###

assessment_criteria_tool = StructuredTool(
    name="assessment_criteria_tool",
    func=criteria_tool.get_assessment_by_criteria,
    args_schema={"essay_type": (int), "agent": (str)},
    description=(
        "Use this tool to get the assessment criteria for a specific IELTS essay criterion. "
        "Inputs: essay_type (int), agent name (str). Returns common and specific assessments for the criterion."
    )
)

all_assessment_criteria_tool = StructuredTool(
    name="all_assessment_criteria_tool",
    func=criteria_tool.get_all_assessment_criteria,
    args_schema={"essay_type": (int)},
    description=(
        "Use this tool to get all assessment criteria for a given essay type. "
        "Input: essay_type (int). Returns all criteria with penalties and structured explanatory text."
    )
)

hierarchy_assessment_criteria_tool = Tool(
    name="hierarchy_assessment_criteria_tool",
    func=criteria_tool.get_hierarchy_description,
    description=(
        "Use this tool to understand the hierarchical structure of the Assessment Criteria JSON file. "
        "No inputs required."
    )
)

task_description_tool = StructuredTool(
    name="task_description_tool",
    func=criteria_tool.get_task_description,
    args_schema={"essay_type": int},
    description=(
        "Use this tool to get the description of a given IELTS essay task. "
        "Input: essay_type (int). Useful for providing task context in scoring or reasoning."
    )
)

task_word_requirement_tool = Tool(
    name="task_word_requirement_tool",
    func=criteria_tool.get_task_word_requirement,
    description=(
        "Use this tool to get the word requirement for a given IELTS essay task. "
        "Input: essay_type (int). Useful for verifying minimum word count."
    )
)

penalties_tool = Tool(
    name="penalties_tool",
    func=criteria_tool.get_penalties_by_exam_type,
    description=(
        "Use this tool to retrieve the penalties applicable for a given IELTS exam type. "
        "Input: exam_type (str: 'Academic' or 'General Training'). Returns a JSON-formatted list of penalties."
    )
)