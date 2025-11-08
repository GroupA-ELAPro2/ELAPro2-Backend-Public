from app.main import app
from fastapi.testclient import TestClient
import unittest
import pydantic
import json
from unittest.mock import Mock


class TestFastAPI(unittest.TestCase):
    
    #Setup tests with basic input data
    def setUp(self):
        self.client = TestClient(app)
        self.essay_data = {"essay":"The answer to the meaning of life is 42. But I'm no expert on this.","question":"What is the meaning of life?","track_id":"test track","essay_type":2,"target_band":5,"image_url":"test_url"}
        return super().setUp()
    
    #Test a valid API response sends a 200 response code and the response format is a dict
    def test_post(self):
        response = self.client.post("/process_essay/",json=self.essay_data, headers={'X-API-Key': 'd3626f7c-5112-43a8-86a7-3ca100964772'})
        self.assertEqual(response.status_code,200)
        self.assertIsInstance(response.json(),dict)
    
    #Test invalid data received sends a 422 response code
    def test_invalid(self):
        self.essay_data["target_band"] = 0 #Send invalid data
        response = self.client.post("/process_essay/",json=self.essay_data, headers={'X-API-Key': 'd3626f7c-5112-43a8-86a7-3ca100964772'})
        self.assertEqual(response.status_code,422)
        
    #Ensure that the same track_id sent is received in the response
    def test_track_id(self):
        self.essay_data["track_id"] = "456@same_track_id@456"
        response = self.client.post("/process_essay/",json=self.essay_data, headers={'X-API-Key': 'd3626f7c-5112-43a8-86a7-3ca100964772'})
        response_trackid = response.json()['data']
        self.assertEqual(response_trackid["track_id"],"456@same_track_id@456")
    
    #Ensure exceptions raised from the evaluate_essay function return status code 50#0
    def test_process_essay_exception(self):
        #patch the process_essay function with a mock exception to test response code
        with unittest.mock.patch('app.main.evaluate_essay',side_effect = pydantic.ValidationError("Mock Validation Error",[])):
            response = self.client.post("/process_essay/",json=self.essay_data, headers={'X-API-Key': 'd3626f7c-5112-43a8-86a7-3ca100964772'})
            self.assertEqual(response.status_code,500)


