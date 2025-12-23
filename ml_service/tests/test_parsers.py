from src.parsers import CVParser, JobOfferParser


def test_cv_parser_segmentation():
    """Verify CV sections are detected."""
    cv_text = """
    John Doe
    Summary
    Passionate developer.
    Experience
    Worked at Google.
    Skills
    Python, SQL.
    """
    parser = CVParser()
    sections = parser.parse(cv_text)

    assert "passionate developer" in sections["summary"].lower()
    assert "worked at google" in sections["experience"].lower()
    assert "python" in sections["skills"].lower()


def test_job_parser_signal_filtering():
    """Verify noise like 'About Us' is separated."""
    job_text = """
    About Us
    We are a great company.
    Requirements
    Must know Python.
    Responsibilities
    Write code.
    """
    parser = JobOfferParser()
    parsed = parser.parse(job_text)

    assert "about" not in parsed
    assert "must know python" in parsed["requirements"].lower()
    assert "write code" in parsed["responsibilities"].lower()
