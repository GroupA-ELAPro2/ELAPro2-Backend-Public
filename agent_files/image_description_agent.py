# Import Libraries
import os
from agent_files.agent_states import ImageDescriptionOutput, ToolState
from agent_files.helper_functions import get_llm
from langgraph.graph import StateGraph, START, END
import requests
from langchain_core.messages import HumanMessage

# Load environment variables

# Only load .env for local development
if os.getenv("RENDER") is None:
    from dotenv import load_dotenv

    load_dotenv()

# Read API keys and models from environment variables
gemini_api_key = os.getenv("GEMINI_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")
model = os.getenv("IMAGE_MODEL")

# Initialise LLM
llm = get_llm(
    model=model,
    gemini_key=gemini_api_key,
    openai_key=openai_api_key,
    name="image_description_agent",
    temperature=0,
)

# Initialise LLM with structured output
image_structured = llm.with_structured_output(ImageDescriptionOutput)


# Image evaluation
def image_evaluation(input_state: ToolState) -> ImageDescriptionOutput:
    """Generate a concise description of an image for Academic Writing Task 1.

    Analyzes visual content (charts, graphs, diagrams, tables, maps) and provides
    a factual summary of key elements, trends, and components. Only generates a new
    description if a valid image URL is provided and no existing description is present.

    Args:
        input_state (ToolState): Tool state containing image URL and any existing description.

    Returns:
        ImageDescriptionOutput: Image description (either newly generated or existing).
    """
    prompt = HumanMessage(
        content=[
            {
                "type": "text",
                "text": f"""
Provide a short summary of the context of the image.
Identify the type of image (diagram, graph, table, chart, map or other).
Only provide facutal content about the visual (explain trends, the components, colour coding etc.)
Keep the context summary to no more than 3 sentences.

If it is not a single image or you are unable to provide a description then don't respond.
""",
            },
            {"type": "image_url", "image_url": {"url": input_state.image_url}},
        ]
    )

    if input_state.is_image_url() and (
        input_state.image_description == None
        or len(input_state.image_description) == 0
        or input_state.image_description == "null"
    ):
        # Call LLM
        response = image_structured.invoke([prompt])
        if response == "" or None:
            return ImageDescriptionOutput(
                image_description=input_state.image_description
            )
    else:
        return ImageDescriptionOutput(image_description=input_state.image_description)
    return response


# Build SubGraph
subgraph_builder = StateGraph(
    ImageDescriptionOutput, input_schema=ToolState, output_schema=ImageDescriptionOutput
)

# Add node to generate image description for Academic Writing Task 1 visuals
subgraph_builder.add_node("Image Evaluator", image_evaluation)

# Define workflow: START -> evaluator -> END
subgraph_builder.add_edge(START, "Image Evaluator")
subgraph_builder.add_edge("Image Evaluator", END)

# Compile the subgraph
graph = subgraph_builder.compile()


def image_agent(data):
    """Execute the image evaluation agent workflow.

    Args:
        data: Input data for image evaluation.

    Returns:
        Image evaluation results from the graph execution.
    """
    return graph.invoke(data)
