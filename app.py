from fastapi import FastAPI
from routes import criteria, scoring
from dotenv import load_dotenv

load_dotenv()
app = FastAPI(
    title="Resume Ranking API",
    description="API endpoints to extract ranking criteria and score resumes.",
    version="1.0.0"
)

# Include the criteria router (e.g., under the '/job' prefix)
app.include_router(criteria.router, prefix="/job", tags=["Job Description Processing"])

# Include the scoring router (e.g., under the '/resume' prefix)
app.include_router(scoring.router, prefix="/resume", tags=["Resume Scoring"])

@app.get("/", summary="Welcome")
async def root():
    return {"message": "Welcome to the Resume Ranking API. Visit /docs for API documentation."}
