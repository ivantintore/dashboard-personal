import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import fitz  # PyMuPDF

from app.core.converters.pdf_converter import PDFConverter


class TestPDFConverter:
    """Test cases for PDFConverter class"""
    
    @pytest.fixture
    def converter(self):
        """Create a converter instance for testing"""
        return PDFConverter()
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test files"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    @pytest.fixture
    def sample_pdf(self, temp_dir):
        """Create a sample test PDF"""
        pdf_path = temp_dir / "test.pdf"
        pdf_path.touch()
        return pdf_path
    
    def test_init(self, converter):
        """Test converter initialization"""
        assert converter.output_format == "JPEG"
        assert converter.output_extension == ".jpg"
        assert converter.max_pages == 100
        assert converter.max_images_per_page == 10
        assert converter.default_quality == 85
    
    def test_get_supported_formats(self, converter):
        """Test supported formats list"""
        formats = converter.get_supported_formats()
        assert ".pdf" in formats
        assert len(formats) == 1
    
    def test_validate_input_file_valid(self, converter, sample_pdf):
        """Test validation of valid input file"""
        # Mock PyMuPDF operations
        with patch('fitz.open') as mock_open:
            mock_doc = MagicMock()
            mock_doc.__len__ = MagicMock(return_value=5)  # 5 pages
            mock_open.return_value.__enter__.return_value = mock_doc
            
            result = converter.validate_input_file(sample_pdf)
            assert result is True
    
    def test_validate_input_file_nonexistent(self, converter, temp_dir):
        """Test validation of nonexistent file"""
        nonexistent_file = temp_dir / "nonexistent.pdf"
        result = converter.validate_input_file(nonexistent_file)
        assert result is False
    
    def test_validate_input_file_wrong_extension(self, converter, temp_dir):
        """Test validation of file with wrong extension"""
        wrong_file = temp_dir / "test.txt"
        wrong_file.touch()
        result = converter.validate_input_file(wrong_file)
        assert result is False
    
    def test_generate_page_image_filename(self, converter, temp_dir):
        """Test filename generation for extracted images"""
        output_dir = temp_dir / "output"
        
        # Test first image on page 1
        filename = converter._generate_page_image_filename(1, 0, output_dir)
        assert filename.name == "page_1a.jpg"
        
        # Test second image on page 1
        filename = converter._generate_page_image_filename(1, 1, output_dir)
        assert filename.name == "page_1b.jpg"
        
        # Test first image on page 5
        filename = converter._generate_page_image_filename(5, 0, output_dir)
        assert filename.name == "page_5a.jpg"
    
    @pytest.mark.asyncio
    async def test_extract_images_from_pdf_success(self, converter, sample_pdf, temp_dir):
        """Test successful PDF image extraction"""
        output_dir = temp_dir / "output"
        
        # Mock PyMuPDF operations
        with patch('fitz.open') as mock_open:
            # Create mock PDF document
            mock_doc = MagicMock()
            mock_doc.__len__ = MagicMock(return_value=2)  # 2 pages
            
            # Create mock pages
            mock_page1 = MagicMock()
            mock_page1.get_images.return_value = [
                (1, 0, 0, 100, 100),  # xref, x0, y0, x1, y1
                (2, 0, 0, 200, 200)
            ]
            
            mock_page2 = MagicMock()
            mock_page2.get_images.return_value = [
                (3, 0, 0, 150, 150)
            ]
            
            mock_doc.__getitem__.side_effect = [mock_page1, mock_page2]
            
            # Mock image extraction
            mock_doc.extract_image.side_effect = [
                {"image": b"fake_image_data_1"},
                {"image": b"fake_image_data_2"},
                {"image": b"fake_image_data_3"}
            ]
            
            # Mock the context manager properly
            mock_open.return_value = mock_doc
            
            # Mock the page.parent.extract_image method
            mock_page1.parent = mock_doc
            mock_page2.parent = mock_doc
            
            # Mock PIL operations
            with patch('PIL.Image.open') as mock_pil_open:
                mock_img = MagicMock()
                mock_img.mode = 'RGB'
                mock_img.size = (100, 100)
                mock_img.save = MagicMock()
                mock_pil_open.return_value = mock_img
                
                # Mock file size
                with patch('os.path.getsize') as mock_size:
                    mock_size.return_value = 1024
                    
                    result = await converter.extract_images_from_pdf(
                        sample_pdf, 
                        output_dir, 
                        quality=90
                    )
                    
                    assert result['success'] is True
                    assert result['pdf_path'] == str(sample_pdf)
                    assert result['total_pages'] == 2
                    assert result['total_images'] == 3
                    assert result['quality'] == 90
                    assert len(result['extracted_images']) == 3
    
    @pytest.mark.asyncio
    async def test_extract_images_from_pdf_too_large(self, converter, sample_pdf, temp_dir):
        """Test PDF with too many pages"""
        output_dir = temp_dir / "output"
        
        with patch('fitz.open') as mock_open:
            mock_doc = MagicMock()
            mock_doc.__len__ = MagicMock(return_value=150)  # Exceeds limit
            mock_open.return_value = mock_doc
            
            result = await converter.extract_images_from_pdf(
                sample_pdf, 
                output_dir, 
                quality=85
            )
            
            assert result['success'] is False
            assert "demasiado grande" in result['error']
    
    @pytest.mark.asyncio
    async def test_extract_images_from_pdf_no_images(self, converter, sample_pdf, temp_dir):
        """Test PDF with no images"""
        output_dir = temp_dir / "output"
        
        with patch('fitz.open') as mock_open:
            mock_doc = MagicMock()
            mock_doc.__len__ = MagicMock(return_value=1)
            
            mock_page = MagicMock()
            mock_page.get_images.return_value = []  # No images
            
            mock_doc.__getitem__.return_value = mock_page
            mock_open.return_value = mock_doc
            
            result = await converter.extract_images_from_pdf(
                sample_pdf, 
                output_dir, 
                quality=85
            )
            
            assert result['success'] is True
            assert result['total_images'] == 0
            assert len(result['extracted_images']) == 0
    
    @pytest.mark.asyncio
    async def test_extract_images_from_pdf_error_handling(self, converter, sample_pdf, temp_dir):
        """Test error handling during PDF processing"""
        output_dir = temp_dir / "output"
        
        with patch('fitz.open') as mock_open:
            # Simulate an error during PDF processing
            mock_open.side_effect = Exception("Test PDF error")
            
            result = await converter.extract_images_from_pdf(
                sample_pdf, 
                output_dir, 
                quality=85
            )
            
            assert result['success'] is False
            assert 'error' in result
            assert result['error'] == "Test PDF error"
            assert result['error_type'] == "Exception"
    
    @pytest.mark.asyncio
    async def test_create_zip_file(self, converter, temp_dir):
        """Test ZIP file creation"""
        output_dir = temp_dir / "output"
        output_dir.mkdir()
        
        # Create dummy image files
        image1 = output_dir / "page_1a.jpg"
        image2 = output_dir / "output_dir" / "page_2a.jpg"
        image2.parent.mkdir()
        
        image1.touch()
        image2.touch()
        
        # Mock image info
        images = [
            {"path": str(image1), "filename": "page_1a.jpg"},
            {"path": str(image2), "filename": "page_2a.jpg"}
        ]
        
        zip_path = await converter._create_zip_file(images, output_dir, "test_pdf")
        
        assert zip_path.exists()
        assert zip_path.name == "test_pdf_extracted_images.zip"
        
        # Verify ZIP contents
        import zipfile
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            file_list = zipf.namelist()
            assert "page_1a.jpg" in file_list
            assert "page_2a.jpg" in file_list


if __name__ == "__main__":
    pytest.main([__file__])
