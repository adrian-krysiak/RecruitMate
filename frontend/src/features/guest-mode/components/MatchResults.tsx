import { type MatchResponse, type MatchStatus, type CuratedMatchDetail } from '../../../types/api';
import { STATUS_CONFIG } from '../../../constants';
import styles from './MatchResults.module.css';
import { memo } from 'react';

interface MatchResultsProps {
  data: MatchResponse;
}

// Helper to get status configuration
const getStatusConfig = (status: MatchStatus) => {
  return STATUS_CONFIG[status] || STATUS_CONFIG.None;
};

// --- Sub-Components ---

/** Overall Score Header */
const OverallScoreHeader = ({ score, status }: { score: number | null; status: MatchStatus }) => {
  const config = getStatusConfig(status);
  return (
    <div className={`${styles.overallScore} ${styles[config.colorClass]}`}>
      <h2>
        {score !== null ? (
          <>Match Score: {score}%</>
        ) : (
          <>{config.label} {config.emoji}</>
        )}
      </h2>
      {score !== null && (
        <span className={styles.statusLabel}>{config.label} {config.emoji}</span>
      )}
    </div>
  );
};

/** Status Metrics Row */
const StatusMetrics = ({
  semantic,
  keywords,
  actionVerbs,
}: {
  semantic: MatchStatus;
  keywords: MatchStatus;
  actionVerbs: MatchStatus;
}) => (
  <div className={styles.scoresWrapper}>
    <StatusCard label="Semantic Relevance" status={semantic} />
    <StatusCard label="ATS Keywords" status={keywords} />
    <StatusCard label="Action Verbs" status={actionVerbs} />
  </div>
);

/** Individual Status Card */
const StatusCard = ({ label, status }: { label: string; status: MatchStatus }) => {
  const config = getStatusConfig(status);
  return (
    <div className={`${styles.scoreItem} ${styles[config.colorClass]}`}>
      <span className={styles.scoreLabel}>{label}</span>
      <span className={styles.statusValue}>
        {config.label} {config.emoji}
      </span>
    </div>
  );
};

/** Missing Keywords Section with Premium Upsell */
const MissingKeywordsSection = ({
  keywords,
  hiddenCount,
}: {
  keywords: string[];
  hiddenCount: number;
}) => {
  if (keywords.length === 0 && hiddenCount === 0) return null;

  return (
    <div className={styles.missingKeywordsSection}>
      <h3>⚠️ Missing Keywords</h3>
      <p className={styles.sectionHint}>
        Add these keywords to your CV to improve ATS compatibility:
      </p>
      <div className={styles.keywordList}>
        {keywords.map((keyword, index) => (
          <span key={index} className={styles.keywordTag}>
            {keyword}
          </span>
        ))}
        {hiddenCount > 0 && (
          <div className={styles.lockedCard}>
            <span className={styles.lockIcon}>🔒</span>
            <span>
              And <strong>{hiddenCount}</strong> more keywords.{' '}
              <em>Upgrade to Premium to see the full list.</em>
            </span>
          </div>
        )}
      </div>
    </div>
  );
};

/** Unaddressed Requirements (Gaps) Section */
const UnaddressedRequirementsSection = ({ requirements }: { requirements: string[] }) => {
  if (requirements.length === 0) return null;

  return (
    <div className={styles.gapsSection}>
      <h3>🎯 Gaps in Your Profile</h3>
      <p className={styles.sectionHint}>
        These job requirements were not clearly addressed in your CV:
      </p>
      <ul className={styles.gapsList}>
        {requirements.map((req, index) => (
          <li key={index} className={styles.gapItem}>
            {req}
          </li>
        ))}
      </ul>
    </div>
  );
};

/** Top Matches Detail List */
const TopMatchesList = ({ matches }: { matches: CuratedMatchDetail[] }) => {
  if (matches.length === 0) {
    return (
      <div className={styles.emptyState}>
        <p>No strong matches found between your CV and the job requirements.</p>
      </div>
    );
  }

  return (
    <div className={styles.detailsList}>
      {matches.map((match, idx) => {
        const config = getStatusConfig(match.status);
        return (
          <div key={idx} className={`${styles.detailItem} ${styles[config.colorClass]}`}>
            <div className={styles.detailHeader}>
              <strong className={styles.statusBadge}>
                {config.label} {config.emoji}
              </strong>
              {match.score_percentage !== null && (
                <span className={styles.scoreDisplay}>
                  {match.score_percentage}%
                </span>
              )}
            </div>

            <div className={styles.metaInfo}>
              Section: {match.cv_section}
            </div>

            <p className={styles.detailText}>
              <span className={styles.detailLabel}>JOB REQUIREMENT</span>
              {match.job_requirement}
            </p>

            <p className={styles.detailText}>
              <span className={styles.detailLabel}>YOUR CV</span>
              {match.cv_match}
            </p>
          </div>
        );
      })}
    </div>
  );
};

/** AI Report Section with Premium Upsell */
const AIReportSection = ({ report }: { report: string | null }) => {
  return (
    <div className={styles.aiReportSection}>
      <h3>🤖 AI Deep Analysis</h3>
      {report ? (
        <div className={styles.aiReportContent}>
          {/* Render markdown as plain text for now - can add react-markdown later */}
          {report.split('\n').map((line, idx) => (
            <p key={idx}>{line}</p>
          ))}
        </div>
      ) : (
        <div className={styles.upgradePrompt}>
          <div className={styles.upgradeIcon}>✨</div>
          <div className={styles.upgradeText}>
            <strong>Unlock Deep AI Analysis</strong>
            <p>
              Get personalized feedback on your CV, including specific suggestions
              for improvement, missing skills analysis, and tailored recommendations
              to boost your match score.
            </p>
            <p className={styles.premiumHint}>
              Premium users with AI Deep Analysis receive detailed AI-powered insights with every scan.
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

// --- Main Component ---
export const MatchResults = memo(({ data }: MatchResultsProps) => {
  return (
    <div className={styles.container}>
      <OverallScoreHeader score={data.overall_score} status={data.overall_status} />

      <StatusMetrics
        semantic={data.semantic_status}
        keywords={data.keywords_status}
        actionVerbs={data.action_verbs_status}
      />

      <MissingKeywordsSection
        keywords={data.missing_keywords}
        hiddenCount={data.hidden_keywords_count}
      />

      <UnaddressedRequirementsSection requirements={data.unaddressed_requirements} />

      <h3>🔍 Top Matches</h3>
      <TopMatchesList matches={data.top_matches} />

      <AIReportSection report={data.ai_report} />
    </div>
  );
});