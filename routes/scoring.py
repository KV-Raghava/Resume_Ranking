import io
import csv
from typing import List, Dict

import PyPDF2
from docx import Document
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse
from openai import OpenAI
import json
import random
import os
router = APIRouter()



def extract_header_title(criteria: str) -> str:
    """
    Use OpenAI to extract a concise header title for the given criterion.
    
    Example:
      Input: "Must have certification XYZ"
      Output: "Certification XYZ"
    """
    client = OpenAI()
    completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": """
            You are an expert HR evaluator. Your task is to extract a concise header title for a given candidate evaluation criterion.
            Here is an example for you:
            input: "Proficient in RAG implementations and vector database operations"
            output: "RAG & Vector Databases"
"""},
        {
            "role": "user",
            "content": f""" 
            Extract a concise header title for the following candidate evaluation criterion:{criteria}.
            Respond with only the header title , don't add any extra words or lines before or after the header title."""
        }
    ],
temperature=0.2,
)
    header_title = completion.choices[0].message.content
    return header_title

def extract_text_from_pdf(file_bytes: bytes) -> str:
    reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

def extract_text_from_docx(file_bytes: bytes) -> str:
    document = Document(io.BytesIO(file_bytes))
    return "\n".join([para.text for para in document.paragraphs])

def extract_text_from_file(uploaded_file: UploadFile) -> str:
    file_bytes = uploaded_file.file.read()
    uploaded_file.file.seek(0)
    if uploaded_file.filename.lower().endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    elif uploaded_file.filename.lower().endswith(".docx"):
        return extract_text_from_docx(file_bytes)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type. Use PDF or DOCX.")

