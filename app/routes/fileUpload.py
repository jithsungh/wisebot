import shutil
from fastapi import FastAPI, UploadFile, File

app = FastAPI()

@app.post("/")
async def save_file(file: UploadFile = File(...)):
    file_path = f"uploads/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"message": f"File saved at {file_path}"}
