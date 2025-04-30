from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from app.graph import generate_market_plot

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/generate-plot")
async def generate_plot(request: Request):
    data = await request.json()
    subject = data["subject"]
    comparables = data["comparables"]

    region = subject["city"]
    effective_date = subject["effective_date"]
    output_path = f"app/static/{region}_latest1.png"

    generate_market_plot(region, subject, comparables, output_path)
    return FileResponse(output_path, media_type="image/png")