def evaluate_resume(header_titles: dict, resume_text: str, criteria: List[str]) -> dict:
    """
    Evaluate the resume text against the provided list of criteria.
    In a single OpenAI call, extract the candidate's full name and score the resume on each criterion.
    The LLM is instructed to return a JSON object with the following structure:
    
      {
         "Candidate Name": "<candidate name>",
         "Scores": {
             "<criterion 1>": <score>,
             "<criterion 2>": <score>,
             ...
         },
         "Total Score": <sum of scores>
      }
    """
   
    criteria_text = "\n".join([f"- {header_titles[crit]} : {crit}" for crit in criteria])
    sample_dict = {"Candidate's Name": "John Doe"}
    
    # For each criterion, generate a random score between 0 and 10.
    for crit, header in header_titles.items():
        sample_dict[header] = random.randint(0, 10)

    # Calculate total score as the sum of individual scores.
    sample_dict["Total Score"] = sum(sample_dict[header] for header in header_titles.values())

    # Convert the dictionary to a nicely formatted JSON string.
    sample_output = json.dumps(sample_dict, indent=2)
    client = OpenAI()
    completion = client.chat.completions.create(
    model="gpt-4o",
    messages=[
            {"role": "system", "content": """
    You are an expert HR evaluator. Your job is to evaluate a candidate's resume against a list of evaluation criteria.
    You need to extract the candidate's full name from the resume, assign a score between 0 and 10 for each criterion, calculate the total score and
    return the result in a JSON format.
    Use exactly the same header names as provided in the criteria input. 
    Ensure that you give only the json response and don't add any extra words or lines before or after the json body.
    Here is an example for you on how to replicate the headers in the criteria in the final output json:
            input(criteria): 
- Prompt Engineering & LLM Deployment : Hands-on experience with prompt engineering, fine-tuning, and deploying LLM-driven applications
- RAG & Vector Databases : Proficient in RAG implementations and vector database operations
- Azure OpenAI & AI Search : Strong understanding of Azure OpenAI and Azure AI Search
- MLOps & Scalable Pipelines : Knowledge of MLOps practices for managing AI workflows and deploying scalable pipelines
- SQL & NoSQL Databases : Familiarity with SQL and NoSQL databases, including Azure Cosmos DB
- OpenAI-Python & Related Frameworks : Experience with OpenAI-Python, LiteLLM, Pydentic and related frameworks
- Azure Certifications : Azure Certifications such as Microsoft Certified: Azure AI Engineer Associate or Azure Solutions Architect Expert
- AI Workflows in Microsoft Ecosystem : Experience designing and integrating AI-driven enterprise workflows within the Microsoft ecosystem
- Reinforcement Learning & Multi-Modal AI : Experience with advanced techniques (reinforcement learning, multi-modal AI)
- Open-Source AI Contributions : Contributions to open-source AI projects
- Team Communication : Foster open communication within the team
- Teamwork & Quality Results : Demonstrate commitment to teamwork by delivering high-quality results consistently
- Entrepreneurial Mindset : Approach challenges with an entrepreneurial mindset
- Strategic Thinking & Problem-Solving : Strategic thinking and problem-solving capabilities
- Adaptability to Fast-Paced Innovation : Adaptability to a fast-paced, innovation-driven environment
             
            output: 
{"Candidate's Name": "John Doe",
  "Prompt Engineering & LLM Deployment": 3,
  "RAG & Vector Databases": 8,
  "Azure OpenAI & AI Search": 7,
  "MLOps & Scalable Pipelines": 10,
  "SQL & NoSQL Databases": 3,
  "OpenAI-Python & Related Frameworks": 2,
  "Azure Certifications": 5,
  "AI Workflows in Microsoft Ecosystem": 2,
  "Reinforcement Learning & Multi-Modal AI": 10,
  "Open-Source AI Contributions": 6,
  "Team Communication": 0,
  "Teamwork & Quality Results": 1,
  "Entrepreneurial Mindset": 9,
  "Strategic Thinking & Problem-Solving": 0,
  "Adaptability to Fast-Paced Innovation": 1,
  "Total Score": 67}

    """},
            {
                "role": "user",
                "content": f""" 
Here is the resume text:
{resume_text}
Here are the evaluation criteria:
{criteria_text}
Ensure that you give only the json response and don't add any extra words or lines before or after the json body.
                """
            }
        ],
    temperature=0.2,
    )
    result = completion.choices[0].message.content
    if "```json" in result:
        result_str = result.strip()
        result_str = result_str.replace("```json", "").replace("```", "").strip()
        result_json = json.loads(result_str)
    else:
        result_json = json.loads(result)
    sol  = []
    sol.append(result_json["Candidate's Name"])
    for crit in criteria:
        sol.append(result_json[header_titles[crit]])
    sol.append(result_json["Total Score"])
    return sol
@router.post("/score-resumes", 
             summary="Score resumes against provided criteria",
             responses={
        200: {
            "content": {
                "text/csv": {
                    "example": (
                        "Name,Prompt Engineering & LLM Deployment,RAG & Vector Databases,Azure OpenAI & AI Search,Total_Score\n"
                        "John Doe,3,8,7,18\n"
                    )
                }
            },
            "description": "CSV file containing candidate evaluation scores."
        }
    })
async def score_resumes(
    criteria: List[str] = Form(...),
    files: List[UploadFile] = File(...)
):
    
    header_titles = {}
    for crit in criteria:
        header = extract_header_title(crit)
        header_titles[crit] = header
    titles= []
    titles.append("Name")
    for crit in criteria:
        titles.append(header_titles[crit])
    titles.append("Total_Score")
    data = []
    # data.append(titles)
    for file in files:
        resume_text = extract_text_from_file(file)
        
        evaluation = evaluate_resume(header_titles, resume_text, criteria)
        data.append(evaluation)
    # data = [["Name", "Age", "City"], ["Alice", 30, "New York"], ["Bob", 25, "Los Angeles"]]
    data.sort(key=lambda x: x[-1], reverse=True)
    data.insert(0, titles)
    # Create CSV in-memory
    stream = io.StringIO()
    writer = csv.writer(stream)
    writer.writerows(data)
    stream.seek(0)

    return StreamingResponse(stream, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=data.csv"})
