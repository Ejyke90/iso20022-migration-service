"""
Word to PDF Converter Class
Standalone converter using aspose-words (works on Linux/Railway)
"""
import aspose.words as aw
import os

class WordToPDFConverter:
    """Word to PDF converter using Aspose.Words"""
    
    def __init__(self, config=None):
        self.config = config or {}
    
    def convert(self, input_path: str, output_path: str) -> bool:
        """
        Convert a Word document to PDF
        
        Args:
            input_path: Path to input .docx file
            output_path: Path for output .pdf file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not os.path.exists(input_path):
                raise FileNotFoundError(f"Input file not found: {input_path}")
            
            # Load the document from the absolute path
            doc = aw.Document(input_path)
            
            # Save as PDF
            doc.save(output_path)
            
            return os.path.exists(output_path)
        except Exception as e:
            print(f"Conversion error: {e}")
            return False
    
    def batch_convert(self, input_files: list, output_dir: str) -> dict:
        """
        Convert multiple files
        
        Args:
            input_files: List of input file paths
            output_dir: Output directory
            
        Returns:
            dict: Results with success/failure counts
        """
        os.makedirs(output_dir, exist_ok=True)
        
        results = {'total': len(input_files), 'success': 0, 'failed': 0}
        
        for input_file in input_files:
            output_file = os.path.join(
                output_dir,
                os.path.splitext(os.path.basename(input_file))[0] + '.pdf'
            )
            
            if self.convert(input_file, output_file):
                results['success'] += 1
            else:
                results['failed'] += 1
        
        return results
