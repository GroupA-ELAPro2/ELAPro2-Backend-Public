import json
from agent_files.helper_functions import map_agent_to_criteria, map_essay_type
from importlib import resources

class KeyAssessmentCriteriaTool:
    def __init__(self, academic_json_path, general_json_path):
        with resources.open_text('app.tools',academic_json_path, encoding='utf-8') as f:
            self.academic_data = json.load(f)
        with resources.open_text('app.tools',general_json_path, encoding='utf-8') as f:
            self.general_data = json.load(f)

    def _get_data_by_exam_type(self, exam_type: str):
        """Return the correct dataset based on exam type string."""
        if exam_type == "Academic":
            return self.academic_data
        elif exam_type == "General Training":
            return self.general_data
        else:
            raise ValueError(f"Invalid exam_type: {exam_type}. Must be 'Academic' or 'General Training'.")
    
    def _clean_dict(self, data: dict) -> dict:
        """
        Recursively remove keys with empty lists, empty strings, or None values.
        """
        if not isinstance(data, dict):
            return data
        return {
            k: self._clean_dict(v)
            for k, v in data.items()
            if v not in (None, "", [])  # remove None, empty string, empty list
        }
                
    def _format_output_all_criteria(self, exam_type, task_type_name, criteria_data, penalties) -> str:
        """
        Wraps key assessment criteria data in a standard explanatory text.
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
     
    def _format_output_criterion(self, exam_type, task_type_name, criteria_name, criteria_data) -> str:
        """
        Wraps key assessment criteria data in a standard explanatory text.
        """

         # Format common assessment
        common_assessment = criteria_data.get("common_assessment", [])
        common_assessment_formatted = "" if not common_assessment else "\n- " + "\n- ".join(common_assessment)

        # Format specific assessment
        specific_assessment = criteria_data.get("specific_assessment", [])
        specific_assessment_formatted = "" if not specific_assessment else "\n- " + "\n- ".join(specific_assessment)


        return f"""
        For **{exam_type} – {task_type_name}** and **{criteria_name}** Criterion, the essay will be assessed on:          
        
        Core IELTS standards (apply to all types of tasks):
        {common_assessment_formatted}

        {"" if not specific_assessment else f"Requirements unique to the {exam_type} Writing test:"}

        {specific_assessment_formatted}
                """
    
    def get_hierarchy_description(self) -> str:
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
        """
        Returns all key assessment criteria for a given essay type,
        with the common formatted explanatory text.
        """
        exam_type, task_type_name, _ = map_essay_type(essay_type)
        data = self._get_data_by_exam_type(exam_type)
        penalties = self.get_penalties_by_exam_type(exam_type)

        try:
            criteria_data = data[exam_type][task_type_name]            
            
            return self._format_output_all_criteria(exam_type, task_type_name, criteria_data, penalties)
        except KeyError:
            return {"error": f"Data not found for {exam_type} - {task_type_name}"}
        
    def get_penalties_by_exam_type(self, exam_type: str):
        """Return the penalties based on exam type string."""
        data = self._get_data_by_exam_type(exam_type)
        penalties = data[exam_type]["penalties"]
        
        return json.dumps(penalties, indent=2, ensure_ascii=False)
        
    def get_task_description(self, essay_type: int) -> str:
        """
        Returns task description for a given essay type.
        Used for scoring reasoning.
        """
        exam_type, task_type_name, _ = map_essay_type(essay_type)
        data = self._get_data_by_exam_type(exam_type)        

        return data[exam_type][task_type_name]["description"]
    
    def get_task_word_requirement(self, essay_type: int) -> int:
        """
        Returns the number of words required for a given essay type.
        """
        exam_type, task_type_name, _ = map_essay_type(essay_type)
        data = self._get_data_by_exam_type(exam_type)

        return data[exam_type][task_type_name]["word_requirement"]
        
    def get_assessment_by_criteria(self, essay_type: int, agent: str) -> str:
        """
        Returns all the criteria to be assessed for a given agent and essay type.
        Used for scoring reasoning.
        """       

        exam_type, task_type_name, task_number = map_essay_type(essay_type)
        data = self._get_data_by_exam_type(exam_type)
        criteria = map_agent_to_criteria(agent, task_number)

        try:
            criteria_data = data[exam_type][task_type_name][criteria]

            return self._format_output_criterion(exam_type, task_type_name, criteria, criteria_data)
        except KeyError:
            return "Criterion assessment not found for given parameters."

    