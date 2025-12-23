from typing import List, Set, Dict, Tuple

from spacy.language import Language

from src.config import SECTION_WEIGHTS


class NERProcessor:
    """
    Processor responsible for Named Entity Recognition and Gap Analysis.
    It identifies technical skills in the Job Offer and checks their presence
    in specific sections of the CV, applying weighted scoring.
    """

    def __init__(self, nlp: Language):
        """
        Initializes the processor with a shared Spacy NLP object.
        We inject the EntityRuler here to ensure skills are recognized.
        """
        self.nlp = nlp
        self._setup_entity_ruler()

    def _setup_entity_ruler(self):
        """
        Configures the EntityRuler with patterns.
        Checks if ruler exists to avoid duplication errors on re-init.
        """
        if "entity_ruler" not in self.nlp.pipe_names:
            ruler = self.nlp.add_pipe("entity_ruler", before="parser")
        else:
            ruler = self.nlp.get_pipe("entity_ruler")
            # Clear old patterns if any, to ensure fresh state
            ruler.clear()

        # Load MVP patterns (In future: Load from ESCO/DB)
        patterns = self._get_mvp_patterns()
        ruler.add_patterns(patterns)

    def analyze(self, job_text: str, cv_sections: Dict[str, str]
                ) -> Tuple[float, List[str], List[str]]:
        """
        Performs the Gap Analysis and calculates the Weighted Keyword Score.

        Returns:
            Tuple[float, List[str], List[str]]:
            (keyword_score, common_keywords, missing_keywords)
        """
        # 1. Extract required skills from Job Offer (Signal only)
        job_skills = self._extract_skills(job_text)

        if not job_skills:
            # Fallback: If no skills detected in job, we can't score based on keywords.
            # Return 0.0 or handle in Orchestrator (Fallback Processor).
            return 0.0, [], []

        # 2. Extract skills from CV per section to apply weights
        # Map: {'python': 1.0, 'sql': 0.65, ...} (stores max weight found for skill)
        cv_skill_weights: Dict[str, float] = {}

        for section, text in cv_sections.items():
            if not text:
                continue

            section_weight = SECTION_WEIGHTS.get(section, 0.1)
            skills_in_section = self._extract_skills(text)

            for skill in skills_in_section:
                # Keep the highest weight (e.g., if skill is in Exp and Skills, take Exp)
                current_max = cv_skill_weights.get(skill, 0.0)
                cv_skill_weights[skill] = max(current_max, section_weight)

        # 3. Gap Analysis & Scoring
        common_keywords = []
        missing_keywords = []
        total_score = 0.0

        for required_skill in job_skills:
            if required_skill in cv_skill_weights:
                # Skill found! Add the weight of the section it was found in.
                # Example: Found in Experience -> +1.0
                total_score += cv_skill_weights[required_skill]
                common_keywords.append(required_skill)
            else:
                # Skill missing -> +0.0
                missing_keywords.append(required_skill)

        # Normalize score (0.0 to 1.0)
        # Score = Sum of weights / Number of required skills
        # If perfect match in Experience sections -> 1.0
        final_score = total_score / len(job_skills)

        return round(final_score, 4), common_keywords, missing_keywords

    def _extract_skills(self, text: str) -> List[str]:
        """
        Runs the NLP pipeline and returns unique SKILL entities (lowercase).
        """
        if not text.strip():
            return []

        doc = self.nlp(text)
        # Use set comprehension for uniqueness
        skills_dict = {}
        for ent in doc.ents:
            if ent.label_ == "SKILL":
                skills_dict[ent.text.lower()] = None
        return list(skills_dict.keys())

    def _get_mvp_patterns(self) -> List[Dict]:
        """
        Returns the hardcoded list of patterns for the MVP.
        TODO: Replace with ESCO CSV loader.
        """
        skills = [
            # Data & AI
            "Python", "SQL", "NoSQL", "Postgres", "PostgreSQL", "ETL", "Data Engineering",
            "Pandas", "NumPy", "Matplotlib", "Seaborn", "Scikit-learn",
            "TensorFlow", "PyTorch", "Keras", "LangChain", "RAG", "LLM",
            "Machine Learning", "Deep Learning", "Data Science", "NLP",

            # Web & Backend
            "Django", "Flask", "FastAPI", "React", "TypeScript", "JavaScript", "JS",
            "HTML", "CSS", "Node.js", "Java", "C++", "C#", ".NET", "Go", "Golang",
            "Rust", "PHP", "Laravel", "Spring Boot",

            # DevOps & Cloud
            "AWS", "Amazon Web Services", "Azure", "GCP", "Google Cloud",
            "Docker", "Kubernetes", "K8s", "Terraform", "Ansible", "Jenkins",
            "Git", "GitHub", "GitLab", "CI/CD", "Linux", "Bash",

            # BI & Tools
            "Power BI", "Tableau", "Excel", "Jira", "Confluence", "Slack",

            # Soft Skills & Methodology
            "Agile", "Scrum", "Kanban", "Leadership", "Communication",
            "Teamwork", "Problem Solving", "Critical Thinking", "English",
            "Project Management", "Time Management"
        ]

        patterns = []
        for skill in skills:
            patterns.append({"label": "SKILL", "pattern": [
                            {"LOWER": skill.lower()}]})

        return patterns
