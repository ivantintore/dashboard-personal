import os
import asyncio
import uuid
from pathlib import Path
from typing import List, Dict, Any
from fastapi import UploadFile
import aiofiles
import zipfile
import tempfile
import shutil
import threading
import time

from app.core.converters.heic_converter import HEICConverter
from app.core.converters.pdf_converter import PDFConverter
from app.core.validators.file_validator import FileValidator
from app.utils.logger import logger
from config.settings import settings


class BatchProcessor:
    """Processes multiple files (HEIC/PDF/Images) in batch with progress tracking"""
    
    def __init__(self):
        self.heic_converter = HEICConverter()
        self.pdf_converter = PDFConverter()
        self.file_validator = FileValidator()
        self.temp_dir = Path("temp")
        self.temp_dir.mkdir(exist_ok=True)
    
    async def process_files(
        self, 
        files: List[UploadFile], 
        quality: int = 85,
        compression: int = 85
    ) -> Dict[str, Any]:
        """
        Process multiple files (HEIC/PDF/Images) and return results
        
        Args:
            files: List of uploaded files
            quality: JPG quality (1-100)
            compression: Compression level (1-100)
            
        Returns:
            Dict with processing results and download info
        """
        try:
            # Generate unique task ID
            task_id = str(uuid.uuid4())
            task_dir = self.temp_dir / task_id
            task_dir.mkdir(exist_ok=True)
            
            logger.conversion_start(task_id, len(files), "mixed")
            
            # Separate files by type
            heic_files = []
            pdf_files = []
            image_files = []
            
            logger.info(f"Processing {len(files)} uploaded files for task {task_id}")
            for i, file in enumerate(files):
                logger.debug(f"File {i}: {file.filename} (size: {file.size}, type: {file.content_type})")
                
                if file.filename.lower().endswith(('.heic', '.heif')):
                    heic_files.append(file)
                    logger.debug(f"  Categorized as HEIC file: {file.filename}")
                elif file.filename.lower().endswith('.pdf'):
                    pdf_files.append(file)
                    logger.debug(f"  Categorized as PDF file: {file.filename}")
                elif file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp')):
                    image_files.append(file)
                    logger.debug(f"  Categorized as Image file: {file.filename}")
                else:
                    logger.warning(f"Unknown file type: {file.filename}")
            
            logger.info(f"File distribution: {len(heic_files)} HEIC, {len(pdf_files)} PDF, {len(image_files)} Images")
            
            # Process files in parallel
            tasks = []
            
            # Process HEIC files
            if heic_files:
                heic_task = self._process_heic_files(heic_files, task_dir, quality, compression)
                tasks.append(heic_task)
            
            # Process PDF files
            if pdf_files:
                pdf_task = self._process_pdf_files(pdf_files, task_dir, quality, compression)
                tasks.append(pdf_task)
            
            # Process other image files
            if image_files:
                image_task = self._process_image_files(image_files, task_dir, quality, compression)
                tasks.append(image_task)
            
            # Wait for all tasks to complete
            logger.info(f"Waiting for {len(tasks)} tasks to complete...")
            results = await asyncio.gather(*tasks, return_exceptions=True)
            logger.info(f"Got {len(results)} task results")
            
            # Combine results - FIXED: Properly handle different result types
            all_results = []
            for i, result in enumerate(results):
                logger.debug(f"Processing task result {i}: type={type(result)}")
                
                if isinstance(result, list):
                    logger.debug(f"  Result is list with {len(result)} items")
                    all_results.extend(result)
                    for j, item in enumerate(result):
                        logger.debug(f"    Item {j}: success={item.get('success')}")
                elif isinstance(result, dict):
                    logger.debug(f"  Result is dict: success={result.get('success')}")
                    # Handle both successful and failed results
                    if result.get('success'):
                        all_results.append(result)
                        logger.debug(f"    Added successful result")
                    elif 'error' in result:
                        all_results.append(result)
                        logger.debug(f"    Added failed result")
                elif isinstance(result, Exception):
                    logger.error(f"Task {i} returned exception: {result}")
                    # Handle exceptions from asyncio.gather
                    all_results.append({
                        "success": False,
                        "error": str(result),
                        "error_type": type(result).__name__
                    })
                    logger.debug(f"    Added exception result")
            
            logger.info(f"Final results: {len(all_results)} items")
            successful_results = [r for r in all_results if r.get('success')]
            failed_results = [r for r in all_results if not r.get('success')]
            logger.info(f"Success: {len(successful_results)}, Failed: {len(failed_results)}")
            
            # Create final ZIP file
            zip_path = await self._create_final_zip(task_dir, task_id, all_results)
            
            # Schedule cleanup after 5 minutes to allow downloads
            self._schedule_delayed_cleanup(task_dir, task_id, delay_minutes=5)
            
            return {
                "success": True,
                "task_id": task_id,
                "total_files": len(files),
                "heic_files": len(heic_files),
                "pdf_files": len(pdf_files),
                "image_files": len(image_files),
                "processed_files": len([r for r in all_results if r.get('success')]),
                "download_url": f"/api/download/{task_id}",
                "zip_path": str(zip_path),
                "results": all_results
            }
            
        except Exception as e:
            logger.exception(e, f"BatchProcessor.process_files for task {task_id if 'task_id' in locals() else 'unknown'}")
            
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    async def _process_heic_files(
        self, 
        files: List[UploadFile], 
        output_dir: Path, 
        quality: int, 
        compression: int
    ) -> List[Dict]:
        """Process HEIC files and return conversion results"""
        results = []
        
        logger.info(f"🖼️ Processing {len(files)} HEIC files...")
        for i, file in enumerate(files):
            logger.info(f"🖼️ Processing HEIC file {i+1}/{len(files)}: {file.filename}")
            try:
                # Save uploaded file temporarily
                temp_path = output_dir / f"temp_{file.filename}"
                logger.debug(f"💾 Saving HEIC temp file to: {temp_path}")
                
                async with aiofiles.open(temp_path, 'wb') as f:
                    content = await file.read()
                    await f.write(content)
                    logger.debug(f"💾 Saved {len(content)} bytes to HEIC temp file")
                
                # Convert file
                output_filename = self.heic_converter._generate_output_filename(temp_path)
                output_path = output_dir / output_filename
                logger.debug(f"🔄 Converting HEIC to: {output_path}")
                
                result = await self.heic_converter.convert_file(
                    temp_path, output_path, quality, compression
                )
                
                logger.info(f"📊 HEIC Conversion result: {result}")
                
                if result['success']:
                    results.append(result)
                    logger.info(f"✅ Successfully converted HEIC: {file.filename}")
                else:
                    logger.error(f"❌ Failed to convert HEIC: {file.filename} - {result.get('error', 'Unknown error')}")
                    results.append(result)
                
                # Don't delete temp file yet - we need it for the ZIP
                # temp_path.unlink(missing_ok=True)
                
            except Exception as e:
                error_msg = str(e)
                logger.exception(e, f"processing HEIC file {file.filename}")
                results.append({
                    "success": False,
                    "filename": file.filename,
                    "error": error_msg
                })
        
        logger.info(f"🖼️ HEIC processing complete. {len([r for r in results if r.get('success')])} successful, {len([r for r in results if not r.get('success')])} failed")
        return results
    
    async def _process_image_files(
        self, 
        files: List[UploadFile], 
        output_dir: Path, 
        quality: int, 
        compression: int
    ) -> List[Dict]:
        """Process image files and return conversion results"""
        results = []
        
        print(f"🖼️ Processing {len(files)} image files...")
        for i, file in enumerate(files):
            print(f"🖼️ Processing image file {i+1}/{len(files)}: {file.filename}")
            try:
                # Save uploaded file temporarily
                temp_path = output_dir / f"temp_{file.filename}"
                print(f"💾 Saving temp file to: {temp_path}")
                
                async with aiofiles.open(temp_path, 'wb') as f:
                    content = await file.read()
                    await f.write(content)
                    print(f"💾 Saved {len(content)} bytes to temp file")
                
                # Convert to JPG
                output_filename = Path(file.filename).stem + ".jpg"
                output_path = output_dir / output_filename
                print(f"🔄 Converting to: {output_path}")
                
                result = await self._convert_image_to_jpg(temp_path, output_path, quality, compression)
                print(f"📊 Conversion result: {result}")
                
                if result['success']:
                    results.append(result)
                    print(f"✅ Successfully converted: {file.filename}")
                else:
                    print(f"❌ Failed to convert: {file.filename} - {result.get('error', 'Unknown error')}")
                    results.append(result)
                
                # Don't delete temp file yet - we need it for the ZIP
                # temp_path.unlink(missing_ok=True)
                
            except Exception as e:
                error_msg = str(e)
                print(f"❌ Exception processing {file.filename}: {error_msg}")
                results.append({
                    "success": False,
                    "filename": file.filename,
                    "error": error_msg
                })
        
        print(f"🖼️ Image processing complete. {len([r for r in results if r.get('success')])} successful, {len([r for r in results if not r.get('success')])} failed")
        return results
    
    async def _convert_image_to_jpg(
        self, 
        input_path: Path, 
        output_path: Path, 
        quality: int, 
        compression: int
    ) -> Dict:
        """Convert any image format to JPG"""
        try:
            from PIL import Image
            
            # Open image
            with Image.open(input_path) as img:
                # Convert to RGB if necessary
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                
                # Get original image info
                original_size = os.path.getsize(input_path)
                original_dimensions = img.size
                
                # Create output directory if it doesn't exist
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Save as JPG with specified quality
                img.save(
                    output_path,
                    format="JPEG",
                    quality=quality,
                    optimize=True
                )
                
                # Get output file info
                output_size = os.path.getsize(output_path)
                compression_ratio = (1 - (output_size / original_size)) * 100
                
                return {
                    "success": True,
                    "input_path": str(input_path),
                    "output_path": str(output_path),
                    "original_size": original_size,
                    "output_size": output_size,
                    "compression_ratio": round(compression_ratio, 2),
                    "quality": quality,
                    "original_dimensions": original_dimensions,
                    "output_dimensions": img.size,
                    "format": "JPEG"
                }
                
        except Exception as e:
            return {
                "success": False,
                "input_path": str(input_path),
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    async def _process_pdf_files(
        self, 
        files: List[UploadFile], 
        output_dir: Path, 
        quality: int, 
        compression: int
    ) -> List[Dict]:
        """Process PDF files and return extraction results"""
        results = []
        
        for file in files:
            try:
                # Save uploaded file temporarily
                temp_path = output_dir / f"temp_{file.filename}"
                async with aiofiles.open(temp_path, 'wb') as f:
                    content = await file.read()
                    await f.write(content)
                
                # Extract images from PDF
                pdf_output_dir = output_dir / f"pdf_{file.stem}"
                result = await self.pdf_converter.extract_images_from_pdf(
                    temp_path, pdf_output_dir, quality, compression
                )
                
                if result['success']:
                    results.append(result)
                
                # Don't delete temp file yet - we need it for the ZIP
                # temp_path.unlink(missing_ok=True)
                
            except Exception as e:
                results.append({
                    "success": False,
                    "filename": file.filename,
                    "error": str(e)
                })
        
        return results
    
    async def _create_final_zip(
        self, 
        task_dir: Path, 
        task_id: str, 
        results: List[Dict]
    ) -> Path:
        """Create final ZIP file with all converted images"""
        zip_path = self.temp_dir / f"{task_id}.zip"
        
        print(f"🔍 Creating ZIP: {zip_path}")
        print(f"📊 Results to process: {len(results)}")
        print(f"📁 Task directory: {task_dir}")
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add all converted files
            for i, result in enumerate(results):
                print(f"📋 Processing result {i}: {result}")
                
                if result.get('success'):
                    print(f"✅ Success result found")
                    
                    if 'output_path' in result:
                        # HEIC/Image conversion result
                        file_path = Path(result['output_path'])
                        print(f"🖼️ Image file path: {file_path}")
                        print(f"📁 File exists: {file_path.exists()}")
                        
                        if file_path.exists():
                            zipf.write(file_path, file_path.name)
                            print(f"📦 Added to ZIP: {file_path.name}")
                        else:
                            print(f"❌ File not found: {file_path}")
                            
                    elif 'extracted_images' in result:
                        # PDF extraction result
                        print(f"📄 PDF extraction result with {len(result['extracted_images'])} images")
                        for img_info in result['extracted_images']:
                            img_path = Path(img_info['path'])
                            print(f"🖼️ PDF image path: {img_path}")
                            print(f"📁 Image exists: {img_path.exists()}")
                            
                            if img_path.exists():
                                zipf.write(img_path, img_info['filename'])
                                print(f"📦 Added to ZIP: {img_info['filename']}")
                            else:
                                print(f"❌ PDF image not found: {img_path}")
                    else:
                        print(f"⚠️ Unknown result structure: {result.keys()}")
                else:
                    print(f"❌ Failed result: {result}")
        
        # Verify ZIP contents
        zip_size = zip_path.stat().st_size
        print(f"📦 ZIP created: {zip_path} (size: {zip_size} bytes)")
        
        if zip_size < 100:  # Suspiciously small
            print(f"🚨 WARNING: ZIP is suspiciously small!")
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                file_list = zipf.namelist()
                print(f"📋 ZIP contents: {file_list}")
        
        return zip_path
    
    def _schedule_delayed_cleanup(self, task_dir: Path, task_id: str, delay_minutes: int = 5):
        """Schedule cleanup after specified delay to allow downloads"""
        def delayed_cleanup():
            delay_seconds = delay_minutes * 60
            print(f"⏰ Scheduling cleanup for task {task_id} in {delay_minutes} minutes...")
            time.sleep(delay_seconds)
            
            try:
                print(f"🧹 Starting delayed cleanup for task {task_id}...")
                
                # Remove temp files
                if task_dir.exists():
                    for temp_file in task_dir.glob("temp_*"):
                        temp_file.unlink(missing_ok=True)
                        print(f"🧹 Cleaned up temp file: {temp_file}")
                
                # Remove ZIP file
                zip_file = self.temp_dir / f"{task_id}.zip"
                if zip_file.exists():
                    zip_file.unlink(missing_ok=True)
                    print(f"🗑️ Cleaned up ZIP file: {zip_file}")
                
                # Remove task directory if empty
                if task_dir.exists() and not any(task_dir.iterdir()):
                    task_dir.rmdir()
                    print(f"📁 Removed empty task directory: {task_dir}")
                    
                print(f"✅ Delayed cleanup completed for task {task_id}")
                
            except Exception as e:
                print(f"❌ Error in delayed cleanup for task {task_id}: {e}")
        
        # Run cleanup in background thread
        cleanup_thread = threading.Thread(target=delayed_cleanup, daemon=True)
        cleanup_thread.start()
        print(f"⏰ Cleanup scheduled for task {task_id} (will execute in {delay_minutes} minutes)")

    async def _cleanup_temp_files(self, task_dir: Path):
        """Clean up temporary files after ZIP creation (DEPRECATED - use delayed cleanup)"""
        try:
            # Remove all temp_* files
            for temp_file in task_dir.glob("temp_*"):
                temp_file.unlink(missing_ok=True)
                print(f"🧹 Cleaned up temp file: {temp_file}")
        except Exception as e:
            print(f"Error cleaning up temp files: {e}")
    
    async def cleanup_task(self, task_id: str):
        """Clean up temporary files for a task"""
        try:
            task_dir = self.temp_dir / task_id
            if task_dir.exists():
                shutil.rmtree(task_dir)
            
            zip_file = self.temp_dir / f"{task_id}.zip"
            if zip_file.exists():
                zip_file.unlink()
                
        except Exception as e:
            print(f"Error cleaning up task {task_id}: {e}")
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get status of a processing task"""
        task_dir = self.temp_dir / task_id
        zip_file = self.temp_dir / f"{task_id}.zip"
        
        return {
            "task_id": task_id,
            "exists": task_dir.exists(),
            "zip_ready": zip_file.exists(),
            "zip_size": zip_file.stat().st_size if zip_file.exists() else 0
        }
