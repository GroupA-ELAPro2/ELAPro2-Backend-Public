# Import Libraries

import os
#from dotenv import load_dotenv
from agent_files.agent_states import CentralAgentState, InputState, OutputState
#from agent_files.essay_answer_agent import answer_agent
from agent_files.grammar_agent import grammar_agent
from agent_files.lexical_agent import lexical_agent
from agent_files.coherence_agent import coherence_agent
from agent_files.task_agent import task_agent
from agent_files.eval_agent import meta_eval_agent
from agent_files.gap_analysis_agent import gap_analysis_agent
from langgraph.graph import StateGraph, START, END
from langchain_core.runnables import RunnableLambda

# Load environment variables

# Only load .env for local development
if os.getenv("RENDER") is None:
    from dotenv import load_dotenv
    load_dotenv()

# aggregates the comments of the agents to update the  
def aggregator(input:CentralAgentState)->CentralAgentState:
    return input

#Modify Callable agents to retriables
grammar_retriable = RunnableLambda(grammar_agent).with_retry(stop_after_attempt=5)
lexical_retriable = RunnableLambda(lexical_agent).with_retry(stop_after_attempt=5)
task_retriable = RunnableLambda(task_agent).with_retry(stop_after_attempt=5)
coherence_retriable = RunnableLambda(coherence_agent).with_retry(stop_after_attempt=5)
gap_retriable = RunnableLambda(gap_analysis_agent).with_retry(stop_after_attempt=5)
meta_retriable = RunnableLambda(meta_eval_agent).with_retry(stop_after_attempt=5)

# Build combined evaluation graph

builder = StateGraph(CentralAgentState, input_schema=InputState, output_schema=OutputState)

# Main evaluation nodes

builder.add_node("grammar_evaluation", grammar_retriable)
builder.add_node("lexical_evaluation",lexical_retriable)
builder.add_node("task_evaluation",task_retriable)
builder.add_node("coherence_evaluation",coherence_retriable)

# node to aggregate the results from the specialists into a single state
builder.add_node("aggregator",aggregator)

# Meta-evaluation node
builder.add_node("meta_evaluation" ,meta_retriable)

# Gap Analysis node
builder.add_node("gap_analysis" ,gap_retriable)

# # Map the gap analysis action plan to the output state
# builder.add_node("overall_summary" ,overview_summary)

# Connect edges

# Start → all main evaluation nodes in parallel
builder.add_edge(START, "grammar_evaluation")
builder.add_edge(START, "lexical_evaluation")
builder.add_edge(START, "task_evaluation")
builder.add_edge(START, "coherence_evaluation")

# Main evaluation nodes → overall feedback
builder.add_edge("grammar_evaluation", "aggregator")
builder.add_edge("lexical_evaluation", "aggregator")
builder.add_edge("task_evaluation", "aggregator")
builder.add_edge("coherence_evaluation", "aggregator")

try:
    eval_monitoring = os.getenv("EVAL_MONITORING")
    if eval_monitoring and eval_monitoring.lower() in ("true","1","yes","y"):
        eval_monitoring = True
    else:
        eval_monitoring = False
except:
    eval_monitoring = False
    
if eval_monitoring:
    # Overall feedback → meta evaluation (parallel node, not linked to END)
    builder.add_edge("aggregator", "meta_evaluation")
    builder.add_edge("meta_evaluation", END)

# Jump from aggregator to gap_analysis (parallel node, not linked to END)
builder.add_edge("aggregator", "gap_analysis")
    
# Overall feedback → END (main flow)
builder.add_edge("gap_analysis", END)

# Compile the graph
combined_graph = builder.compile()

import uuid

# # helper function to invoke graph
# def evaluate_essay(data:InputState):
#     return combined_graph.invoke(data, config={"configurable":{"thread_id":uuid.uuid4()}})

# helper function to invoke graph
def evaluate_essay(data:InputState):

    # ## to work for eval agent
    # if isinstance(data.track_id, tuple):
    #     data.track_id = data.track_id[0]        

    return combined_graph.invoke(data, config={"configurable":{"thread_id":data.track_id}})
 

