import { useState, useEffect, useCallback, type FormEvent } from 'react';
import { useMatchAnalysis } from '../../hooks/useMatchAnalysis';
import { MatchResults } from './components/MatchResults';
import { ErrorMessage } from "./components/ErrorMessage";
import { ScannerControls } from './components/ScannerControls';
import { CVInputSection } from './components/CVInputSection';
import { LoadingOverlay } from '../../components/LoadingOverlay';
import { STORAGE_KEYS, MATCH_CONFIG } from '../../constants';
import { StorageService } from '../../utils/storage';
import styles from './GuestScanner.module.css';

interface GuestScannerProps {
  isLoggedIn?: boolean;
}

export const GuestScanner = ({ isLoggedIn = false }: GuestScannerProps) => {
  const [jobDesc, setJobDesc] = useState('');
  const [cvText, setCvText] = useState('');
  const [cvFile, setCvFile] = useState<File | null>(null);
  // Use isLoggedIn directly to control AI parsing state
  const [useAiParsing, setUseAiParsing] = useState(false);

  const [inputMode, setInputMode] = useState<'text' | 'file'>(() => {
    return (StorageService.getString(STORAGE_KEYS.SCANNER_INPUT_MODE) as 'text' | 'file') || 'text';
  });

  const { result, loading, error, performAnalysis } = useMatchAnalysis();

  useEffect(() => {
    StorageService.setString(STORAGE_KEYS.SCANNER_INPUT_MODE, inputMode);
  }, [inputMode]);

  // Reset AI parsing when login state changes
  useEffect(() => {
    setUseAiParsing(isLoggedIn);
  }, [isLoggedIn]);


  const handleSubmit = useCallback(async (e: FormEvent) => {
    e.preventDefault();

    const hasCv = inputMode === 'text' ? cvText.length >= MATCH_CONFIG.MIN_CV_LENGTH : !!cvFile;

    if (jobDesc && hasCv) {
      if (inputMode === 'file' && cvFile) {
        console.log("Sending file:", cvFile.name);
        await performAnalysis(jobDesc, `[FILE UPLOADED: ${cvFile.name}]`);
      } else {
        await performAnalysis(jobDesc, cvText);
      }
    }
  }, [inputMode, cvText, cvFile, jobDesc, performAnalysis]);

  return (
    <>
      <LoadingOverlay isVisible={loading} message="Analyzing CV match..." />
      <div className={styles.container}>
        <h1>RecruitMate - Guest Mode</h1>

        <ScannerControls
          inputMode={inputMode}
          setInputMode={setInputMode}
          isLoggedIn={isLoggedIn}
          useAiParsing={useAiParsing}
          setUseAiParsing={setUseAiParsing}
        />

        <form onSubmit={handleSubmit}>
          <div className={styles.grid}>

            <CVInputSection
              inputMode={inputMode}
              cvText={cvText}
              setCvText={setCvText}
              cvFile={cvFile}
              setCvFile={setCvFile}
              loading={loading}
            />

            <textarea
              className={styles.textarea}
              placeholder="Paste Job Description..."
              value={jobDesc}
              minLength={MATCH_CONFIG.MIN_JOB_DESC_LENGTH}
              onChange={(e) => setJobDesc(e.target.value)}
              disabled={loading}
              aria-label="Job Description"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading || !jobDesc || (inputMode === 'text' ? !cvText : !cvFile)}
            className={styles.button}
            aria-label="Scan match between CV and job description"
          >
            {loading ? 'Analyzing...' : 'Scan Match'}
          </button>
        </form>

        <ErrorMessage error={error} />
        {result && <MatchResults data={result} />}
      </div>
    </>
  );
};