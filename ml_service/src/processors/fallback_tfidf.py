from typing import Tuple, List, Optional

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import spacy


class FallbackProcessor:
    """
    Legacy TF-IDF matching logic acting as a safety net.
    It calculates statistical similarity based on word frequency,
    useful when semantic models (SBERT) or strict NER fail.
    """

    def __init__(self, nlp: spacy.language.Language):
        """
        Initializes with the shared Spacy NLP object for lemmatization.
        """
        self.nlp = nlp

    def analyze(self, job_text: str, cv_text: str) -> Tuple[float, List[str]]:
        """
        Calculates TF-IDF cosine similarity and extracts top common keywords.

        Returns:
            Tuple[float, List[str]]: (similarity_score, common_keywords)
        """
        # 1. Preprocessing (Lemmatization)
        # We process the FULL text to catch everything
        clean_job = self._lemmatize(job_text)
        clean_cv = self._lemmatize(cv_text)

        if not clean_job or not clean_cv:
            return 0.0, []

        try:
            # 2. Vectorization
            # stop_words='english' removes common noise like "and", "the", "is"
            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf_matrix = vectorizer.fit_transform([clean_job, clean_cv])

            # 3. Cosine Similarity
            # Matrix shape: (2, N_features)
            # We compare row 0 (Job) with row 1 (CV)
            similarity = cosine_similarity(
                tfidf_matrix[0:1], tfidf_matrix[1:2])
            score = float(similarity[0][0])

            # 4. Extract Common Keywords
            # Get feature names (words)
            feature_names = np.array(vectorizer.get_feature_names_out())

            # Get vectors as dense arrays
            job_vec = np.array(tfidf_matrix[0].todense()).flatten()
            cv_vec = np.array(tfidf_matrix[1].todense()).flatten()

            # Find indices where BOTH vectors have a value > 0
            # Multiply vectors: if either is 0, result is 0.
            common_mask = job_vec * cv_vec

            # Sort by highest combined weight (importance)
            sorted_indices = common_mask.argsort()[::-1]

            # Select top 10 keywords where overlap > 0
            top_indices = [
                idx for idx in sorted_indices if common_mask[idx] > 0][:10]
            common_keywords = feature_names[top_indices].tolist()

            return round(score, 4), common_keywords

        except ValueError:
            # Handle empty vocabulary cases (e.g., text contained only stop words)
            return 0.0, []

    def _lemmatize(self, text: str) -> str:
        """
        Helper: Cleans text and converts words to base form.
        Uses the injected Spacy model.
        """
        if not text:
            return ""

        # Increase max length to avoid errors on huge CVs
        self.nlp.max_length = 2000000

        doc = self.nlp(text.lower())

        # Keep only alphabetic tokens that are not stop words
        tokens = [
            token.lemma_ for token in doc if token.is_alpha and not token.is_stop]

        return " ".join(tokens)
