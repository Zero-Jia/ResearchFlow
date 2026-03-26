from fastapi import FastAPI

app = FastAPI(title="ResearchFlow API")


@app.get("/")
def root():
    return {
        "message": "ResearchFlow backend is ready"
    }