from agent_files.image_description_agent import (
    image_evaluation,
    image_agent,
)
from agent_files.agent_states import InputState, ImageDescriptionOutput
import unittest
import os


class TestImageDesc(unittest.TestCase):

    # Setup tests with basic input data
    def setUp(self):
        os.environ["LANGSMITH_TRACING_V2"] = "false"
        self.input_data = {
            "essay": "The answer to the meaning of life is 42. But I'm no expert on this.",
            "question": "What is the meaning of life?",
            "track_id": "test track",
            "essay_type": 2,
            "target_band": 5,
            "image_url": "https://engnovatewebsitestorage.blob.core.windows.net/ielts-writing-task-1-images/a0977f9b9c675777",
        }
        return super().setUp()

    # Test for valid URL
    def test_url_exists(self):
        input = InputState(**self.input_data)
        self.assertTrue(input.is_image_url())

    def test_invalid_url(self):
        input = InputState(**self.input_data)
        input.image_url = "email@email.com"
        self.assertFalse(input.is_image_url())
        input.image_url = "https://www.somefakeurl.xxx"
        self.assertFalse(input.is_image_url())

    def test_image_evaluation(self):
        self.input_data["image_url"] = (
            "https://www.oxfordonlineenglish.com/wp-content/uploads/2020/03/IELTS-Writing-Task-1-Academic-for-quiz-graphic-e1584609098154.jpg"
        )
        description = image_evaluation(InputState(**self.input_data))
        print(description)
        self.assertIsInstance(
            description, ImageDescriptionOutput, f"Returned: {description}"
        )

    def test_not_image(self):
        input = InputState(**self.input_data)
        input.image_url = "https://www.google.com/"
        self.assertFalse(input.is_image_url())

    def test_is_image(self):
        input = InputState(**self.input_data)
        self.assertTrue(input.is_image_url())

    def test_not_image_return_value(self):
        self.input_data["image_url"] = "https://www.google.com/"
        self.input_data["image_description"] = "Google Homepage"
        self.assertEqual(
            image_evaluation(InputState(**self.input_data)),
            ImageDescriptionOutput(image_description="Google Homepage"),
        )

    def test_no_url_function(self):
        self.input_data["image_url"] = None
        self.assertEqual(
            image_evaluation(InputState(**self.input_data)),
            ImageDescriptionOutput(image_description=None),
        )

    def test_no_url_agent(self):
        self.input_data["image_url"] = None
        self.assertEqual(
            image_agent(InputState(**self.input_data)), {"image_description": None}
        )

    def test_return_existing_desc(self):
        self.input_data["image_description"] = "This is a mock image descritption"
        description = image_agent(InputState(**self.input_data))
        self.assertEqual(
            description, {"image_description": "This is a mock image descritption"}
        )

    def test_agent_valid(self):
        description = image_agent(InputState(**self.input_data))
        self.assertIsInstance(description, dict, f"Returned: {description}")

    def test_null_description(self):
        self.input_data["image_description"] = "null"
        description = image_agent(InputState(**self.input_data))
        self.assertNotEqual(description, {"image_description": "null"})
