from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "DataProbe Server Running"}


@app.get("/health")
async def health():
    return {"status": "ok"}
