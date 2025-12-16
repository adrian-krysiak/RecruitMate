import { type MatchResponse } from '../../../types/api';
import styles from './MatchResults.module.css';

interface MatchResultsProps {
  data: MatchResponse;
}

export const MatchResults = ({ data }: MatchResultsProps) => {

  const sortedDetails = [...data.details].sort((a, b) => {
      return b.score - a.score;
  })

  return (
    <div className={styles.container}>
      <h2>Match Score: {(data.final_score * 100).toFixed(1)}%</h2>

      <div className={styles.scoresWrapper}>
        <span className={styles.scoreItem}>
            Semantic: {(data.sbert_score * 100).toFixed(1)}%
        </span>
        <span className={styles.scoreItem}>
            Keywords: {(data.tfidf_score * 100).toFixed(1)}%
        </span>
      </div>

      <h3>Details Breakdown</h3>
      {sortedDetails.map((detail, idx) => (
        <div key={idx} className={styles.detailItem}>
          <div className={styles.detailHeader}>
            <strong className={styles.statusBadge}>{detail.status}</strong>
            <span>Score: {detail.score.toFixed(2)}</span>
          </div>
          <p className={styles.detailText}>
            {detail.requirement_chunk}
          </p>
        </div>
      ))}
    </div>
  );
};