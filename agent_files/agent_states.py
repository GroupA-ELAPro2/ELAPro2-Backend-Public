from typing import Optional
from pydantic import BaseModel, Field
import requests


class InputState(BaseModel):
    """Input state model for IELTS essay grading submissions.

    Attributes:
        track_id (str): UUID for the essay submission request.
        question (str): The IELTS essay question.
        essay (str): Essay submitted for grading.
        essay_type (int): Writing task type (1-4). 1=General Writing 1,
            2=General Writing 2, 3=Academic Writing 1, 4=Academic Writing 2.
        target_band (int): Target IELTS band score (1-9).
        image_url (Optional[str]): URL of image for Academic Writing Task 1.
        image_description (Optional[str]): Brief description of the image.
    """

    track_id: str = Field(
        min_length=3, description="The UUID for the essay submission request"
    )
    question: str = Field(min_length=1, description="The IELTS essay question")
    essay: str = Field(min_length=1, description="Essay submitted for grading")
    essay_type: int = Field(
        2,
        ge=1,
        le=4,
        description="Integer representation of writing task: 1 - General Writing 1; 2 - General Writing 2; 3 - Academic Writing 1; 4 - Academic Writing 2",
    )
    target_band: int = Field(
        9, ge=1, le=9, description="Target band score selected by the student."
    )
    image_url: Optional[str] = Field(
        default=None, description="URL of the image for Academic Writing Task 1"
    )
    image_description: Optional[str] = Field(
        description="A short summarised description of the image contained in the image_url",
        default=None,
    )

    def is_image_url(self):
        """Check if the image_url URL points to an image by inspecting the Content-Type header.

        Args:
            url (str): URL to validate.

        Returns:
            bool: True if URL points to an image with successful response, False otherwise.
        """
        try:
            response = requests.head(self.image_url, allow_redirects=True, timeout=5)
            response.raise_for_status()
            content_type = response.headers.get("Content-Type", "")
            return content_type.startswith("image/") and (
                200 <= response.status_code < 300
            )
        except requests.exceptions.RequestException as e:
            return False


class GrammarOutputState(BaseModel):
    """Output state for IELTS Grammatical Range and Accuracy assessment.

    Attributes:
        grammar_score (int): Band score (0-9) for grammatical range and accuracy.
        grammar_comment (str): Explanation of score and suggestions for improvement.
    """

    grammar_score: int = Field(
        ge=0,
        le=9,
        description="The IELTS Grammatical Range and Accuracy band score from 0 to 9 for the provided essay and question",
    )
    grammar_comment: str = Field(
        description="Brief comments explaining the reason for the IELTS Grammatical Range and Accuracy band score and suggestions to meet the target band.",
        min_length=3,
    )


class CoherenceOutputState(BaseModel):
    """Output state for IELTS Coherence and Cohesion assessment.

    Attributes:
        coherence_score (int): Band score (0-9) for coherence and cohesion.
        coherence_comment (str): Explanation of score and suggestions for improvement.
    """

    coherence_score: int = Field(
        ge=0,
        le=9,
        description="The IELTS Coherence and Cohesion band score from 0 to 9 for the provided essay and question",
    )
    coherence_comment: str = Field(
        description="Brief comments explaining the reason for the IELTS Coherence and Cohesion band score and suggestions to meet the target band.",
        min_length=3,
    )


class ToolState(InputState):
    """Extended input state with tool outputs for intermediate processing.

    Attributes:
        task_tool_output (Optional[str]): Output from task achievement tool.
        criteria_tool_output (Optional[str]): Output from criteria assessment tool.
        band_tool_output (Optional[str]): Output from band descriptor tool.
    """

    task_tool_output: Optional[str] = None
    criteria_tool_output: Optional[str] = None
    band_tool_output: Optional[str] = None


class LexicalOutputState(BaseModel):
    """Output state for IELTS Lexical Resource assessment.

    Attributes:
        lexical_score (int): Band score (0-9) for lexical resource.
        lexical_comment (str): Explanation of score and suggestions for improvement.
    """

    lexical_score: int = Field(
        ge=0,
        le=9,
        description="The IELTS Lexical Resource band score from 0 to 9 for the provided essay and question",
    )
    lexical_comment: str = Field(
        description="Brief comments explaining the reason for the IELTS Lexical Resource band score and suggestions to meet the target band.",
        min_length=3,
    )


class ImageDescriptionOutput(BaseModel):
    """Output state containing image description for visual prompts.

    Attributes:
        image_description (Optional[str]): Brief summary of the image content.
    """

    image_description: Optional[str] = Field(
        description="A short summarised description of the image contained in the image_url",
        default=None,
    )


