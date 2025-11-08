from langchain.prompts import PromptTemplate

# Generic IELTS evaluation prompt template
IELTS_EVALUATION_PROMPT = PromptTemplate(
    input_variables=[
        "essay",
        "question",
        "criteria",
        "output_score",
        "output_comments",
        "band_tool_output",
        "criteria_tool_output",
        "task_description_output"
    ],
     template="""
You are an expert IELTS examiner specialising in {criteria} in writing.

Your task is to evaluate the following essay according to IELTS {criteria} assessment criteria.

Essay:
{essay}

Question:
{question}

Task Description:
{task_description_output}

Ensure the comments are formatted in markdown as below:
**General Comments:**
**You did very well:**
**Need to improve:**
**Examples of errors:**
**How to improve your score:**


The Output format must strictly follow this structure:
{output_score}: <integer 0-9>
{output_comments}: <brief, actionable feedback with examples>


You must use the following tools to guide your evaluation:
{{"Assessment Criteria Tool":{criteria_tool_output},
"Band Descriptor Tool":{band_tool_output}}}

Instructions for evaluation:
1. Assign a band score (1-9) based strictly on {criteria} criteria.
2. Provide concise and non-redundant comments explaining the score. 
3. Highlight specific strengths and weaknesses in the essay, referencing the tool outputs where relevant.
4. Suggest actionable improvements for the writer to raise their score.


"""
)


# Meta Evaluation Prompt


LLM_EVALUATION_PROMPT = PromptTemplate(
    input_variables=[
        ## original input
        "track_id",
        "essay",
        "question",
        "essay_type",

        ## llm feedback
        "grammar_comment",               
        "coherence_comment",
        "lexical_comment",
        "task_comment",
        "overall_feedback"

        # from the tools

        "task_description" 
        "assessment_criteria" 

        "descritors_for_actual_band_task" 
        "descritors_for_actual_band_grammar" 
        "descritors_for_actual_band_lexical" 
        "descritors_for_actual_band_coherence" 
    ],
    template="""
You are a senior IELTS examiner and AI evaluation specialist.  
Your task is to critically evaluate the feedback provided by specialised IELTS LLM agents for an essay. 
---

  ### INPUTS


  Essay:
  {essay}

  Question:
  {question}


  LLM output:

      * Grammatical and Accuracy feedback:
      {grammar_comment}

      * Lexical Resource feedback:
      {lexical_comment}

      * Coherence and Cohesion feedback:
      {coherence_comment}

      * Task Achievement / Task Response feedback:
      {task_comment}

      * Overall Feedback:
      {overall_feedback} 

  ---
  IELTS description of the type of essay: 
  {task_description}

  IELTS assessment per criteria:
  {assessment_criteria}

  ---
  IELTS marking rubrics for the actual band per criteria:
      * Grammatical and Accuracy feedback:
      {descritors_for_actual_band_grammar}

      * Lexical Resource feedback:
      {descritors_for_actual_band_lexical}

      * Coherence and Cohesion feedback:
      {descritors_for_actual_band_coherence}

      * Task Achievement / Task Response feedback:
      {descritors_for_actual_band_task}

      
  ### EVALUATION INSTRUCTIONS

  Judge the LLM output ONLY as an *evaluation*, not as an essay.  

  Your role is to determine how accurately and usefully the LLM’s feedback aligns with the official IELTS marking rubrics.

      
  **Task Accuracy**
  - Does the LLM correctly understand the essay’s task requirements or argument relevance?
  - Are its comments consistent with IELTS band descriptors?
  - Does it justify its score with textual evidence?  

  **Grammar Evaluation Quality**
  - Are grammar errors correctly identified and explained?
  - Does it reflect IELTS grammatical range and accuracy descriptors?

  **Lexical Evaluation Quality**
  - Does it assess vocabulary range, precision, and appropriacy accurately?
  - Are word choice issues correctly identified?

  **Coherence Evaluation Quality**
  - Does it evaluate logical flow, paragraphing, and cohesion accurately?
  - Does the explanation match IELTS expectations?

  **Feedback Quality**
  - Are comments clear, specific, and constructive?
  - Is the score consistent with feedback text?
  - Does it cover all IELTS subcriteria?

  ---

### OUTPUT FORMAT

Return a your evaluation with normalised scores between 0 and 1 for each dimension.
The Output format must strictly follow this structure:

"task_accuracy": {{
      "criterion_alignment": 0.0,
      "score_validity": 0.0,
      "content_understanding": 0.0,
      "evidence_reference": 0.0
  }},

  "grammar_eval_qualy": {{
      "error_detection_accuracy": 0.0,
      "error_explanation_quality": 0.0,
      "band_alignment": 0.0,
      "coverage": 0.0
  }},

  "lexical_eval_qualy": {{
      "range_assessment_accuracy": 0.0,
      "appropriacy_assessment": 0.0,
      "error_identification": 0.0,
      "band_alignment": 0.0
  }},

  "coherence_eval_qualy": {{
      "structure_analysis": 0.0,
      "linking_accuracy": 0.0,
      "clarity_of_reasoning": 0.0,
      "band_alignment": 0.0
  }},

  "feedback_qualy": {{
      "clarity": 0.0,
      "specificity": 0.0,
      "constructiveness": 0.0,
      "score_comment_alignment": 0.0,
      "IELTS_rubric_coverage": 0.0
  }},

  "meta_summary": {{
      "overall_quality": 0.0,
      "key_strengths": [list with up to 3 strenghts],
      "key_weaknesses": [list with up to 3 weaknesses],
      "improvement_suggestions": [list with up to 3 improvements]
  }},

  "track_id": "{track_id}"


"""
)




