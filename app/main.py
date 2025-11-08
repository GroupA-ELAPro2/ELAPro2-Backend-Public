from fastapi import FastAPI, HTTPException, status, Depends
from agent_files.central_agent import evaluate_essay
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import JSONResponse, HTMLResponse
import json
from agent_files.agent_states import InputState,OutputState
import os
from app.auth import get_user
import markdown
from pathlib import Path
import io

#Get summarised readme file for docs page
script_path = Path(__file__).resolve()
md_file_loc = script_path.parent.parent / "README_connect.md"
readme_file = open(md_file_loc,encoding='utf-8')
desc = readme_file.read()
readme_file.close()

#Initialise FastAPI
app = FastAPI(title="IELTS Essay Evaluator",
              summary="Connection to backend service application used to grade IELTS essays and provide feedback",
              description = desc,
              version="2.0.0",
              contact={"name":"Capstone Group A - SP4/6 2025","email":"capstone_grA_2025@outlook.com"})

#Router for process_essay with no authentication. Displays summarised readme as HTML
@app.get("/process_essay/", response_class=HTMLResponse)
async def return_readme():
    output_buffer = io.BytesIO()
    script_path = Path(__file__).resolve()
    md_file_loc = script_path.parent.parent / "README_connect.md"
    markdown.markdownFromFile(input=str(md_file_loc),output=output_buffer)
    html_body = output_buffer.getvalue().decode('utf-8')
    html_content = f"""
        <!DOCTYPE html>
    <html>
    <head>
        <title>ELA Pro2 README</title>
    </head>
    <body>
        {html_body}
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

#Router to process essay. Requires API Key authentication
@app.post("/process_essay/", response_model=OutputState, dependencies=[Depends(get_user)])
async def process_essay(data: InputState, user: str=Depends(get_user)):
    # Print to terminal User Authentication
    print(f"Authenticated User: {user}", flush=True)
    # Print post request to terminal
    print("📤 Request from frontend:", flush=True)
    source_data = data.model_dump()
    print(source_data, flush=True)
    
    # Call LangGraph Essay Evaluation
    try:
        frontend_response = evaluate_essay(data)
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to Process Feedback")
    else:
        # Print to terminal running FastAPI process
        print("📤 Response to frontend:", flush=True)
        print(json.dumps({"data": frontend_response}, indent=2), flush=True)

        return JSONResponse(content={"data": frontend_response})

#Router to ping backend and display status
@app.get("/", response_class=HTMLResponse)
async def get_handler():
    return HTMLResponse(content=f"""
                            <!DOCTYPE html>
                        <html>
                        <head>
                            <title>ELA Pro2</title>
                        </head>
                        <body>
                            <h4>Backend Service is Running</h4>
                            This is the <b>{os.getenv('ELA_ENV')}</b> environment
                        </body>
                        </html>
                        
                        
                        """
    )
    
