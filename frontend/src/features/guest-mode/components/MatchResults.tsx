import { type MatchResponse } from '../../../types/api';
import { SCORE_THRESHOLDS } from '../../../constants';
import styles from './MatchResults.module.css';
import { memo, useMemo } from 'react';

interface MatchResultsProps {
  data: MatchResponse;
}

interface ComputedStatus {
  label: string;
  className: string;
}

// Helper to determine status based on score
const getTemporaryStatus = (score: number): ComputedStatus => {
  if (score >= SCORE_THRESHOLDS.GOOD) return { label: "Good Match ✅", className: styles.statusGood };
  if (score >= SCORE_THRESHOLDS.MEDIUM) return { label: "Medium Match ⚠️", className: styles.statusMedium };
  if (score > SCORE_THRESHOLDS.WEAK) return { label: "Weak Match 🔸", className: styles.statusWeak };
  return { label: "No Match ❌", className: styles.statusNone };
};

export const MatchResults = memo(({ data }: MatchResultsProps) => {

  const sortedDetails = useMemo(() =>
    [...data.details].sort((a, b) => b.score - a.score),
    [data.details]
  );

  return (
    <div className={styles.container}>
      <h2>Match Score: {(data.final_score * 100).toFixed(1)}%</h2>

      {/* Main Scores */}
      <div className={styles.scoresWrapper}>
        <div className={styles.scoreItem}>
          <span className={styles.scoreLabel}>Semantic</span>
          <span className={styles.scoreValue}>{(data.semantic_score * 100).toFixed(1)}%</span>
        </div>
        <div className={styles.scoreItem}>
          <span className={styles.scoreLabel}>Keywords</span>
          <span className={styles.scoreValue}>{(data.keyword_score * 100).toFixed(1)}%</span>
        </div>
        <div className={styles.scoreItem}>
          <span className={styles.scoreLabel}>Action Verbs</span>
          <span className={styles.scoreValue}>{(data.action_verb_score * 100).toFixed(1)}%</span>
        </div>
      </div>

      {/* Missing Keywords Alert */}
      {data.missing_keywords.length > 0 && (
        <div className={styles.missingKeywordsSection}>
          <h3>⚠️ Missing Keywords</h3>
          <div className={styles.keywordList}>
            {data.missing_keywords.map((keyword, index) => (
              <span key={index} className={styles.keywordTag}>
                {keyword}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Details List */}
      <h3>Details Breakdown</h3>
      <div className={styles.detailsList}>
        {sortedDetails.map((detail, idx) => {
          const status = getTemporaryStatus(detail.score);

          return (
            <div key={idx} className={`${styles.detailItem} ${status.className}`}>
              <div className={styles.detailHeader}>
                <strong className={styles.statusBadge}>{status.label}</strong>
                <span className={styles.scoreDisplay}>Score: {detail.score.toFixed(2)}</span>
                {detail.raw_semantic_score && (
                  <span className={styles.scoreDisplay}>
                    Raw Score: {detail.raw_semantic_score.toFixed(2)}
                  </span>
                )}
              </div>

              <div className={styles.metaInfo}>
                Section: {detail.cv_section}
              </div>

              <p className={styles.detailText}> OFFER <br />
                {detail.job_requirement}
              </p>

              <p className={styles.detailText}> CV <br />
                {detail.best_cv_match}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
});