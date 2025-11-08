import json
from agent_files.helper_functions import map_agent_to_criteria, map_essay_type
from importlib import resources


class KeyAssessmentCriteriaTool:
    """Tool for retrieving IELTS key assessment criteria from JSON data files.

    Manages assessment criteria for both Academic and General Training writing tasks,
    providing methods to retrieve criteria by essay type, task type, and specific
    assessment criteria. Also handles penalties and word requirements.

    Attributes:
        academic_data (dict): Loaded Academic writing assessment criteria.
        general_data (dict): Loaded General Training writing assessment criteria.
    """

    def __init__(self, academic_json_path, general_json_path):
        """Initialize the tool with JSON data files.

        Args:
            academic_json_path (str): Path to Academic assessment criteria JSON file.
            general_json_path (str): Path to General Training assessment criteria JSON file.
        """
        with resources.open_text(
            "app.tools", academic_json_path, encoding="utf-8"
        ) as f:
            self.academic_data = json.load(f)
        with resources.open_text("app.tools", general_json_path, encoding="utf-8") as f:
            self.general_data = json.load(f)

    def _get_data_by_exam_type(self, exam_type: str):
        """Return the correct dataset based on exam type string.

        Args:
            exam_type (str): "Academic" or "General Training".

        Returns:
            dict: Assessment criteria data for the specified exam type.

        Raises:
            ValueError: If exam_type is not "Academic" or "General Training".
        """
        if exam_type == "Academic":
            return self.academic_data
        elif exam_type == "General Training":
            return self.general_data
        else:
            raise ValueError(
                f"Invalid exam_type: {exam_type}. Must be 'Academic' or 'General Training'."
            )

    def _clean_dict(self, data: dict) -> dict:
        """Recursively remove keys with empty values from dictionary.

        Args:
            data (dict): Dictionary to clean.

        Returns:
            dict: Cleaned dictionary with empty lists, strings, and None values removed.
        """
        if not isinstance(data, dict):
            return data
        return {
            k: self._clean_dict(v)
            for k, v in data.items()
            if v not in (None, "", [])  # remove None, empty string, empty list
        }

    def _format_output_all_criteria(
        self, exam_type, task_type_name, criteria_data, penalties
    ) -> str:
        """Format all assessment criteria with explanatory context.

        Args:
            exam_type (str): "Academic" or "General Training".
            task_type_name (str): Task type name (e.g., "Task 1", "Task 2").
            criteria_data (dict): Assessment criteria data.
            penalties (str): Formatted penalty information.

        Returns:
            str: Formatted assessment criteria output with explanatory text.
        """

        cleaned_criteria = self._clean_dict(criteria_data)

        return f"""
    The IELTS essay must be assessed according to the following criteria:

    - "common_assessment": Core IELTS writing standards
    - "specific_assessment": Requirements unique to the {exam_type} Writing test

    For **{exam_type} – {task_type_name}**, the essay will be assessed on:

    {json.dumps(cleaned_criteria, indent=2, ensure_ascii=False)}

    **Penalties apply in these cases:**
    {penalties}
    """

    def _format_output_criterion(self, criteria_name, criteria_data) -> str:
        """Format a specific criterion's assessment data with explanatory context.

        Args:
            exam_type (str): "Academic" or "General Training".
            task_type_name (str): Task type name (e.g., "Task 1", "Task 2").
            criteria_name (str): Name of the specific criterion.
            criteria_data (dict): Assessment data for the criterion.

        Returns:
            str: Formatted criterion assessment output with explanatory text.
        """

        # Format common assessment
        common_assessment = criteria_data.get("common_assessment", [])
        common_assessment_formatted = (
            "" if not common_assessment else "\n- " + "\n- ".join(common_assessment)
        )

        # Format specific assessment
        specific_assessment = criteria_data.get("specific_assessment", [])
        specific_assessment_formatted = (
            "" if not specific_assessment else "\n- " + "\n- ".join(specific_assessment)
        )
        return f"""

        When evaluating **{criteria_name}** you must consider ONLY:         
                
        {common_assessment_formatted}

        {"" if not specific_assessment else specific_assessment_formatted}
        
                """

    def get_hierarchy_description(self) -> str:
        """Get the JSON data structure hierarchy description.

        Returns:
            str: Description of the assessment criteria data hierarchy.
        """
        return """The information below is extracted from IELTS Writing Key Assessment Criteria document.
                    The hierarchy of the original JSON file is:
                    
                    Exam Type
                    --> Task Type
                        --> word_requirement
                        --> description
                        --> Criteria
                            --> common_assessment
                            --> specific_assessment
                    --> penalties
                    --> weighting                                    
                    """

    def get_all_assessment_criteria(self, essay_type: int) -> str:
        """Retrieve all key assessment criteria for an essay type.

        Args:
            essay_type (int): Essay type identifier (1-4).

        Returns:
            str: Formatted assessment criteria for all criteria, or error message.
        """
        exam_type, task_type_name, _ = map_essay_type(essay_type)
        data = self._get_data_by_exam_type(exam_type)
        penalties = self.get_penalties_by_exam_type(exam_type)

        try:
            criteria_data = data[exam_type][task_type_name]

            return self._format_output_all_criteria(
                exam_type, task_type_name, criteria_data, penalties
            )
        except KeyError:
            return {"error": f"Data not found for {exam_type} - {task_type_name}"}

    def get_penalties_by_exam_type(self, exam_type: str):
        """Retrieve penalty information for an exam type.

        Args:
            exam_type (str): "Academic" or "General Training".

        Returns:
            str: Formatted JSON string of penalty information.
        """
        data = self._get_data_by_exam_type(exam_type)
        penalties = data[exam_type]["penalties"]

        return json.dumps(penalties, indent=2, ensure_ascii=False)

    def get_task_description(self, essay_type: int) -> str:
        """Retrieve task description for an essay type.

        Used during scoring to understand task requirements and expectations.

        Args:
            essay_type (int): Essay type identifier (1-4).

        Returns:
            str: Task description text.
        """
        exam_type, task_type_name, _ = map_essay_type(essay_type)
        data = self._get_data_by_exam_type(exam_type)

        return data[exam_type][task_type_name]["description"]

    def get_task_word_requirement(self, essay_type: int) -> int:
        """Retrieve minimum word count requirement for an essay type.

        Args:
            essay_type (int): Essay type identifier (1-4).

        Returns:
            int: Minimum number of words required.
        """
        exam_type, task_type_name, _ = map_essay_type(essay_type)
        data = self._get_data_by_exam_type(exam_type)

        return data[exam_type][task_type_name]["word_requirement"]

    def get_assessment_by_criteria(self, essay_type: int, agent: str) -> str:
        """Retrieve assessment criteria for a specific criterion and essay type.

        Used during scoring to understand expectations for a particular
        assessment criterion (e.g., grammar, coherence, lexical resource).

        Args:
            essay_type (int): Essay type identifier (1-4).
            agent (str): Agent name corresponding to assessment criteria.

        Returns:
            str: Formatted assessment criteria for the criterion, or error message.
        """
        exam_type, task_type_name, task_number = map_essay_type(essay_type)
        data = self._get_data_by_exam_type(exam_type)
        criteria = map_agent_to_criteria(agent, task_number)

        try:
            criteria_data = data[exam_type][task_type_name][criteria]

            return self._format_output_criterion(criteria, criteria_data)
        except KeyError:
            return "Criterion assessment not found for given parameters."

    def get_word_count_penalty(self, essay_type: int, essay: str) -> str:
        """
        Calculate and return the word count penalty message for an essay based on its type and length.

        This function evaluates whether an essay meets the minimum word count requirements
        and determines the appropriate penalty to apply to the Task Achievement Band score
        if the word count is insufficient.

        Args:
            essay_type (int): The type of essay being evaluated.
                - Types 1 and 3: Require minimum 150 words
                - Types 2 and 4: Require minimum 250 words
            essay (str): The essay text to evaluate. Word count is calculated by splitting
                on whitespace.

        Returns:
            str: A message describing the word count requirement, actual word count, and
                the penalty to apply (if any). The message format is:
                "The minimum words required for this task is: {requirement}.
                 This essay actually has {count} words: {penalty}"

        Penalty Structure:
            For essay types 1 and 3 (150-word minimum):
                - 140-149 words: Reduce Task Achievement by 0.5 bands
                - 100-139 words: Reduce Task Achievement by 1+ bands
                - < 100 words: Cap Task Achievement at Band 5 maximum
                - >= 150 words: No penalty

            For essay types 2 and 4 (250-word minimum):
                - 230-249 words: Reduce Task Achievement by 0.5 bands
                - 200-229 words: Reduce Task Achievement by 1+ bands
                - < 200 words: Cap Task Achievement at Band 5 maximum
                - >= 250 words: No penalty

        Note:
            The function relies on `get_task_word_requirement()` to retrieve the minimum
            word count for each essay type.
        """

        word_requirement = self.get_task_word_requirement(essay_type)
        words = essay.split()
        actual_word_count = len(words)

        general_response = f"The minimum words required for this task is: {word_requirement}. This essay actually has {actual_word_count} words: "
        slight_penalty = "REDUCE the Task Achievement Band score by 0.5"
        stronger_penalty = "REDUCE the Task Achievement Band score by 1 band or more depending on Task Achievement impact."
        critical_penalty = "The Task Achievement Band score should *not exceed Band score 5* for Task Achievement"
        no_penalty = "no word count penalty applies."

        if essay_type in (1, 3):

            if actual_word_count < 150 and actual_word_count >= 140:

                return general_response + slight_penalty

            elif actual_word_count < 140:

                return general_response + stronger_penalty

            elif actual_word_count < 100:

                return general_response + critical_penalty

            else:

                return general_response + no_penalty

        if essay_type in (2, 4):

            if actual_word_count < 250 and actual_word_count >= 230:

                return general_response + slight_penalty

            elif actual_word_count < 230:

                return general_response + stronger_penalty

            elif actual_word_count < 200:

                return general_response + critical_penalty

            else:

                return general_response + no_penalty
