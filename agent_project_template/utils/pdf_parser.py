"""
PDF Parser Tool

Tool for parsing text from PDF files using pdfplumber.
"""
import io
import pdfplumber
from typing import Union
from ai_agents.core.exceptions import DataProcessException
from ai_agents.core.error_codes import DataProcessErrorCode


def parse_text_from_pdf(file):
    """
    Parse text content from PDF file.

    Args:
        file: PDF file to parse.

    Returns:
        str: Extracted text content.
    """
    pass


def parse_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """
    Parse text content from PDF bytes using pdfplumber. 
    https://github.com/jsvine/pdfplumber 

    Args:
        pdf_bytes (bytes): PDF file content as bytes.

    Returns:
        str: Extracted text content from all pages.
    """
    try:
        pdf_file = io.BytesIO(pdf_bytes)
        with pdfplumber.open(pdf_file) as pdf:
            text_content = []
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text_content.append(page_text)
                else:
                    text_content.append(f"\n--- Page {page_num} (No text found) ---\n")
            return "\n".join(text_content) if text_content else "No text could be extracted from the PDF."
    except Exception as e:
        raise DataProcessException(DataProcessErrorCode.DATA_CONVERSION_ERROR, detail=f"Error parsing PDF content: {str(e)}")


def parse_text_from_pdf_file(file_path: str) -> str:
    """
    Parse text content from PDF file path using pdfplumber.

    Args:
        file_path (str): Path to the PDF file.

    Returns:
        str: Extracted text content from all pages.
    """
    try:
        with pdfplumber.open(file_path) as pdf:
            text_content = []
            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text()
                if page_text:
                    text_content.append(page_text)
                else:
                    text_content.append(f"\n--- Page {page_num} (No text found) ---\n")
            return "\n".join(text_content) if text_content else "No text could be extracted from the PDF."
    except Exception as e:
        raise DataProcessException(DataProcessErrorCode.DATA_CONVERSION_ERROR, detail=f"Error parsing PDF file: {str(e)}")

# https://docling-project.github.io/docling/usage/#adjust-pipeline-features
# 非p0任务，不使用docling
# 先检查OCR是否能识别，如果不能，再使用docling; 后面有时间再优化