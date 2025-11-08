import json, re
from agent_files.helper_functions import map_agent_to_criteria, map_essay_type
from importlib import resources


class BandDescriptorTool:
    """Tool for retrieving IELTS band descriptors from JSON data files.

    Manages band descriptors for both Academic and General Training writing tasks,
    providing methods to retrieve descriptors by criteria, band level, and essay type.

    Attributes:
        academic_data (dict): Loaded Academic writing band descriptors.
        general_data (dict): Loaded General Training writing band descriptors.
    """

    def __init__(self, academic_json_path, general_json_path):
        """Initialize the tool with JSON data files.

        Args:
            academic_json_path (str): Path to Academic band descriptors JSON file.
            general_json_path (str): Path to General Training band descriptors JSON file.
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
            dict: Band descriptor data for the specified exam type.

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

    def _format_descriptor_output_all(
        self, exam_type, task_type_name, descriptor_name, descriptor_data
    ) -> str:
        """Format descriptor data with explanatory context.

        Args:
            exam_type (str): "Academic" or "General Training".
            task_type_name (str): Task type name (e.g., "Task 1", "Task 2").
            descriptor_name (str): Name of the descriptor or criteria.
            descriptor_data (dict): Descriptor data to format.

        Returns:
            str: Formatted descriptor output with explanatory text.
        """
        return f"""
                An essay must fully fit the positive features of the descriptor at a particular level.

                - "common_descriptor": Describes the overall positive qualities expected at this band.
                - "specific_descriptor": these are specifics requirements for {exam_type} writing test; missing these may lower the rating.
                - "critical_negative_features": indicates negative features that will limit a rating.

                Here are the band score descriptors for {exam_type} - {task_type_name}:

                {descriptor_name}: {json.dumps(descriptor_data, indent=2)}
                """

    def _format_descriptor_output(self, descriptor_name, descriptor_data) -> str:
        """Format descriptor data into readable band-score rules.

        Args:
            descriptor_name (str): Name of the descriptor or criteria.
            descriptor_data (dict): Descriptor data to format.

        Returns:
            str: Formatted descriptor output as explanatory band score rules.
        """
        formatted_output = [
            f"Below are the **band scores descriptors** for '{descriptor_name}'"
            f"\nTo determine the correct '{descriptor_name}' band score for the essay, use the rules below to decide the score",
            "The bold text highlights critical features that strongly determine whether the essay fits that band.",
            "",
        ]
        # Iterate over bands in ascending order
        for band, details in sorted(descriptor_data.items(), key=lambda x: int(x[0])):
            # Combine both descriptors
            combined_text = " ".join(
                filter(
                    None,
                    [
                        details.get("common_descriptor"),
                        details.get("specific_descriptor"),
                    ],
                )
            )

            # Bold critical negative features inside the text
            for feature in details.get("critical_negative_features", []):
                pattern = re.escape(feature)
                combined_text = re.sub(pattern, f"**{feature}**", combined_text)

            # Split sentences into bullet points
            sentences = [
                s.strip() for s in re.split(r"(?<=[.])\s+", combined_text) if s
            ]

            # Build the section for this band
            formatted_output.append(f"\nScore = {band} when:")
            for sentence in sentences:
                formatted_output.append(f"- {sentence}")

        return "\n".join(formatted_output)

    def get_hierarchy_description(self) -> str:
        """Get the JSON data structure hierarchy description.

        Returns:
            str: Description of the band descriptor data hierarchy.
        """
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
        """Retrieve all descriptors (all criteria, all bands) for an essay type.

        Args:
            essay_type (int): Essay type identifier (1-4).

        Returns:
            str: Formatted descriptor data for all criteria and bands, or error message.
        """
        exam_type, task_type_name, _ = map_essay_type(essay_type)
        data = self._get_data_by_exam_type(exam_type)

        try:
            descriptor_data = data[exam_type][task_type_name]
            return self._format_descriptor_output(
                exam_type, task_type_name, "All criteria", descriptor_data
            )
        except KeyError:
            return {
                "error": f"Descriptors not found for {exam_type} - {task_type_name}"
            }

    def get_all_band_descriptors_by_criteria(self, essay_type: int, agent: str) -> str:
        """Retrieve all band descriptors for a specific criteria and essay type.

        Used during scoring to understand expectations across all band levels
        for a particular assessment criterion.

        Args:
            essay_type (int): Essay type identifier (1-4).
            agent (str): Agent name corresponding to assessment criteria.

        Returns:
            str: Formatted band descriptors for the criteria, or error message.
        """
        exam_type, task_type_name, task_number = map_essay_type(essay_type)
        data = self._get_data_by_exam_type(exam_type)
        criteria = map_agent_to_criteria(agent, task_number)

        try:
            descriptor_data = data[exam_type][task_type_name][criteria]
            return self._format_descriptor_output(criteria, descriptor_data)
        except KeyError:
            return "Descriptor not found for given parameters."

    def get_target_band_descriptors_by_criteria(
        self, essay_type: int, agent: str, band: int
    ) -> str:
        """Retrieve descriptors for a specific criteria at a target band level.

        Used to check if an essay meets the requirements for a specific band
        level in a particular assessment criterion.

        Args:
            essay_type (int): Essay type identifier (1-4).
            agent (str): Agent name corresponding to assessment criteria.
            band (int): Target band score (1-9).

        Returns:
            str: Formatted band descriptor for the criteria and band, or error message.
        """
        exam_type, task_type_name, task_number = map_essay_type(essay_type)
        data = self._get_data_by_exam_type(exam_type)
        criteria = map_agent_to_criteria(agent, task_number)

        try:
            descriptor_data = data[exam_type][task_type_name][criteria][str(band)]
            return self._format_descriptor_output_all(
                exam_type, task_type_name, f"{criteria} - Band {band}", descriptor_data
            )
        except KeyError:
            return "Descriptor not found for given parameters."

    def get_all_descriptors_by_band(self, essay_type: int, band: int) -> dict:
        """Retrieve descriptors for all criteria at a specific band level.

        Used to check overall essay alignment with a target band across
        all assessment criteria.

        Args:
            essay_type (int): Essay type identifier (1-4).
            band (int): Target band score (1-9).

        Returns:
            dict: Formatted band descriptors for all criteria at the band, or error message.
        """
        exam_type, task_type_name, _ = map_essay_type(essay_type)
        data = self._get_data_by_exam_type(exam_type)

        try:
            task_criteria = data[exam_type][task_type_name]
            band_descriptors = {}
            for criterion, bands in task_criteria.items():
                band_descriptors[criterion] = bands.get(
                    str(band), "Band not found for this criterion."
                )
            return self._format_descriptor_output(
                exam_type,
                task_type_name,
                f"All criteria - Band {band}",
                band_descriptors,
            )
        except KeyError:
            return "Descriptor not found for given parameters."
