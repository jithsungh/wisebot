import shutil
import os
import sys
import asyncio
import uuid
from datetime import datetime
from typing import Dict, Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse

# Add the services directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'services'))

from extractText import extract_text
from feedDoc import setup_knowledge_base

router = APIRouter()

# In-memory storage for processing status (in production, use Redis or database)
processing_status: Dict[str, Dict] = {}

async def process_document_async(file_path: str, filename: str, processing_id: str):
    """Async function to process document in background"""
    try:
        # Update status to processing
        processing_status[processing_id]["status"] = "processing"
        processing_status[processing_id]["message"] = "Extracting text from document..."
        
        # Extract text from document
        extracted_text = extract_text(file_path)
        
        if not extracted_text.strip():
            processing_status[processing_id]["status"] = "error"
            processing_status[processing_id]["message"] = "No text could be extracted from the document"
            return
        
        processing_status[processing_id]["message"] = "Processing text and creating knowledge chunks..."
        
        # Process and add to knowledge base
        doc_count = setup_knowledge_base(extracted_text, "manuals")
        
        # Update status to completed
        processing_status[processing_id]["status"] = "completed"
        processing_status[processing_id]["message"] = f"Successfully processed {filename}"
        processing_status[processing_id]["chunks_created"] = doc_count
        processing_status[processing_id]["text_length"] = len(extracted_text)
        processing_status[processing_id]["completed_at"] = datetime.now().isoformat()
        
    except Exception as e:
        processing_status[processing_id]["status"] = "error"
        processing_status[processing_id]["message"] = str(e)
        
        # Clean up temp file on error
        if os.path.exists(file_path):
            os.remove(file_path)

@router.post("/")
async def save_file(file: UploadFile = File(...)):
    """Save uploaded file"""
    try:
        # Ensure uploads directory exists
        os.makedirs("uploads", exist_ok=True)
        
        file_path = f"uploads/{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        return {"message": f"File saved at {file_path}", "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

@router.post("/process-async")
async def process_document_async_endpoint(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """Upload and process document asynchronously"""
    try:
        # Generate unique processing ID
        processing_id = str(uuid.uuid4())
        
        # Save file first
        os.makedirs("uploads", exist_ok=True)
        file_path = f"uploads/{file.filename}"
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Initialize processing status
        processing_status[processing_id] = {
            "status": "uploaded",
            "message": "File uploaded successfully, processing started...",
            "filename": file.filename,
            "file_size": os.path.getsize(file_path),
            "started_at": datetime.now().isoformat()
        }
        
        # Start background processing
        background_tasks.add_task(
            process_document_async,
            file_path,
            file.filename,
            processing_id
        )
        
        return {
            "processing_id": processing_id,
            "message": "File uploaded successfully. Processing started in background.",
            "filename": file.filename,
            "status": "processing_started"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")

@router.get("/status/{processing_id}")
async def get_processing_status(processing_id: str):
    """Get the status of document processing"""
    if processing_id not in processing_status:
        raise HTTPException(status_code=404, detail="Processing ID not found")
    
    return processing_status[processing_id]

@router.post("/process")
async def process_and_feed_document(file: UploadFile = File(...)):
    """Process document and add to knowledge base (synchronous - original endpoint)"""
    """Process document and add to knowledge base"""
    try:
        # Save file temporarily
        os.makedirs("uploads", exist_ok=True)
        file_path = f"uploads/{file.filename}"
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Extract text from document
        try:
            extracted_text = extract_text(file_path)
        except Exception as e:
            # Clean up temp file
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(status_code=400, detail=f"Failed to extract text: {str(e)}")
        
        if not extracted_text.strip():
            # Clean up temp file
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(status_code=400, detail="No text could be extracted from the document")
        
        # Process and add to knowledge base
        try:
            doc_count = setup_knowledge_base(extracted_text, "manuals")
        except Exception as e:
            # Clean up temp file
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")
        
        # Clean up temp file (optional - you might want to keep it)
        # if os.path.exists(file_path):
        #     os.remove(file_path)
        
        return {
            "message": f"Successfully processed {file.filename}",
            "filename": file.filename,
            "text_length": len(extracted_text),
            "chunks_created": doc_count,
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.get("/list")
async def list_uploaded_files():
    """List all uploaded files"""
    try:
        if not os.path.exists("uploads"):
            return {"files": []}
        
        files = []
        for filename in os.listdir("uploads"):
            file_path = os.path.join("uploads", filename)
            if os.path.isfile(file_path):
                stat = os.stat(file_path)
                files.append({
                    "filename": filename,
                    "size": stat.st_size,
                    "modified": stat.st_mtime
                })
        
        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")
