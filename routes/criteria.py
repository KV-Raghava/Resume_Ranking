import io
from typing import List
import os
import PyPDF2
from docx import Document
from fastapi import APIRouter, UploadFile, File, HTTPException
from openai import OpenAI
import json
import logging


router = APIRouter()

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
    # Reset pointer so file can be re-read if needed.
    uploaded_file.file.seek(0)
    if uploaded_file.filename.lower().endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    elif uploaded_file.filename.lower().endswith(".docx"):
        return extract_text_from_docx(file_bytes)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type. Use PDF or DOCX.")

def extract_criteria_from_text(text: str) -> List[str]:
    
    
    
    try:
        
        client = OpenAI()
        completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
                {"role": "system", "content": """
        You are an expert HR assistant with extensive experience in evaluating job descriptions.
        Your task is to analyze a job description and extract all key ranking criteria that employers use 
        to evaluate candidates. These criteria should include key criteria such as required skills, certifications, years of experience
        educational qualifications, and any other important attributes that can help rank a candidate
        Your response must be a json with one field as criteria, which is a list of criteria.
        Ensure that you give only the json response and don't add any extra words or lines before or after the json body.
        sample output :{
        "criteria": [
            "Must have certification XYZ",
            "5+ years of experience in Python development",
            "Strong background in Machine Learning"
        ]
        }
        """},
                {
                    "role": "user",
                    "content": f"Extract the key ranking criteria from this job description:{text}"
                }
            ],
        temperature=0.2,
        )
        criteria = completion.choices[0].message.content
        if "```json" in criteria:
            result_str = criteria.strip()
            result_str = result_str.replace("```json", "").replace("```", "").strip()
            criteria = json.loads(result_str)
        else:
            criteria = json.loads(criteria)
        return criteria["criteria"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM extraction failed: {str(e)}")

@router.post("/extract-criteria", summary="Extract ranking criteria from a job description", responses={
        200: {
            "content": {
                "application/json": {
                    "example": {
                        "criteria": [
                            "Must have certification XYZ",
                            "5+ years of experience in Python development",
                            "Strong background in Machine Learning"
                        ]
                    }
                }
            },
            "description": "A JSON object with a list of ranking criteria."
        }
    })
async def extract_criteria(file: UploadFile = File(...)):
    text = extract_text_from_file(file)
    criteria = extract_criteria_from_text(text)
    return {"criteria": criteria}
