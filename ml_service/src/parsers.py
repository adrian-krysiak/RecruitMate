import re
from typing import Dict, List, Optional, Pattern


class BaseParser:
    """
    Shared utilities and core logic for text parsing.
    """

    def __init__(self, raw_patterns: Dict[str, List[str]],
                 default_section: str):
        self.default_section = default_section
        # Pre-compile regex patterns once during initialization.
        self._compiled_patterns: Dict[str, Pattern] = {
            section: re.compile(
                r'(?:' + '|'.join(patterns) + r')',
                re.IGNORECASE
            )
            for section, patterns in raw_patterns.items()
        }

    def _parse_core(self, text: str) -> Dict[str, List[str]]:
        """
        Core parsing loop. Returns a dictionary of lists (buffers).
        """
        lines = text.split('\n')
        sections = {key: [] for key in self._compiled_patterns.keys()}

        if self.default_section not in sections:
            sections[self.default_section] = []

        current_section = self.default_section

        for line in lines:
            clean_line = line.strip()
            if not clean_line:
                continue

            new_section = self._detect_section_header(clean_line)

            if new_section:
                current_section = new_section
            else:
                sections[current_section].append(clean_line)
        return sections

    def _detect_section_header(self, line: str) -> Optional[str]:
        """
        Checks if a line matches a known section header pattern.
        """
        # 1. First guard: Line length heuristic
        if not self._is_likely_header(line):
            return None

        # 2. Second guard: Regex matching (using pre-compiled patterns)
        for section, pattern in self._compiled_patterns.items():
            if pattern.search(line):
                return section

        return None

    @staticmethod
    def _is_likely_header(line: str, max_words: int = 7) -> bool:
        """
        Heuristic: Headers are usually short and don't end with sentence
        punctuation.
        """
        if not line:
            return False

        # Check word count
        if len(line.split()) > max_words:
            return False

        # Check if it looks like a full sentence
        if line.endswith(('.', '!', '?', ';', ',', ')', ']', '}')):
            return False

        return True


class CVParser(BaseParser):
    """
    Parses Candidate CVs into structured sections.
    """
    RAW_PATTERNS = {
        'skills': [
            r'skills', r'technologies', r'tech stack',
            r'competencies', r'expertise', r'toolbox',
            r'proficiencies', r'abilities', r'knowledg[e|es]?',
            r'languages?'
        ],
        'experience': [
            r'experience', r'employment', r'work history', r'career'
        ],
        'education': [
            r'education', r'academic', r'background',
            r'qualifi', r'credentials', r'certifi'
        ],
        'projects': [
            r'projects', r'portfolios?'
        ],
        'summary': [
            r'summary', r'profile', r'about', r'objective', r'overview',
            r'intro'
        ],
        'other': [
            r'rodo', r'gdpr', r'consent', r'additional information',
            r'personal details', r'hobbies?', r'contacts?'
        ]
    }

    def __init__(self):
        super().__init__(self.RAW_PATTERNS, default_section='summary')

    def parse(self, text: str) -> Dict[str, str]:
        raw_sections = self._parse_core(text)
        # Filter out 'other' and join lines
        return {
            k: "\n".join(v)
            for k, v in raw_sections.items()
            if k != 'other' and v
        }


class JobOfferParser(BaseParser):
    """
    Parses Job Descriptions into Signal (Requirements) and Noise (About Us).
    """
    RAW_PATTERNS = {
        'requirements': [
            r'requirements', r'qualifications', r'what you bring',
            r'must have', r'skills', r'nice to have', r'profile',
            r'essential', r'technical requirements', r'you should have',
            r'who you are', r'what we look for', r'key skills',
            r'what you need', r'about you', r'preferred qualifications',
            r'competencies', r'capabilities', r'tech stack', r'if you'
        ],
        'responsibilities': [
            r'responsibilities', r'duties', r"what you'll do",
            r'what you will do', r'your role', r'scope',
            r'day to day', r"what you['’]ll", r'key tasks',
            r'accountabilities', r'you will'
        ],
        'education': [
            r'education', r'academic', r'background',
            r'qualifi', r'credentials', r'certifi'
        ],
        'about': [
            r'about (us|the company|the role)', r'company overview',
            r'who we are', r'why join us', r'mission?', r'vision?',
            r'our values?', r'what we offer', r'benefits?'
        ]
    }

    def __init__(self):
        super().__init__(self.RAW_PATTERNS, default_section='uncategorized')

    def parse(self, text: str) -> Dict[str, str]:
        raw_sections = self._parse_core(text)

        # Post-Processing: 'uncategorized' often contains requirements
        # in short job offers (merge it back, filter out about)

        return {
            k: "\n".join(v)
            for k, v in raw_sections.items()
            if k != 'about' and v
        }