class TaskAgentOutput(BaseModel):
    """Output state for IELTS Task Achievement assessment.

    Attributes:
        task_score (int): Band score (0-9) for task achievement.
        task_comment (str): Explanation of score and suggestions for improvement.
    """

    task_score: int = Field(
        ge=0,
        le=9,
        description="The IELTS Task Achievement band score from 0 to 9 for the provided essay and question",
    )
    task_comment: str = Field(
        description="Brief comments explaining the reason for the IELTS Task Achievement band score and suggestions to meet the target band.",
        min_length=3,
    )


class TaskOutputState(TaskAgentOutput, ImageDescriptionOutput):
    """Combined output state for task achievement and image description."""

    pass


class OutputState(
    GrammarOutputState, CoherenceOutputState, LexicalOutputState, TaskOutputState
):
    """Complete output state containing all IELTS assessment criteria scores.

    Attributes:
        track_id (str): UUID for the essay submission request.
        overall_feedback (str): Actionable feedback or improvement plan.
    """

    track_id: str = Field(
        min_length=3, description="The UUID for the essay submission request"
    )
    overall_feedback: str = Field(
        min_length=3,
        default="Overall Feedback Not Generated",
        description="Actionable feedback or improvement plan.",
    )


class CentralAgentState(InputState):
    """Central state for orchestrating IELTS essay grading workflow.

    Attributes:
        grammar_score (Optional[int]): Band score (0-9) for grammar.
        coherence_score (Optional[int]): Band score (0-9) for coherence.
        lexical_score (Optional[int]): Band score (0-9) for lexical resource.
        task_score (Optional[int]): Band score (0-9) for task achievement.
        grammar_comment (Optional[str]): Grammar assessment feedback.
        coherence_comment (Optional[str]): Coherence assessment feedback.
        lexical_comment (Optional[str]): Lexical assessment feedback.
        task_comment (Optional[str]): Task achievement feedback.
        overall_feedback (str): Actionable feedback or improvement plan.
    """

    grammar_score: Optional[int] = Field(default=None, ge=0, le=9)
    coherence_score: Optional[int] = Field(default=None, ge=0, le=9)
    lexical_score: Optional[int] = Field(default=None, ge=0, le=9)
    task_score: Optional[int] = Field(default=None, ge=0, le=9)
    grammar_comment: Optional[str] = None
    coherence_comment: Optional[str] = None
    lexical_comment: Optional[str] = None
    task_comment: Optional[str] = None
    overall_feedback: str = Field(
        min_length=3, default="Overall Feedback Not Generated"
    )


class EvaluationOutputState(BaseModel):
    """Output state for quality evaluation metrics of the grading process.

    Attributes:
        Task_Accuracy (dict | None): Task achievement evaluation metrics.
        Grammar_Evaluation_Quality (dict | None): Grammar assessment quality metrics.
        Lexical_Evaluation_Quality (dict | None): Lexical assessment quality metrics.
        Coherence_Evaluation_Quality (dict | None): Coherence assessment quality metrics.
        Feedback_Quality (dict | None): Overall feedback quality metrics.
        meta_summary (dict | None): Meta-level summary of evaluation.
        usage_metadata (dict | None): Usage and performance metadata.
    """

    Task_Accuracy: dict | None = None
    Grammar_Evaluation_Quality: dict | None = None
    Lexical_Evaluation_Quality: dict | None = None
    Coherence_Evaluation_Quality: dict | None = None
    Feedback_Quality: dict | None = None
    meta_summary: dict | None = None
    usage_metadata: dict | None = None


class GapAnalysisOutputState(OutputState):
    """Output state for gap analysis between current and target band scores.

    Attributes:
        overall_band (float): Average band score (0.0-9.0) across all criteria.
        met_target (bool): Whether the essay met or exceeded the target band.
        weak_bands (dict[str, int]): Criteria below target with their current scores.
        overall_feedback (str): Actionable improvement plan generated by LLM.
        descriptors_used (Optional[dict[str, dict]]): Target band descriptors for weak criteria.
        assessment_criteria_used (Optional[dict[str, dict]]): Assessment criteria used in analysis.
    """

    overall_band: float = Field(
        ge=0.0, le=9.0, description="Computed average band score across all criteria."
    )
    met_target: bool = Field(
        description="Whether the essay met or exceeded the target band."
    )
    weak_bands: dict[str, int] = Field(
        description="Dictionary of weak criteria and their current band scores (below target)."
    )
    overall_feedback: str = Field(
        description="Actionable feedback or improvement plan generated by the LLM."
    )
    descriptors_used: Optional[dict[str, dict]] = Field(
        default=None,
        description="Target band descriptors per weak criterion used to generate the improvement plan.",
    )
    assessment_criteria_used: Optional[dict[str, dict]] = Field(
        default=None,
        description="Assessment criteria per weak criterion used in the analysis.",
    )
