import json
from agent_files.helper_functions import map_agent_to_criteria, map_essay_type
from importlib import resources

class BandDescriptorTool:
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
        
    def _format_descriptor_output(self, exam_type, task_type_name, descriptor_name, descriptor_data) -> str:
        """
        Wraps descriptor data in a standard explanatory text.
        """
        return f"""             
                An essay must fully fit the positive features of the descriptor at a particular level. 
                
                - "common_descriptor": Describes the overall positive qualities expected at this band.  
                - "specific_descriptor": these are specifics requirements for {exam_type} writing test; missing these may lower the rating.  
                - "critical_negative_features": indicates negative features that will limit a rating.                

                Here are the band score descriptors for {exam_type} - {task_type_name}:                

                {descriptor_name}: {json.dumps(descriptor_data, indent=2)}
                """
    
    def get_hierarchy_description(self) -> str:
        return """The information below is extracted from IELTS Writing Tasks Band Descriptors.
                    The hierarchy of the original JSON file is:

                    Exam Type
                    --> Task Type
                        --> Criteria
                            --> Band Scores (1 to 9)
                                --> Descriptors
                                    --> common_descriptor
                                    --> specific_descriptor
                                    --> critical_negative_features
                    """

    def get_all_descriptors(self, essay_type: int) -> str:
        """
        Returns all descriptors (all criteria, all bands) for a given essay type,
        with the common formatted explanatory text.
        """
        exam_type, task_type_name, _ = map_essay_type(essay_type)
        data = self._get_data_by_exam_type(exam_type)

        try:
            descriptor_data = data[exam_type][task_type_name]
            return self._format_descriptor_output(exam_type, task_type_name, "All criteria", descriptor_data)
        except KeyError:
            return {"error": f"Descriptors not found for {exam_type} - {task_type_name}"}

    def get_all_band_descriptors_by_criteria(self, essay_type: int, agent: str) -> str:
        """
        Returns all band descriptors for a given agent and essay type.
        Used for scoring reasoning.
        """
        exam_type, task_type_name, task_number = map_essay_type(essay_type)
        data = self._get_data_by_exam_type(exam_type)
        criteria = map_agent_to_criteria(agent, task_number)

        try:
            descriptor_data = data[exam_type][task_type_name][criteria]
            return self._format_descriptor_output(exam_type, task_type_name, criteria, descriptor_data)
        except KeyError:
            return "Descriptor not found for given parameters."

    def get_target_band_descriptors_by_criteria(self, essay_type: int, agent: str, band: int) -> str:
        """
        Returns descriptors for a specific criteria and target band.
        Used to check alignment of an essay criteria with a given band.
        """
        exam_type, task_type_name, task_number = map_essay_type(essay_type)
        data = self._get_data_by_exam_type(exam_type)
        criteria = map_agent_to_criteria(agent, task_number)

        try:
            descriptor_data = data[exam_type][task_type_name][criteria][str(band)]
            return self._format_descriptor_output(exam_type, task_type_name, f"{criteria} - Band {band}", descriptor_data)
        except KeyError:
            return "Descriptor not found for given parameters."
        
    
    def get_all_descriptors_by_band(self, essay_type: int, band: int) -> dict:
        """
        Returns all criteria descriptors for a specific target band.
        Used to check alignment of an essay with a given band.
        """
        exam_type, task_type_name, _ = map_essay_type(essay_type)
        data = self._get_data_by_exam_type(exam_type)

        try:
            task_criteria = data[exam_type][task_type_name]
            band_descriptors = {}
            for criterion, bands in task_criteria.items():
                band_descriptors[criterion] = bands.get(str(band), "Band not found for this criterion.")
            return self._format_descriptor_output(exam_type, task_type_name, f"All criteria - Band {band}", band_descriptors)
        except KeyError:
            return "Descriptor not found for given parameters."