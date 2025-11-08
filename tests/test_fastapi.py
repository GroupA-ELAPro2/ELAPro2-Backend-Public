from app.main import app
from app import auth
from fastapi.testclient import TestClient
import unittest
import pydantic
import unittest.mock
from fastapi import HTTPException
import os


class TestFastAPI(unittest.TestCase):

    # Setup tests with basic input data
    def setUp(self):
        os.environ["LANGSMITH_TRACING_V2"] = "false"
        self.client = TestClient(app)
        self.essay_data = {
            "essay": "The answer to the meaning of life is 42. But I'm no expert on this.",
            "question": "What is the meaning of life?",
            "track_id": "test track",
            "essay_type": 2,
            "target_band": 5,
            "image_url": "test_url",
        }
        return super().setUp()

    # Test a valid API response sends a 200 response code and the response format is a dict
    def test_post(self):
        response = self.client.post(
            "/process_essay/",
            json=self.essay_data,
            headers={"X-API-Key": "key123-dev-456"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), dict)

    # Test invalid data received sends a 422 response code
    def test_invalid(self):
        self.essay_data["target_band"] = 0  # Send invalid data
        response = self.client.post(
            "/process_essay/",
            json=self.essay_data,
            headers={"X-API-Key": "key123-dev-456"},
        )
        self.assertEqual(response.status_code, 422)

    # Ensure that the same track_id sent is received in the response
    def test_track_id(self):
        self.essay_data["track_id"] = "456@same_track_id@456"
        response = self.client.post(
            "/process_essay/",
            json=self.essay_data,
            headers={"X-API-Key": "key123-dev-456"},
        )
        response_trackid = response.json()["data"]
        self.assertEqual(response_trackid["track_id"], "456@same_track_id@456")

    # Ensure exceptions raised from the evaluate_essay function return status code 50#0
    def test_process_essay_exception(self):
        # patch the process_essay function with a mock exception to test response code
        with unittest.mock.patch(
            "app.main.evaluate_essay",
            side_effect=pydantic.ValidationError("Mock Validation Error", []),
        ):
            response = self.client.post(
                "/process_essay/",
                json=self.essay_data,
                headers={"X-API-Key": "key123-dev-456"},
            )
            self.assertEqual(response.status_code, 500)

    # Test valid api key
    def test_api_key_exists(self):
        exists = auth.check_api_key("invalid_api")
        self.assertEqual(exists, False)
        exists = auth.check_api_key("key123-dev-456")
        self.assertEqual(exists, True)

    # Test get user
    def test_api_user(self):
        with self.assertRaises(HTTPException) as HTTPe:
            auth.get_user_from_api_key("invalid_api")
        self.assertEqual(HTTPe.exception.status_code, 401)
        user = auth.get_user_from_api_key("key123-dev-456")
        self.assertEqual(user, "dev_testing_key_user")

    # Test get user from header
    def test_api_header_user(self):
        with self.assertRaises(HTTPException) as HTTPe:
            auth.get_user_from_api_key("invalid_api")
        self.assertEqual(HTTPe.exception.status_code, 401)
        user = auth.get_user_from_api_key("key123-dev-456")
        self.assertEqual(user, "dev_testing_key_user")

    # Test process essay with no api key
    def test_process_no_api(self):
        response = self.client.post("/process_essay/", json=self.essay_data)
        self.assertEqual(response.status_code, 403)

    # Test process essay with invalid apikey
    def test_process_invalid_api(self):
        response = self.client.post(
            "/process_essay/", json=self.essay_data, headers={"X-API-Key": "invalid"}
        )
        self.assertEqual(response.status_code, 401)

    # Test process essay as get returns html
    def test_process_get(self):
        response = self.client.get("/process_essay")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers.get("Content-Type"), "text/html; charset=utf-8"
        )

    # test get request returns html
    def test_get(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers.get("Content-Type"), "text/html; charset=utf-8"
        )

    # test keyfile not found
    def test_no_keyfile(self):
        with self.assertRaises(FileNotFoundError):
            auth.get_user_from_api_key("key123-dev-456", "somefile.csv")
        with self.assertRaises(FileNotFoundError):
            auth.check_api_key("key123-dev-456", "somefile.csv")
