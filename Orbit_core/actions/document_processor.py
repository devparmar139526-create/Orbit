"""
Document Processing & Organization
Phase 3: Summarization, Organization, CSV/Excel Processing
"""

from typing import List, Dict, Optional, Any
from pathlib import Path
from datetime import datetime
import json
import shutil

class DocumentProcessor:
    def __init__(self, settings=None):
        self.settings = settings
        
        # Configuration
        self.enable_doc_organization = getattr(settings, 'ENABLE_DOC_ORGANIZATION', True) if settings else True
        self.enable_doc_summarization = getattr(settings, 'ENABLE_DOC_SUMMARIZATION', True) if settings else True
        self.enable_csv_processing = getattr(settings, 'ENABLE_CSV_PROCESSING', True) if settings else True
        self.enable_report_generation = getattr(settings, 'ENABLE_REPORT_GENERATION', True) if settings else True
        
        # Allowed directories (security)
        if settings and hasattr(settings, 'ALLOWED_DIRECTORIES'):
            self.allowed_dirs = [Path(d).expanduser() for d in settings.ALLOWED_DIRECTORIES]
        else:
            self.allowed_dirs = [
                Path.home() / "Documents",
                Path.home() / "Downloads"
            ]
        
        # Document organization categories
        if settings and hasattr(settings, 'DOC_CATEGORIES'):
            self.doc_categories = settings.DOC_CATEGORIES
        else:
            self.doc_categories = {
                'PDF': ['.pdf'],
                'Word': ['.doc', '.docx', '.odt'],
                'Excel': ['.xls', '.xlsx', '.csv'],
                'Text': ['.txt', '.md', '.rtf'],
                'Presentations': ['.ppt', '.pptx'],
                'Images': ['.jpg', '.png', '.gif', '.svg']
            }
        
        # Summary settings
        self.summary_max_length = getattr(settings, 'SUMMARY_MAX_LENGTH', 500) if settings else 500
        self.summary_sentences = getattr(settings, 'SUMMARY_SENTENCES', 5) if settings else 5
        
        # Last accessed file for voice commands
        self.last_summarized_file = None
    
    def _is_path_allowed(self, path: Path) -> bool:
        """Check if path is in allowed directories"""
        try:
            path = path.resolve()
            return any(path.is_relative_to(allowed) for allowed in self.allowed_dirs)
        except:
            return False
    
    def find_file_by_name(self, filename: str, file_type: Optional[str] = None) -> Optional[Path]:
        """
        Smart file finder - searches Downloads and Documents for files
        
        Args:
            filename: Partial or full filename (e.g., "report", "mind lab")
            file_type: Optional file type filter (e.g., "pdf", "txt", "csv")
        
        Returns:
            Path to found file or None
        """
        filename_lower = filename.lower()
        search_dirs = [
            Path.home() / "Downloads",
            Path.home() / "Downloads" / "Documents",
            Path.home() / "Documents",
            Path.home() / "Desktop"
        ]
        
        candidates = []
        
        for search_dir in search_dirs:
            if not search_dir.exists():
                continue
            
            try:
                # Search recursively (up to 2 levels deep)
                for depth in [0, 1, 2]:
                    if depth == 0:
                        files = search_dir.glob("*")
                    elif depth == 1:
                        files = search_dir.glob("*/*")
                    else:
                        files = search_dir.glob("*/*/*")
                    
                    for file in files:
                        if not file.is_file():
                            continue
                        
                        # Check file type filter
                        if file_type and not file.suffix.lower().endswith(file_type.lower()):
                            continue
                        
                        # Check if filename matches
                        if filename_lower in file.name.lower():
                            candidates.append(file)
            except PermissionError:
                continue
        
        if not candidates:
            return None
        
        # Return most recently modified file
        candidates.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        return candidates[0]
    
    def get_recent_files(self, file_type: Optional[str] = None, limit: int = 5) -> List[Path]:
        """
        Get recently modified files from common directories
        
        Args:
            file_type: Optional file type filter (e.g., "pdf", "txt")
            limit: Maximum number of files to return
        
        Returns:
            List of file paths
        """
        search_dirs = [
            Path.home() / "Downloads",
            Path.home() / "Documents",
            Path.home() / "Desktop"
        ]
        
        files = []
        
        for search_dir in search_dirs:
            if not search_dir.exists():
                continue
            
            try:
                for file in search_dir.rglob("*"):
                    if not file.is_file():
                        continue
                    
                    # Check file type
                    if file_type:
                        if not file.suffix.lower().endswith(file_type.lower()):
                            continue
                    else:
                        # Only include common document types
                        if file.suffix.lower() not in ['.pdf', '.txt', '.doc', '.docx', '.csv', '.xlsx']:
                            continue
                    
                    files.append(file)
            except PermissionError:
                continue
        
        # Sort by modification time (newest first)
        files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        
        return files[:limit]
    
    def organize_documents_by_type(self, directory: Optional[str] = None) -> Dict:
        """
        Organize documents by type into categorized folders
        
        Args:
            directory: Directory to organize (default: Downloads)
        
        Returns:
            Dict with organization results
        """
        if not self.enable_doc_organization:
            return {'error': 'Document organization is disabled'}
        
        try:
            # Default to Downloads folder
            target_dir = Path(directory).expanduser() if directory else Path.home() / "Downloads"
            
            if not self._is_path_allowed(target_dir):
                return {'error': 'Access denied: Directory not in allowed list'}
            
            if not target_dir.exists():
                return {'error': f'Directory not found: {target_dir}'}
            
            organized_count = 0
            results = {}
            
            for file in target_dir.iterdir():
                if file.is_file():
                    ext = file.suffix.lower()
                    
                    # Find category for this file type
                    for category, extensions in self.doc_categories.items():
                        if ext in extensions:
                            # Create category folder
                            category_folder = target_dir / category
                            category_folder.mkdir(exist_ok=True)
                            
                            # Move file
                            try:
                                dest = category_folder / file.name
                                # Handle name conflicts
                                if dest.exists():
                                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                                    dest = category_folder / f"{file.stem}_{timestamp}{file.suffix}"
                                
                                shutil.move(str(file), str(dest))
                                organized_count += 1
                                results[category] = results.get(category, 0) + 1
                            except Exception as e:
                                print(f"Error moving {file.name}: {e}")
                            
                            break
            
            return {
                'status': 'success',
                'organized_count': organized_count,
                'categories': results,
                'directory': str(target_dir)
            }
        
        except Exception as e:
            return {'error': f'Organization failed: {str(e)}'}
    
    def organize_documents_by_date(self, directory: Optional[str] = None) -> Dict:
        """
        Organize documents by date (YYYY-MM folders)
        
        Args:
            directory: Directory to organize
        
        Returns:
            Dict with organization results
        """
        if not self.enable_doc_organization:
            return {'error': 'Document organization is disabled'}
        
        try:
            target_dir = Path(directory).expanduser() if directory else Path.home() / "Downloads"
            
            if not self._is_path_allowed(target_dir):
                return {'error': 'Access denied: Directory not in allowed list'}
            
            if not target_dir.exists():
                return {'error': f'Directory not found: {target_dir}'}
            
            organized_count = 0
            results = {}
            
            for file in target_dir.iterdir():
                if file.is_file():
                    # Get file modification time
                    mod_time = datetime.fromtimestamp(file.stat().st_mtime)
                    date_folder = mod_time.strftime('%Y-%m')
                    
                    # Create date folder
                    folder_path = target_dir / date_folder
                    folder_path.mkdir(exist_ok=True)
                    
                    # Move file
                    try:
                        dest = folder_path / file.name
                        if dest.exists():
                            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                            dest = folder_path / f"{file.stem}_{timestamp}{file.suffix}"
                        
                        shutil.move(str(file), str(dest))
                        organized_count += 1
                        results[date_folder] = results.get(date_folder, 0) + 1
                    except Exception as e:
                        print(f"Error moving {file.name}: {e}")
            
            return {
                'status': 'success',
                'organized_count': organized_count,
                'date_folders': results,
                'directory': str(target_dir)
            }
        
        except Exception as e:
            return {'error': f'Organization failed: {str(e)}'}
    
    def summarize_document(self, file_path: str = None, filename: str = None, file_type: str = None) -> Dict:
        """
        Summarize document content (PDF, TXT, etc.)
        
        Args:
            file_path: Full path to document (optional if filename provided)
            filename: Filename or partial name to search for (e.g., "mind lab", "report")
            file_type: File type filter (e.g., "pdf", "txt")
        
        Returns:
            Dict with summary
        """
        if not self.enable_doc_summarization:
            return {'error': 'Document summarization is disabled'}
        
        try:
            # If no file_path provided, try to find by filename
            if not file_path and filename:
                found_file = self.find_file_by_name(filename, file_type)
                if not found_file:
                    return {
                        'error': f'Could not find file matching "{filename}"',
                        'suggestion': 'Try: "summarize latest pdf" or provide full path'
                    }
                file = found_file
            elif file_path:
                file = Path(file_path).expanduser()
            else:
                # No path or filename - summarize most recent document
                recent_files = self.get_recent_files(file_type or 'pdf', limit=1)
                if not recent_files:
                    return {'error': 'No recent documents found'}
                file = recent_files[0]
            
            if not self._is_path_allowed(file):
                return {'error': 'Access denied: File not in allowed directories'}
            
            if not file.exists():
                return {'error': f'File not found: {file}'}
            
            # Read file content based on type
            content = ""
            
            if file.suffix.lower() == '.txt':
                with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            
            elif file.suffix.lower() == '.pdf':
                try:
                    import PyPDF2
                    with open(file, 'rb') as f:
                        pdf_reader = PyPDF2.PdfReader(f)
                        for page in pdf_reader.pages:
                            content += page.extract_text()
                except ImportError:
                    return {'error': 'PDF support requires PyPDF2: pip install PyPDF2'}
                except Exception as e:
                    return {'error': f'PDF reading failed: {str(e)}'}
            
            else:
                return {'error': f'Unsupported file type: {file.suffix}'}
            
            # Create summary
            summary = self._create_summary(content)
            
            return {
                'file': str(file),
                'type': file.suffix,
                'size': f"{file.stat().st_size / 1024:.2f} KB",
                'summary': summary,
                'original_length': len(content),
                'summary_length': len(summary)
            }
        
        except Exception as e:
            return {'error': f'Summarization failed: {str(e)}'}
    
    def _create_summary(self, text: str) -> str:
        """Create a summary of the text"""
        # Simple extractive summarization
        sentences = text.replace('\n', ' ').split('. ')
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        # Take first N sentences (simple summary)
        summary_sentences = sentences[:self.summary_sentences]
        summary = '. '.join(summary_sentences)
        
        # Limit length
        if len(summary) > self.summary_max_length:
            summary = summary[:self.summary_max_length] + '...'
        
        return summary
    
    def process_csv(self, file_path: str, operation: str = 'analyze') -> Dict:
        """
        Process CSV/Excel files (analyze, filter, aggregate)
        
        Args:
            file_path: Path to CSV/Excel file
            operation: Operation to perform (analyze, stats, preview)
        
        Returns:
            Dict with processing results
        """
        if not self.enable_csv_processing:
            return {'error': 'CSV processing is disabled'}
        
        try:
            import csv
            
            file = Path(file_path).expanduser()
            
            if not self._is_path_allowed(file):
                return {'error': 'Access denied: File not in allowed directories'}
            
            if not file.exists():
                return {'error': f'File not found: {file}'}
            
            # Read CSV
            with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            
            if not rows:
                return {'error': 'CSV file is empty'}
            
            # Perform operation
            if operation == 'analyze' or operation == 'stats':
                columns = list(rows[0].keys())
                row_count = len(rows)
                
                # Basic stats
                stats = {
                    'file': str(file),
                    'rows': row_count,
                    'columns': len(columns),
                    'column_names': columns,
                    'size': f"{file.stat().st_size / 1024:.2f} KB"
                }
                
                return stats
            
            elif operation == 'preview':
                return {
                    'file': str(file),
                    'preview': rows[:5],  # First 5 rows
                    'total_rows': len(rows)
                }
            
            else:
                return {'error': f'Unknown operation: {operation}'}
        
        except Exception as e:
            return {'error': f'CSV processing failed: {str(e)}'}
    
    def generate_report(self, data: Dict, report_type: str = 'summary') -> Dict:
        """
        Auto-generate reports from data
        
        Args:
            data: Data to generate report from
            report_type: Type of report (summary, detailed, stats)
        
        Returns:
            Dict with report content
        """
        if not self.enable_report_generation:
            return {'error': 'Report generation is disabled'}
        
        try:
            report = {
                'title': f'{report_type.title()} Report',
                'generated_at': datetime.now().isoformat(),
                'type': report_type
            }
            
            # Generate report based on type
            if report_type == 'summary':
                report['sections'] = {
                    'Overview': self._generate_overview(data),
                    'Key Points': self._extract_key_points(data),
                    'Statistics': self._generate_stats(data)
                }
            
            return report
        
        except Exception as e:
            return {'error': f'Report generation failed: {str(e)}'}
    
    def _generate_overview(self, data: Dict) -> str:
        """Generate overview section"""
        return f"Report generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    def _extract_key_points(self, data: Dict) -> List[str]:
        """Extract key points from data"""
        return list(data.keys())[:5]
    
    def _generate_stats(self, data: Dict) -> Dict:
        """Generate statistics"""
        return {
            'total_items': len(data),
            'data_types': list(set(type(v).__name__ for v in data.values()))
        }
    
    def execute(self, command: str) -> str:
        """Main execution method"""
        command_lower = command.lower().strip()
        
        # Document organization by type
        if 'organize documents by type' in command_lower or 'organize docs by type' in command_lower:
            result = self.organize_documents_by_type()
            if 'error' in result:
                return result['error']
            return f"Documents Organized:\n  Total: {result['organized_count']} files\n  Categories: {', '.join(result['categories'].keys())}"
        
        # Document organization by date
        elif 'organize documents by date' in command_lower or 'organize docs by date' in command_lower:
            result = self.organize_documents_by_date()
            if 'error' in result:
                return result['error']
            return f"Documents Organized by Date:\n  Total: {result['organized_count']} files\n  Folders: {len(result['date_folders'])}"
        
        # Document summarization
        elif 'summarize document' in command_lower or 'summarize file' in command_lower:
            return "Please specify the file path: summarize document [path]"
        
        # CSV processing
        elif 'analyze csv' in command_lower or 'process csv' in command_lower:
            return "Please specify the CSV file path: analyze csv [path]"
        
        # Report generation
        elif 'generate report' in command_lower:
            result = self.generate_report({})
            if 'error' in result:
                return result['error']
            return f"Report Generated:\n  Type: {result['type']}\n  Generated: {result['generated_at']}"
        
        else:
            return self._help_message()
    
    def _help_message(self) -> str:
        """Return help message"""
        return """Document Processing Commands:
📁 Organize by Type: 'organize documents by type'
📅 Organize by Date: 'organize documents by date'
📄 Summarize: 'summarize document [path]'
📊 Analyze CSV: 'analyze csv [path]'
📝 Generate Report: 'generate report'

Examples:
  - organize documents by type
  - organize documents by date
  - summarize document ~/Documents/report.pdf
  - analyze csv ~/Downloads/data.csv"""
