import os
import shutil
import tempfile
from pathlib import Path
from typing import Optional, List
import mimetypes


def create_temp_dir(prefix: str = "converter_") -> Path:
    """
    Create a temporary directory for file processing
    
    Args:
        prefix: Prefix for the temporary directory name
        
    Returns:
        Path to created temporary directory
    """
    temp_dir = Path(tempfile.mkdtemp(prefix=prefix))
    return temp_dir


def cleanup_temp_dir(temp_dir: Path):
    """
    Clean up temporary directory and all its contents
    
    Args:
        temp_dir: Path to temporary directory to clean up
    """
    try:
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
    except Exception as e:
        print(f"Error cleaning up temp directory {temp_dir}: {e}")


def get_file_size(file_path: Path) -> int:
    """
    Get file size in bytes
    
    Args:
        file_path: Path to file
        
    Returns:
        File size in bytes
    """
    try:
        return file_path.stat().st_size
    except OSError:
        return 0


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string (e.g., "1.5 MB")
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def get_file_mime_type(file_path: Path) -> Optional[str]:
    """
    Get MIME type of a file
    
    Args:
        file_path: Path to file
        
    Returns:
        MIME type string or None if cannot determine
    """
    try:
        mime_type, _ = mimetypes.guess_type(str(file_path))
        return mime_type
    except Exception:
        return None


def is_image_file(file_path: Path) -> bool:
    """
    Check if file is an image based on extension and MIME type
    
    Args:
        file_path: Path to file
        
    Returns:
        True if file is an image
    """
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.heic', '.heif'}
    image_mime_types = {'image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/tiff', 'image/webp', 'image/heic', 'image/heif'}
    
    # Check extension
    if file_path.suffix.lower() in image_extensions:
        return True
    
    # Check MIME type
    mime_type = get_file_mime_type(file_path)
    if mime_type in image_mime_types:
        return True
    
    return False


def is_pdf_file(file_path: Path) -> bool:
    """
    Check if file is a PDF
    
    Args:
        file_path: Path to file
        
    Returns:
        True if file is a PDF
    """
    return file_path.suffix.lower() == '.pdf' or get_file_mime_type(file_path) == 'application/pdf'


def get_safe_filename(filename: str) -> str:
    """
    Convert filename to safe version by removing/replacing dangerous characters
    
    Args:
        filename: Original filename
        
    Returns:
        Safe filename
    """
    # Remove or replace dangerous characters
    dangerous_chars = '<>:"/\\|?*'
    safe_filename = filename
    
    for char in dangerous_chars:
        safe_filename = safe_filename.replace(char, '_')
    
    # Remove multiple underscores
    while '__' in safe_filename:
        safe_filename = safe_filename.replace('__', '_')
    
    # Remove leading/trailing underscores
    safe_filename = safe_filename.strip('_')
    
    return safe_filename


def create_unique_filename(base_path: Path, filename: str) -> Path:
    """
    Create unique filename to avoid conflicts
    
    Args:
        base_path: Base directory path
        filename: Desired filename
        
    Returns:
        Path to unique filename
    """
    counter = 1
    name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
    
    while True:
        if counter == 1:
            new_filename = filename
        else:
            new_filename = f"{name}_{counter}.{ext}" if ext else f"{name}_{counter}"
        
        new_path = base_path / new_filename
        if not new_path.exists():
            return new_path
        
        counter += 1


def list_files_in_directory(directory: Path, extensions: Optional[List[str]] = None) -> List[Path]:
    """
    List all files in directory with optional extension filter
    
    Args:
        directory: Directory to list files from
        extensions: List of allowed extensions (e.g., ['.jpg', '.png'])
        
    Returns:
        List of file paths
    """
    if not directory.exists() or not directory.is_dir():
        return []
    
    files = []
    for item in directory.iterdir():
        if item.is_file():
            if extensions is None or item.suffix.lower() in extensions:
                files.append(item)
    
    return sorted(files)

