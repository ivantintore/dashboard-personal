import os
import fitz  # PyMuPDF
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from PIL import Image
import io
from config.settings import settings


class PDFConverter:
    """Extracts images from PDF files and converts them to JPG format"""
    
    def __init__(self):
        self.output_format = settings.output_format
        self.output_extension = settings.output_extension
        self.max_pages = settings.max_pdf_pages
        self.max_images_per_page = settings.max_images_per_page
        self.default_quality = settings.default_quality
    
    async def extract_images_from_pdf(
        self, 
        pdf_path: Path, 
        output_dir: Path,
        quality: int = None,
        compression: int = None
    ) -> dict:
        """
        Extract all images from a PDF file and convert to JPG
        
        Args:
            pdf_path: Path to input PDF file
            output_dir: Directory for output images
            quality: JPG quality (1-100)
            compression: Compression level (1-100)
            
        Returns:
            dict: Extraction and conversion results
        """
        try:
            # Set quality
            final_quality = quality or compression or self.default_quality
            final_quality = max(1, min(100, final_quality))
            
            # Open PDF
            pdf_document = fitz.open(pdf_path)
            total_pages = len(pdf_document)
            
            if total_pages > self.max_pages:
                pdf_document.close()
                return {
                    "success": False,
                    "error": f"PDF demasiado grande: {total_pages} páginas (máximo: {self.max_pages})"
                }
            
            extracted_images = []
            total_images = 0
            
            # Process each page
            for page_num in range(total_pages):
                page = pdf_document[page_num]
                page_images = await self._extract_images_from_page(
                    page, page_num, output_dir, final_quality
                )
                
                if page_images:
                    extracted_images.extend(page_images)
                    total_images += len(page_images)
                
                # Check limit per page
                if len(page_images) > self.max_images_per_page:
                    break
            
            pdf_document.close()
            
            # Create ZIP file if multiple images
            zip_path = None
            if len(extracted_images) > 1:
                zip_path = await self._create_zip_file(extracted_images, output_dir, pdf_path.stem)
            
            return {
                "success": True,
                "pdf_path": str(pdf_path),
                "total_pages": total_pages,
                "total_images": total_images,
                "extracted_images": extracted_images,
                "zip_path": str(zip_path) if zip_path else None,
                "quality": final_quality
            }
            
        except Exception as e:
            return {
                "success": False,
                "pdf_path": str(pdf_path),
                "error": str(e),
                "error_type": type(e).__name__
            }
    
    async def _extract_images_from_page(
        self, 
        page, 
        page_num: int, 
        output_dir: Path, 
        quality: int
    ) -> List[Dict]:
        """
        Extract images from a single PDF page
        
        Args:
            page: PDF page object
            page_num: Page number (0-indexed)
            output_dir: Output directory
            quality: JPG quality
            
        Returns:
            List of extracted image information
        """
        images = []
        
        # Get image list from page
        image_list = page.get_images()
        
        for img_index, img in enumerate(image_list):
            try:
                # Get image data
                xref = img[0]
                base_image = page.parent.extract_image(xref)
                image_bytes = base_image["image"]
                
                # Convert to PIL Image
                pil_image = Image.open(io.BytesIO(image_bytes))
                
                # Convert to RGB if necessary
                if pil_image.mode in ('RGBA', 'LA', 'P'):
                    pil_image = pil_image.convert('RGB')
                
                # Generate filename with page number and image index
                filename = self._generate_page_image_filename(
                    page_num + 1, img_index, output_dir
                )
                
                # Save as JPG
                pil_image.save(
                    filename,
                    format=self.output_format,
                    quality=quality,
                    optimize=True
                )
                
                # Get file info
                file_size = os.path.getsize(filename)
                
                images.append({
                    "filename": filename.name,
                    "path": str(filename),
                    "page": page_num + 1,
                    "image_index": img_index,
                    "dimensions": pil_image.size,
                    "size": file_size,
                    "format": self.output_format,
                    "quality": quality
                })
                
            except Exception as e:
                # Log error but continue with other images
                print(f"Error extracting image {img_index} from page {page_num}: {e}")
                continue
        
        return images
    
    def _generate_page_image_filename(
        self, 
        page_num: int, 
        img_index: int, 
        output_dir: Path
    ) -> Path:
        """
        Generate filename for extracted image
        
        Args:
            page_num: Page number (1-indexed)
            img_index: Image index on the page
            output_dir: Output directory
            
        Returns:
            Path to output file
        """
        # Create output directory if it doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename: page_1a, page_1b, page_1c, etc.
        suffix = chr(97 + img_index)  # a, b, c, d...
        filename = f"page_{page_num}{suffix}{self.output_extension}"
        
        return output_dir / filename
    
    async def _create_zip_file(
        self, 
        images: List[Dict], 
        output_dir: Path, 
        pdf_name: str
    ) -> Path:
        """
        Create ZIP file containing all extracted images
        
        Args:
            images: List of image information
            output_dir: Output directory
            pdf_name: Original PDF name
            
        Returns:
            Path to created ZIP file
        """
        import zipfile
        
        zip_filename = f"{pdf_name}_extracted_images.zip"
        zip_path = output_dir / zip_filename
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for img_info in images:
                img_path = Path(img_info['path'])
                if img_path.exists():
                    # Add to ZIP with relative path
                    zipf.write(img_path, img_path.name)
        
        return zip_path
    
    def get_supported_formats(self) -> list:
        """Get list of supported input formats"""
        return ['.pdf']
    
    def validate_input_file(self, file_path: Path) -> bool:
        """Validate if input file is a valid PDF"""
        if not file_path.exists():
            return False
        
        # Check file extension
        if file_path.suffix.lower() != '.pdf':
            return False
        
        # Check if file is readable PDF
        try:
            with fitz.open(file_path) as doc:
                return len(doc) > 0
        except:
            return False
