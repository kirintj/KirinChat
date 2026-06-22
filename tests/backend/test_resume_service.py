import pytest
from kirinchat.api.services.resume import ResumeService


class TestResumeService:
    def test_validate_file_type_valid(self):
        assert ResumeService._validate_file_type("resume.pdf") == True
        assert ResumeService._validate_file_type("resume.docx") == True
        assert ResumeService._validate_file_type("resume.txt") == True

    def test_validate_file_type_invalid(self):
        assert ResumeService._validate_file_type("resume.exe") == False
        assert ResumeService._validate_file_type("resume.jpg") == False

    def test_validate_file_size_valid(self):
        assert ResumeService._validate_file_size(1024) == True
        assert ResumeService._validate_file_size(10 * 1024 * 1024) == True

    def test_validate_file_size_invalid(self):
        assert ResumeService._validate_file_size(11 * 1024 * 1024) == False

    def test_compute_hash(self):
        h1 = ResumeService._compute_hash(b"hello world")
        h2 = ResumeService._compute_hash(b"hello world")
        h3 = ResumeService._compute_hash(b"different content")
        assert h1 == h2
        assert h1 != h3
        assert len(h1) == 64  # SHA256 hex length
