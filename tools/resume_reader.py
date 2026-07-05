from pathlib import Path
from pypdf import PdfReader


class ResumeReader:
    """
    Reads PDF resumes and extracts text.
    """

    @staticmethod
    def extract_text(file_path: str) -> dict:
        """
        Extract text from a PDF resume.

        Args:
            file_path (str): Path to PDF file

        Returns:
            dict: {
                "success": bool,
                "text": str,
                "error": str | None
            }
        """

        try:
            pdf_path = Path(file_path)

            # File existence check
            if not pdf_path.exists():
                return {
                    "success": False,
                    "text": "",
                    "error": f"File not found: {file_path}"
                }

            # File type validation
            if pdf_path.suffix.lower() != ".pdf":
                return {
                    "success": False,
                    "text": "",
                    "error": "Only PDF files are supported."
                }

            reader = PdfReader(file_path)

            extracted_pages = []

            for page in reader.pages:
                page_text = page.extract_text()

                if page_text:
                    extracted_pages.append(page_text)

            full_text = "\n".join(extracted_pages)

            # Basic cleaning
            full_text = full_text.replace("\t", " ")
            full_text = full_text.replace("\r", " ")

            return {
                "success": True,
                "text": full_text.strip(),
                "error": None
            }

        except Exception as e:
            return {
                "success": False,
                "text": "",
                "error": str(e)
            }