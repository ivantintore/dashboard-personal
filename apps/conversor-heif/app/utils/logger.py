import logging
import os
from pathlib import Path
from datetime import datetime
import sys


class Logger:
    """Centralized logging system for the application"""
    
    _instance = None
    _logger = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance._setup_logger()
        return cls._instance
    
    def _setup_logger(self):
        """Setup logger with both file and console output"""
        # Create logs directory
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        # Create logger
        self._logger = logging.getLogger("conversor")
        self._logger.setLevel(logging.DEBUG)
        
        # Clear existing handlers
        self._logger.handlers.clear()
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(filename)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # File handler - detailed logs
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = logs_dir / f"conversor_{today}.log"
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        self._logger.addHandler(file_handler)
        
        # Console handler - simpler logs
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        self._logger.addHandler(console_handler)
        
        # Log startup
        self._logger.info("="*60)
        self._logger.info("🚀 CONVERSOR HEIC + PDF a JPG - LOGGING STARTED")
        self._logger.info(f"📂 Log file: {log_file}")
        self._logger.info("="*60)
    
    def debug(self, message):
        """Log debug message"""
        self._logger.debug(f"🔍 {message}")
    
    def info(self, message):
        """Log info message"""
        self._logger.info(f"ℹ️  {message}")
    
    def warning(self, message):
        """Log warning message"""
        self._logger.warning(f"⚠️  {message}")
    
    def error(self, message):
        """Log error message"""
        self._logger.error(f"❌ {message}")
    
    def critical(self, message):
        """Log critical message"""
        self._logger.critical(f"🚨 {message}")
    
    def api_request(self, method, endpoint, status_code=None, duration=None):
        """Log API request"""
        if status_code and duration:
            self._logger.info(f"🌐 {method} {endpoint} -> {status_code} ({duration:.2f}ms)")
        else:
            self._logger.info(f"🌐 {method} {endpoint}")
    
    def file_operation(self, operation, file_path, success=True, details=None):
        """Log file operation"""
        status = "✅" if success else "❌"
        message = f"📁 {status} {operation}: {file_path}"
        if details:
            message += f" ({details})"
        
        if success:
            self._logger.info(message)
        else:
            self._logger.error(message)
    
    def conversion_start(self, task_id, files_count, file_types):
        """Log conversion start"""
        self._logger.info(f"🔄 CONVERSION START - Task: {task_id}")
        self._logger.info(f"   📊 Files: {files_count} | Types: {file_types}")
    
    def conversion_end(self, task_id, success_count, total_count, duration=None):
        """Log conversion end"""
        duration_str = f" in {duration:.2f}s" if duration else ""
        self._logger.info(f"🏁 CONVERSION END - Task: {task_id}")
        self._logger.info(f"   📊 Success: {success_count}/{total_count}{duration_str}")
    
    def zip_creation(self, task_id, zip_path, file_count, size_bytes):
        """Log ZIP creation"""
        size_mb = size_bytes / (1024 * 1024)
        self._logger.info(f"📦 ZIP CREATED - Task: {task_id}")
        self._logger.info(f"   📂 Path: {zip_path}")
        self._logger.info(f"   📊 Files: {file_count} | Size: {size_mb:.2f}MB")
    
    def exception(self, exception, context=""):
        """Log exception with full traceback"""
        import traceback
        context_str = f" in {context}" if context else ""
        self._logger.error(f"💥 EXCEPTION{context_str}: {type(exception).__name__} - {str(exception)}")
        self._logger.debug(f"🔍 Full traceback:\n{traceback.format_exc()}")


# Global logger instance
logger = Logger()
