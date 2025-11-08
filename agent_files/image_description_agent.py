#AI agent to look at an image url and provide a description of the image.
#Returns either an image description or None

# Import Libraries

import os
from agent_files.agent_states import ImageDescriptionOutput, ToolState
from agent_files.helper_functions import get_llm
from langgraph.graph import StateGraph, START, END
from urllib.parse import urlparse
import requests
from langchain_core.messages import HumanMessage

# ----------------------------
# Load environment variables
# ----------------------------
# Only load .env for local development
if os.getenv("RENDER") is None:
    from dotenv import load_dotenv
    load_dotenv()

# Read API keys and models from environment variables
gemini_api_key = os.getenv("GEMINI_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("IMAGE_MODEL")

# ----------------------------
# Initialize LLM
# ----------------------------

llm = get_llm(model=model,
              gemini_key=gemini_api_key,
              openai_key=openai_api_key,
              name="image_description_agent",
              temperature=0)

image_structured = llm.with_structured_output(ImageDescriptionOutput)


# ----------------------------
# Valid Image Function
# ----------------------------
def is_image_url(url):
    #Checks if a given URL points to an image by inspecting the Content-Type header.
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        # Use requests.head() for efficiency as it only retrieves headers
        # allow_redirects=True handles redirects, timeout prevents hanging
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        print(f"status_code:{response.status_code}")
        content_type = response.headers.get('Content-Type', '')
        return content_type.startswith('image/') and (200 <= response.status_code < 300)
    except requests.exceptions.RequestException as e:
        # Catch various request-related exceptions (e.g., connection errors, timeouts)
        return False


# ----------------------------
# Image evaluation function
# ----------------------------
def image_evaluation(input_state: ToolState) -> ImageDescriptionOutput:
    prompt = HumanMessage(
        content=[
            {"type":"text",
             "text":f"""
Provide a short summary of the context of the image.
Identify the type of image (diagram, graph, table, chart, map or other).
Only provide facutal content about the visual (explain trends, the components, colour coding etc.)
Keep the context summary to no more than 3 sentences.

If it is not a single image or you are unable to provide a description then don't respond.
"""},
            {"type":"image_url","image_url":{"url":input_state.image_url}}])

    if input_state.image_url != None and \
            is_image_url(input_state.image_url) and \
                (input_state.image_description == None or len(input_state.image_description)==0 or input_state.image_description=="null"):
        # Call LLM
        response = image_structured.invoke([prompt])
        if response == "" or None:
            return ImageDescriptionOutput(image_description=input_state.image_description)
    else:
        return ImageDescriptionOutput(image_description=input_state.image_description)
    return response

# ----------------------------
# Build SubGraph
# ----------------------------
subgraph_builder = StateGraph(ImageDescriptionOutput, input_schema=ToolState, output_schema=ImageDescriptionOutput)
subgraph_builder.add_node("Image Evaluator",image_evaluation)
subgraph_builder.add_edge(START,"Image Evaluator")
subgraph_builder.add_edge("Image Evaluator",END)
graph = subgraph_builder.compile()

#Call graph
def image_agent(data):
     return graph.invoke(data)