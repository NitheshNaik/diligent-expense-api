from fastapi import FastAPI

app = FastAPI(title="Smart Expense Tracker")


@app.get("/health")
def health_check():
    return {"status": "ok"}
