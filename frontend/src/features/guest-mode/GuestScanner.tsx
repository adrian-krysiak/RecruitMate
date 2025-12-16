import { useState, type FormEvent } from 'react';
import { useMatchAnalysis } from '../../hooks/useMatchAnalysis';
import { MatchResults } from './components/MatchResults';
import styles from './GuestScanner.module.css';
import { ErrorMessage } from "./components/ErrorMessage";

export const GuestScanner = () => {
  const [jobDesc, setJobDesc] = useState('');
  const [cvText, setCvText] = useState('');
  const { result, loading, error, performAnalysis } = useMatchAnalysis();
  const textAreaMinLength = 50

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (jobDesc && cvText) {
      await performAnalysis(jobDesc, cvText);
    }
  };

  return (
    <div className={styles.container}>
      <h1>RecruitMate - Guest Mode</h1>

      <form onSubmit={handleSubmit}>
        <div className={styles.grid}>
          <textarea
            className={styles.textarea}
            // rows={35}
            placeholder="Paste CV..."
            value={cvText}
            minLength={textAreaMinLength}
            onChange={(e) => setCvText(e.target.value)}
            disabled={loading}
          />
          <textarea
            className={styles.textarea}
            // rows={35}
            placeholder="Paste Job Description..."
            value={jobDesc}
            minLength={textAreaMinLength}
            onChange={(e) => setJobDesc(e.target.value)}
            disabled={loading}
          />
        </div>

        <button
          type="submit"
          disabled={loading || !jobDesc || !cvText}
          className={styles.button}
        >
          {loading ? 'Analyzing...' : 'Scan Match'}
        </button>
      </form>

      <ErrorMessage error={error} />

      {result && <MatchResults data={result} />}

    </div>
  );
};