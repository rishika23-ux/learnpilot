from fastapi import FastAPI

app = FastAPI(title="LearnPilot API")


@app.get("/health")
def health_check():
    return {"status": "ok"}