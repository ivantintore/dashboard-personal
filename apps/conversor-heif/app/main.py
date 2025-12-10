from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from pathlib import Path
from typing import List, Optional
import zipfile
import tempfile
import shutil
import sys

from config.settings import settings
from app.core.processors.batch_processor import BatchProcessor
from app.core.validators.file_validator import FileValidator
from app.utils.file_utils import create_temp_dir, cleanup_temp_dir
from app.utils.logger import logger


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Conversor profesional de imágenes HEIC y PDF a JPG con compresión configurable"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/web/static"), name="static")

# Create uploads directory if it doesn't exist
os.makedirs(settings.upload_dir, exist_ok=True)


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main HTML page"""
    with open("app/web/templates/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/debug.html", response_class=HTMLResponse)
async def debug_page():
    """Serve debug page for troubleshooting"""
    with open("debug.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": settings.app_version}


@app.post("/api/convert")
async def convert_files(
    files: List[UploadFile] = File(...),
    quality: int = Form(85),
    compression: int = Form(85)
):
    """
    Convert multiple HEIC/PDF files to JPG
    """
    logger.api_request("POST", "/api/convert")
    logger.info(f"Received conversion request: {len(files)} files, quality={quality}, compression={compression}")
    
    try:
        # Log file details
        for i, file in enumerate(files):
            logger.debug(f"Upload file {i}: {file.filename} ({file.size} bytes, {file.content_type})")
        
        # Validate files
        validator = FileValidator()
        for file in files:
            if not validator.validate_file(file):
                logger.warning(f"File validation failed for: {file.filename}")
                raise HTTPException(
                    status_code=400, 
                    detail=f"Archivo no válido: {file.filename}"
                )
        
        logger.info("All files passed validation")
        
        # Process files
        processor = BatchProcessor()
        results = await processor.process_files(files, quality, compression)
        
        # Log result structure
        logger.info(f"BatchProcessor returned: {type(results)} with keys: {list(results.keys()) if isinstance(results, dict) else 'N/A'}")
        if isinstance(results, dict):
            logger.info(f"Result success: {results.get('success')}")
            if results.get('success'):
                logger.info(f"Task ID: {results.get('task_id')}")
                logger.info(f"Processed files: {results.get('processed_files')}")
            else:
                logger.error(f"BatchProcessor failed: {results.get('error')}")
        
        # Return the BatchProcessor result directly (it already has the correct structure)
        return results
        
    except HTTPException as he:
        logger.warning(f"HTTP exception in convert_files: {he.status_code} - {he.detail}")
        raise
    except Exception as e:
        logger.exception(e, "convert_files endpoint")
        error_msg = f"Error procesando archivos: {str(e)}"
        raise HTTPException(status_code=500, detail=error_msg)


@app.get("/api/download/{task_id}")
async def download_converted_files(task_id: str):
    """
    Download converted files as ZIP
    """
    logger.api_request("GET", f"/api/download/{task_id}")
    
    try:
        logger.info(f"Download request for task_id: {task_id}")
        
        zip_path = Path(f"temp/{task_id}.zip")
        logger.debug(f"Looking for ZIP at: {zip_path.absolute()}")
        
        if not zip_path.exists():
            logger.warning(f"ZIP file not found: {zip_path}")
            
            # Check if task directory exists
            task_dir = Path(f"temp/{task_id}")
            if task_dir.exists():
                files_in_dir = list(task_dir.glob("*"))
                logger.info(f"Task directory exists with files: {[f.name for f in files_in_dir]}")
            else:
                logger.info(f"Task directory does not exist: {task_dir}")
            
            # List all ZIP files in temp directory
            temp_dir = Path("temp")
            if temp_dir.exists():
                zip_files = list(temp_dir.glob("*.zip"))
                logger.info(f"Available ZIP files: {[f.name for f in zip_files]}")
            
            raise HTTPException(
                status_code=404, 
                detail=f"Archivo ZIP no encontrado para task_id: {task_id}"
            )
        
        zip_size = zip_path.stat().st_size
        logger.info(f"Serving ZIP file: {zip_path.name} ({zip_size} bytes)")
        
        return FileResponse(
            path=str(zip_path),
            filename=f"converted_images_{task_id}.zip",
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename=converted_images_{task_id}.zip"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(e, f"download_converted_files for task {task_id}")
        error_msg = f"Error descargando archivo: {str(e)}"
        raise HTTPException(status_code=500, detail=error_msg)


if __name__ == "__main__":
    try:
        logger.info("Starting Conversor HEIC + PDF a JPG...")
        logger.info(f"Server will start on: http://localhost:8000")
        logger.info(f"Debug mode: {settings.debug}")
        
        # Start server directly with uvicorn
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=settings.debug,
            log_level="info" if not settings.debug else "debug"
        )
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
        
    except Exception as e:
        logger.exception(e, "server startup")
        sys.exit(1)
