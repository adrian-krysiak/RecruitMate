from fastapi import FastAPI


app = FastAPI(title="RecruitMate ML Service")


@app.get("/")
async def read_root():
    return {"message": "ML Service is up and running!", "status": "ok"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
