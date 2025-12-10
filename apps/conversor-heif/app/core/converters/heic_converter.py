import os
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image
import pillow_heif
from config.settings import settings
from app.utils.logger import logger


class HEICConverter:
    """Converts HEIC/HEIF images to JPG format with quality control"""
    
    def __init__(self):
        self.output_format = settings.output_format
        self.output_extension = settings.output_extension
        self.default_quality = settings.default_quality
        # Register HEIF opener with Pillow immediately
        try:
            pillow_heif.register_heif_opener()
        except Exception:
            pass  # Already registered or not available
    
    async def convert_file(
        self, 
        input_path: Path, 
        output_path: Path, 
        quality: int = None,
        compression: int = None
    ) -> dict:
        """
        Convert a HEIC/HEIF file to JPG
        
        Args:
            input_path: Path to input HEIC/HEIF file
            output_path: Path for output JPG file
            quality: JPG quality (1-100)
            compression: Compression level (1-100)
            
        Returns:
            dict: Conversion result with metadata
        """
        try:
            logger.debug(f"🔄 HEICConverter: Starting conversion of {input_path} to {output_path}")
            
            # Set quality (use compression if quality not specified)
            final_quality = quality or compression or self.default_quality
            final_quality = max(1, min(100, final_quality))
            logger.debug(f"🎛️ Using quality: {final_quality}")
            
            # Check if input file exists
            if not input_path.exists():
                raise FileNotFoundError(f"Input file not found: {input_path}")
            
            logger.debug(f"📁 Input file size: {os.path.getsize(input_path)} bytes")
            
            # Ensure HEIF opener is registered
            try:
                pillow_heif.register_heif_opener()
                logger.debug("✅ pillow_heif registered successfully")
            except Exception as e:
                logger.warning(f"⚠️ Failed to register pillow_heif: {e}")
            
            # Try to open with pillow_heif first
            img = None
            try:
                logger.debug("🔍 Attempting to open with pillow_heif...")
                heif_file = pillow_heif.read_heif(str(input_path))
                img = heif_file.to_pillow()
                logger.debug(f"✅ Opened with pillow_heif: {img.size} {img.mode}")
            except Exception as e:
                logger.debug(f"⚠️ pillow_heif failed: {e}, trying PIL fallback...")
                # Fallback to regular PIL
                try:
                    with Image.open(input_path) as pil_img:
                        img = pil_img.copy()
                    logger.debug(f"✅ Opened with PIL: {img.size} {img.mode}")
                except Exception as pil_e:
                    raise Exception(f"Failed to open with both pillow_heif and PIL: pillow_heif={e}, PIL={pil_e}")
            
            # Convert to RGB if necessary (JPG doesn't support RGBA)
            if img.mode in ('RGBA', 'LA', 'P'):
                logger.debug(f"🎨 Converting from {img.mode} to RGB")
                img = img.convert('RGB')
            
            # Get original image info
            original_size = os.path.getsize(input_path)
            original_dimensions = img.size
            logger.debug(f"📊 Original: {original_dimensions} ({original_size} bytes)")
            
            # Create output directory if it doesn't exist
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save as JPG with specified quality
            logger.debug(f"💾 Saving as {self.output_format} with quality {final_quality}")
            img.save(
                output_path,
                format=self.output_format,
                quality=final_quality,
                optimize=True
            )
            
            # Get output file info
            output_size = os.path.getsize(output_path)
            compression_ratio = (1 - (output_size / original_size)) * 100
            
            logger.info(f"✅ HEIC conversion successful: {input_path.name} -> {output_path.name} ({original_size} -> {output_size} bytes)")
            
            return {
                "success": True,
                "input_path": str(input_path),
                "output_path": str(output_path),
                "original_size": original_size,
                "output_size": output_size,
                "compression_ratio": round(compression_ratio, 2),
                "quality": final_quality,
                "original_dimensions": original_dimensions,
                "output_dimensions": img.size,
                "format": self.output_format
            }
            
        except Exception as e:
            logger.error(f"❌ HEIC conversion failed for {input_path}: {type(e).__name__} - {str(e)}")
            return {
                "success": False,
                "input_path": str(input_path),
                "error": str(e),
                "error_type": type(e).__name__,
                "quality": final_quality if 'final_quality' in locals() else 'unknown'
            }
    
    async def convert_multiple_files(
        self, 
        input_files: list, 
        output_dir: Path, 
        quality: int = None,
        compression: int = None
    ) -> list:
        """
        Convert multiple HEIC/HEIF files to JPG
        
        Args:
            input_files: List of input file paths
            output_dir: Directory for output files
            quality: JPG quality (1-100)
            compression: Compression level (1-100)
            
        Returns:
            list: List of conversion results
        """
        results = []
        
        for input_file in input_files:
            # Generate output filename
            output_filename = self._generate_output_filename(input_file)
            output_path = output_dir / output_filename
            
            # Convert file
            result = await self.convert_file(
                input_file, 
                output_path, 
                quality, 
                compression
            )
            
            results.append(result)
        
        return results
    
    def _generate_output_filename(self, input_path: Path) -> str:
        """Generate output filename with JPG extension"""
        stem = input_path.stem
        return f"{stem}{self.output_extension}"
    
    def get_supported_formats(self) -> list:
        """Get list of supported input formats"""
        return ['.heic', '.heif']
    
    def validate_input_file(self, file_path: Path) -> bool:
        """Validate if input file is supported HEIC/HEIF"""
        if not file_path.exists():
            return False
        
        # Check file extension
        if file_path.suffix.lower() not in self.get_supported_formats():
            return False
        
        # Check if file is readable
        try:
            # Try to open with pillow_heif
            heif_file = pillow_heif.read_heif(str(file_path))
            return True
        except:
            try:
                # Fallback to PIL
                with Image.open(file_path) as img:
                    return True
            except:
                return False
