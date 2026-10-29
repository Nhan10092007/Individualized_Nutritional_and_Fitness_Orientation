from fastapi import FastAPI

app = FastAPI(title="Fitness & Nutrition API")


@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "message": "Fitness API is running"
    }