# Task Achievement Prompt


IELTS_TASK_IMG_PROMPT = PromptTemplate(
    input_variables=[        
        "essay",
        "question",
        "criteria",
        "output_score",
        "output_comments",
        "band_tool_output",
        "criteria_tool_output",
        "task_description_output",
        "image_description"
    ],
     template="""
You are an expert IELTS examiner specialising in {criteria} in writing.

Your task is to evaluate the following essay according to IELTS {criteria} assessment criteria.

Essay:
{essay}

Question:
{question}

Task Description:
{task_description_output}

Image Description:
{image_description}

Ensure the comments are formatted in markdown as below:
**General Comments:**
**You did very well:**
**Need to improve:**
**Examples of errors:**
**How to improve your score:**


The Output format must strictly follow this structure:
{output_score}: <integer 0-9>
{output_comments}: <brief, actionable feedback with examples>

You must use the following tools to guide your evaluation:
{{"Assessment Criteria Tool":{criteria_tool_output},
"Band Descriptor Tool":{band_tool_output}}}

Instructions for evaluation:
1. Assign a band score (1-9) based strictly on {criteria} criteria.
2. Provide concise and non-redundant comments explaining the score. 
3. Highlight specific strengths and weaknesses in the essay, referencing the tool outputs where relevant.
4. Suggest actionable improvements for the writer to raise their score.
5. Responses in Australian English.


"""
)


IELTS_GAP_ANALYSIS_PROMPT = PromptTemplate(
    input_variables=[
        "overall_band",
        "target_band",
        "weak_bands",
        "weak_comments",
        "target_band_descriptor_data",
        "criteria_data"
    ],
     template=
"""
You are a senior IELTS teacher.
Follow the instructions prior generate an answer:

1. Evaluate the examiner comments below.
2. Compare the actual result and comments to the expectations on the target band descriptors and assessment guidelines.
3. Create a professional response to the student receiving the feedback.

4. Consider the following information to write the response:

    The student's current overall band is {overall_band}, target is {target_band}.
    Weak areas: {weak_bands}

    criteria evaluation:
    {weak_comments}

    Target band descriptors:
    {target_band_descriptor_data}

    Assessment criteria guidelines:
    {criteria_data}

5. Generate an actionable, criterion-specific improvement plan that helps the student reach Band {target_band}.
6. Provide 1–2 concise and focused suggestions per weak criterion, written in clear, teacher-style feedback.
7. Keep the response concise.
8. DO NOT mention the examiner or a mention about this prompt.  
9. Do not repeat what is already in the comments. 
10. Keep suggestion concise, practical, professional and using Australian English.
11. Ensure that the output is in markdown format with criteria names and titles in **bold** 
12. Ensure the comments are formatted in markdown as below:

**Overview:**
**Improvement Plan:**

Example of a response:

Your current writing score is 6.75, and your target is Band 7. The main area for improvement is **Coherence & Cohesion**, currently at Band 6. 

The feedback highlights a critical issue: the essay did not address the question prompt. This resulted in a lack of logical organisation, progression, and appropriate use of cohesive devices. The examiner correctly identifies that the entire essay is considered an error due to its irrelevance.

**Improvement Plan:**

To improve your **Coherence & Cohesion** score (Band 6 -> Band 7), focus on these areas:

*   **Understand the Question:** Before you start writing, carefully analyse the question. Identify the specific topic and what the question asks you to do (e.g., discuss, compare, explain). Make sure your essay directly answers the prompt.
*   **Plan and Structure:** Create a clear outline before you write. This should include an introduction, body paragraphs with topic sentences that directly relate to the question, and a conclusion. Each paragraph should focus on a single main idea.
*   **Use Cohesive Devices Effectively:** Practice using a variety of cohesive devices (linking words, pronouns, etc.) to connect your ideas logically. Ensure you use them accurately and appropriately to show the relationship between your ideas.

"""   
)