import unittest
from app.tools.tools import BandDescriptorTool, KeyAssessmentCriteriaTool
import os


class testTools(unittest.TestCase):

    # Setup tests with basic input data
    def setUp(self):
        os.environ["LANGSMITH_TRACING_V2"] = "false"
        self.bandtool = BandDescriptorTool(
            "ielts_descriptors_academic.json", "ielts_descriptors_general.json"
        )
        self.criteria_tool = KeyAssessmentCriteriaTool(
            "ielts_assessment_criteria_academic.json",
            "ielts_assessment_criteria_general.json",
        )
        return super().setUp()

    # Test band descriptor tool
    def test_task_desc_tool(self):
        output = self.criteria_tool.get_task_description(1)
        self.assertEqual(
            output,
            "Letter writing task with defined context and purpose. Each task sets out the context and purpose of the letter and the functions the candidate should cover.",
        )
        output = self.criteria_tool.get_task_description(2)
        self.assertEqual(
            output,
            "Formulate and develop a position in relation to a given prompt in the form of a question or statement. Ideas should be supported by evidence, and examples may be drawn from candidate's own experience.",
        )
        output = self.criteria_tool.get_task_description(3)
        self.assertEqual(
            output,
            "Information-transfer task relating to factual content of a diagram, graph, table, chart, map or other visual input",
        )
        output = self.criteria_tool.get_task_description(4)
        self.assertEqual(
            output,
            "Formulate and develop a position in relation to a given prompt in the form of a question or statement. Ideas should be supported by evidence, and examples may be drawn from candidate's own experience.",
        )

    # Test band descriptor tool with invalid input
    def test_invalid_task_desc_tool(self):
        with self.assertRaises(ValueError):
            output = self.criteria_tool.get_task_description(0)
        with self.assertRaises(ValueError):
            output = self.criteria_tool.get_task_description(5)
        with self.assertRaises(ValueError):
            output = self.criteria_tool.get_task_description("string")

    # Test assessment criteria tool
    def test_task_assess_tool(self):
        output = self.criteria_tool.get_assessment_by_criteria(1, "grammar_agent")
        self.assertIsInstance(output, str)
        output = self.criteria_tool.get_assessment_by_criteria(2, "LEXICAL_agent")
        self.assertIsInstance(output, str)
        output = self.criteria_tool.get_assessment_by_criteria(3, "task_AGEnt")
        self.assertIsInstance(output, str)
        output = self.criteria_tool.get_assessment_by_criteria(4, "Coherence_Agent")
        self.assertIsInstance(output, str)

    # Test assessment criteria tool invalid
    def test_task_assess_invalid(self):
        with self.assertRaises(ValueError):
            self.criteria_tool.get_assessment_by_criteria(0, "grammar_agent")
        with self.assertRaises(ValueError):
            self.criteria_tool.get_assessment_by_criteria(5, "task_agent")
        with self.assertRaises(ValueError):
            self.criteria_tool.get_assessment_by_criteria(1, "task")
        with self.assertRaises(TypeError):
            self.criteria_tool.get_assessment_by_criteria(essay_type=1)
        with self.assertRaises(TypeError):
            self.criteria_tool.get_assessment_by_criteria(agent="grammar_agent")
        with self.assertRaises(TypeError):
            self.criteria_tool.get_assessment_by_criteria()

    # Test getting band descriptors by criteria
    def test_band_criteria(self):
        output = self.bandtool.get_all_band_descriptors_by_criteria(1, "grammar_agent")
        self.assertIsInstance(output, str)
        output = self.bandtool.get_all_band_descriptors_by_criteria(2, "LEXICAL_agent")
        self.assertIsInstance(output, str)
        output = self.bandtool.get_all_band_descriptors_by_criteria(3, "task_AGEnt")
        self.assertIsInstance(output, str)
        output = self.bandtool.get_all_band_descriptors_by_criteria(
            4, "Coherence_Agent"
        )
        self.assertIsInstance(output, str)

    # Test assessment criteria tool invalid
    def test_band_criteria_invalid(self):
        with self.assertRaises(ValueError):
            self.bandtool.get_all_band_descriptors_by_criteria(0, "grammar_agent")
        with self.assertRaises(ValueError):
            self.bandtool.get_all_band_descriptors_by_criteria(5, "task_agent")
        with self.assertRaises(ValueError):
            self.bandtool.get_all_band_descriptors_by_criteria(1, "task")
        with self.assertRaises(TypeError):
            self.bandtool.get_all_band_descriptors_by_criteria(essay_type=1)
        with self.assertRaises(TypeError):
            self.bandtool.get_all_band_descriptors_by_criteria(agent="grammar_agent")
        with self.assertRaises(TypeError):
            self.bandtool.get_all_band_descriptors_by_criteria()
