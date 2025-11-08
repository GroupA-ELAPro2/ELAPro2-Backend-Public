from app.tools.band_descriptor_tool import BandDescriptorTool
from app.tools.key_assessment_criteria_tool import KeyAssessmentCriteriaTool
from langchain.tools import Tool, StructuredTool

"""IELTS assessment tools for retrieving band descriptors and assessment criteria.

This module initialises and exposes structured tools for accessing IELTS band descriptors
and key assessment criteria. Tools are designed for use in LLM-based essay evaluation
workflows.
"""

# Initialise the BandDescriptorTool with Academic and General Training JSON files
band_tool = BandDescriptorTool(
    "ielts_descriptors_academic.json", "ielts_descriptors_general.json"
)

# Initialise the KeyAssessmentCriteriaTool with Academic and General Training JSON files
criteria_tool = KeyAssessmentCriteriaTool(
    "ielts_assessment_criteria_academic.json", "ielts_assessment_criteria_general.json"
)

# Tools related to the Band Score descriptors

get_all_band_descriptors_by_criteria = StructuredTool(
    name="band_descriptors_by_criteria_tool",
    args_schema={"essay_type": (int), "agent": (str), "band": (int)},
    func=band_tool.get_all_band_descriptors_by_criteria,
    description=(
        "Use this tool to get all band descriptors for a specific IELTS essay criterion. "
        "Inputs: essay_type (int) and agent name (str). Returns descriptors including common, specific, and critical negative features."
    ),
)
"""Tool for retrieving all band descriptors for a specific assessment criterion.

Returns comprehensive descriptors across all band levels (1-9) for a given criterion,
useful for understanding the full range of expectations during scoring.
"""

get_target_band_descriptors_by_criteria = StructuredTool(
    name="target_band_descriptors_by_criteria_tool",
    args_schema={"essay_type": (int), "agent": (str), "band": (int)},
    func=band_tool.get_target_band_descriptors_by_criteria,
    description=(
        "Use this tool to get the band descriptors for a specific criterion at a specific band score. "
        "Inputs: essay_type (int), agent name (str), band (int). Useful to align an essay to a target band."
    ),
)
"""Tool for retrieving band descriptors at a specific band level for a criterion.

Returns targeted descriptors for checking if an essay meets requirements for a
particular band score in a specific assessment criterion.
"""

get_all_descriptors_by_band = StructuredTool(
    name="band_descriptors_by_band_tool",
    args_schema={"essay_type": (int), "band": (int)},
    func=band_tool.get_all_descriptors_by_band,
    description=(
        "Use this tool to get all criteria descriptors for a given band score. "
        "Inputs: essay_type (int), band (int). Returns descriptors including common, specific, and critical negative features for all criteria."
    ),
)
"""Tool for retrieving descriptors for all criteria at a specific band level.

Returns comprehensive descriptors across all assessment criteria for a target band,
useful for holistic evaluation of essay alignment with a band score.
"""

get_all_descriptors = StructuredTool(
    name="all_band_descriptors_tool",
    args_schema={"essay_type": (int)},
    func=band_tool.get_all_descriptors,
    description=(
        "Use this tool to get all band descriptors for all criteria and all bands of an IELTS essay. "
        "Input: essay_type (int). Useful for full overview of the descriptors."
    ),
)
"""Tool for retrieving complete band descriptor dataset for an essay type.

Returns all descriptors across all criteria and all band levels, providing
a comprehensive reference for IELTS assessment standards.
"""

get_hierarchy_description = Tool(
    name="hierarchy_band_descriptors_tool",
    func=band_tool.get_hierarchy_description,
    description=(
        "Use this tool to understand the hierarchical structure of the Band Descriptor JSON file. "
        "No inputs required."
    ),
)
"""Tool for retrieving band descriptor data structure documentation.

Returns a description of the JSON hierarchy used to organise band descriptors,
useful for understanding data organisation.
"""

# Tools related to Key Assessment Criteria

assessment_criteria_tool = StructuredTool(
    name="assessment_criteria_tool",
    func=criteria_tool.get_assessment_by_criteria,
    args_schema={"essay_type": (int), "agent": (str)},
    description=(
        "Use this tool to get the assessment criteria for a specific IELTS essay criterion. "
        "Inputs: essay_type (int), agent name (str). Returns common and specific assessments for the criterion."
    ),
)
"""Tool for retrieving assessment criteria for a specific criterion.

Returns common and exam-specific assessment standards for a particular criterion
(e.g., grammar, coherence), used during scoring to evaluate essay quality.
"""

all_assessment_criteria_tool = StructuredTool(
    name="all_assessment_criteria_tool",
    func=criteria_tool.get_all_assessment_criteria,
    args_schema={"essay_type": (int)},
    description=(
        "Use this tool to get all assessment criteria for a given essay type. "
        "Input: essay_type (int). Returns all criteria with penalties and structured explanatory text."
    ),
)
"""Tool for retrieving complete assessment criteria for an essay type.

Returns all assessment criteria across all categories with penalty information,
providing comprehensive standards for IELTS essay evaluation.
"""

hierarchy_assessment_criteria_tool = Tool(
    name="hierarchy_assessment_criteria_tool",
    func=criteria_tool.get_hierarchy_description,
    description=(
        "Use this tool to understand the hierarchical structure of the Assessment Criteria JSON file. "
        "No inputs required."
    ),
)
"""Tool for retrieving assessment criteria data structure documentation.

Returns a description of the JSON hierarchy used to organise assessment criteria,
useful for understanding data organisation.
"""

task_description_tool = StructuredTool(
    name="task_description_tool",
    func=criteria_tool.get_task_description,
    args_schema={"essay_type": int},
    description=(
        "Use this tool to get the description of a given IELTS essay task. "
        "Input: essay_type (int). Useful for providing task context in scoring or reasoning."
    ),
)
"""Tool for retrieving task description for an essay type.

Returns the official IELTS task description, providing context about what
the task requires and how it should be approached.
"""

task_word_requirement_tool = Tool(
    name="task_word_requirement_tool",
    func=criteria_tool.get_task_word_requirement,
    description=(
        "Use this tool to get the word requirement for a given IELTS essay task. "
        "Input: essay_type (int). Useful for verifying minimum word count."
    ),
)
"""Tool for retrieving minimum word count requirement for an essay type.

Returns the required minimum number of words for the task, used to verify
if an essay meets basic length requirements.
"""

penalties_tool = Tool(
    name="penalties_tool",
    func=criteria_tool.get_penalties_by_exam_type,
    description=(
        "Use this tool to retrieve the penalties applicable for a given IELTS exam type. "
        "Input: exam_type (str: 'Academic' or 'General Training'). Returns a JSON-formatted list of penalties."
    ),
)
"""Tool for retrieving penalty information for an exam type.

Returns structured information about penalties that apply to essays (e.g., for
being under word count, off-topic, or memorised), used during scoring.
"""

word_count_penalties_tool = StructuredTool(
    name="word_count_penalties_tool",
    func=criteria_tool.get_word_count_penalty,
    args_schema={"essay_type": int, "essay": str},
    description=(
        "Tool to calculate the word count penalty for a given essay."
        "Inputs: essay_type (int) – the type of essay, essay (str) – the essay text."
        "Useful for determining scoring deductions based on word count requirements."
    ),
)
"""
Tool for retrieving the word count penalties applied given a specific essay type and set rules.

Returns the words required, actual word count and the penalty applied, if necessary.
"""
