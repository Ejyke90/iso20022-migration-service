"""
Word to PDF Converter Class
Supports .docx, .doc files using aspose-words (works on Linux/Railway)
"""
import os
from pathlib import Path

try:
    import aspose.words as aw
    ASPOSE_AVAILABLE = True
except ImportError:
    ASPOSE_AVAILABLE = False
    print("Warning: aspose-words not available")

class WordToPDFConverter:
    """Word to PDF converter using Aspose.Words"""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.supported_formats = ['.docx', '.doc']
        
        if not ASPOSE_AVAILABLE:
            raise ImportError("aspose-words is required but not installed")
    
    def convert(self, input_path: str, output_path: str) -> bool:
        """
        Convert a Word document to PDF
        
        Args:
            input_path: Path to input .docx or .doc file
            output_path: Path for output .pdf file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            input_path = Path(input_path)
            output_path = Path(output_path)
            
            if not input_path.exists():
                raise FileNotFoundError(f"Input file not found: {input_path}")
            
            # Validate file format
            if input_path.suffix.lower() not in self.supported_formats:
                raise ValueError(f"Unsupported format: {input_path.suffix}. Supported: {', '.join(self.supported_formats)}")
            
            # Validate file size (50MB max)
            file_size = input_path.stat().st_size
            if file_size > 50 * 1024 * 1024:
                raise ValueError("File too large. Maximum size is 50MB")
            
            if file_size == 0:
                raise ValueError("File is empty")
            
            # Load the document from the absolute path
            doc = aw.Document(str(input_path.absolute()))
            
            # Save as PDF
            doc.save(str(output_path.absolute()))
            
            return output_path.exists()
            
        except Exception as e:
            print(f"Conversion error: {e}")
            return False
    
    def validate_file(self, file_path: str) -> tuple[bool, str]:
        """
        Validate if file can be converted
        
        Args:
            file_path: Path to file to validate
            
        Returns:
            tuple: (is_valid, message)
        """
        try:
            path = Path(file_path)
            
            if not path.exists():
                return False, "File does not exist"
            
            if path.suffix.lower() not in self.supported_formats:
                return False, f"Unsupported format: {path.suffix}. Supported: {', '.join(self.supported_formats)}"
            
            file_size = path.stat().st_size
            if file_size == 0:
                return False, "File is empty"
            
            if file_size > 50 * 1024 * 1024:
                return False, "File too large (max 50MB)"
            
            return True, "Valid"
            
        except Exception as e:
            return False, str(e)
    
    def batch_convert(self, input_files: list, output_dir: str) -> dict:
        """
        Convert multiple files
        
        Args:
            input_files: List of input file paths
            output_dir: Output directory
            
        Returns:
            dict: Results with success/failure counts
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        results = {'total': len(input_files), 'success': 0, 'failed': 0, 'errors': []}
        
        for input_file in input_files:
            input_path = Path(input_file)
            output_file = output_dir / f"{input_path.stem}.pdf"
            
            # Validate first
            is_valid, message = self.validate_file(input_file)
            if not is_valid:
                results['failed'] += 1
                results['errors'].append(f"{input_file}: {message}")
                continue
            
            # Convert
            if self.convert(str(input_file), str(output_file)):
                results['success'] += 1
            else:
                results['failed'] += 1
                results['errors'].append(f"{input_file}: Conversion failed")
        
        return results
