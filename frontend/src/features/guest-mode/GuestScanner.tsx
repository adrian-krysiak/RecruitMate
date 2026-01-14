import { useState, useEffect, useCallback, type FormEvent } from 'react';
import { useMatchAnalysis } from '../../hooks/useMatchAnalysis';
import { MatchResults } from './components/MatchResults';
import { ErrorMessage } from "./components/ErrorMessage";
import { ScannerControls } from './components/ScannerControls';
import { CVInputSection } from './components/CVInputSection';
import { LoadingOverlay } from '../../components/LoadingOverlay';
import { STORAGE_KEYS, MATCH_CONFIG, SESSION_KEYS } from '../../constants';
import { StorageService } from '../../utils/storage';
import styles from './GuestScanner.module.css';

interface GuestScannerProps {
  isLoggedIn?: boolean;
  isPremium?: boolean;
}

// Helper to read file content as text
const readFileAsText = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result as string);
    reader.onerror = () => reject(new Error('Failed to read file'));
    reader.readAsText(file);
  });
};

export const GuestScanner = ({ isLoggedIn = false, isPremium = false }: GuestScannerProps) => {
  // Load persisted form data from sessionStorage
  const [jobDesc, setJobDesc] = useState(() =>
    StorageService.getSessionString(SESSION_KEYS.SCANNER_JOB_DESC) || ''
  );
  const [cvText, setCvText] = useState(() =>
    StorageService.getSessionString(SESSION_KEYS.SCANNER_CV_TEXT) || ''
  );
  const [cvFile, setCvFile] = useState<File | null>(null);

  const [inputMode, setInputMode] = useState<'text' | 'file'>(() => {
    return (StorageService.getString(STORAGE_KEYS.SCANNER_INPUT_MODE) as 'text' | 'file') || 'text';
  });

  const { result, loading, error, performAnalysis } = useMatchAnalysis();

  // User's toggle preference (persists even when they lose premium)
  const [aiEnabled, setAiEnabled] = useState(false);

  // Actual AI parsing state: derived from user preference AND premium status
  // Automatically becomes false when user loses premium/logs out
  const useAiParsing = aiEnabled && isLoggedIn && isPremium;

  // Persist input mode to localStorage
  useEffect(() => {
    StorageService.setString(STORAGE_KEYS.SCANNER_INPUT_MODE, inputMode);
  }, [inputMode]);

  // Persist CV text to sessionStorage
  useEffect(() => {
    if (cvText) {
      StorageService.setSessionString(SESSION_KEYS.SCANNER_CV_TEXT, cvText);
    } else {
      StorageService.removeSessionItem(SESSION_KEYS.SCANNER_CV_TEXT);
    }
  }, [cvText]);

  // Persist job description to sessionStorage
  useEffect(() => {
    if (jobDesc) {
      StorageService.setSessionString(SESSION_KEYS.SCANNER_JOB_DESC, jobDesc);
    } else {
      StorageService.removeSessionItem(SESSION_KEYS.SCANNER_JOB_DESC);
    }
  }, [jobDesc]);

  const handleSubmit = useCallback(async (e: FormEvent) => {
    e.preventDefault();

    const hasCv = inputMode === 'text' ? cvText.length >= MATCH_CONFIG.MIN_CV_LENGTH : !!cvFile;

    if (jobDesc && hasCv) {
      if (inputMode === 'file' && cvFile) {
        try {
          // Read file content as text for TXT files
          if (cvFile.type === 'text/plain') {
            const fileContent = await readFileAsText(cvFile);
            await performAnalysis(jobDesc, fileContent, useAiParsing);
          } else {
            // For PDF/DOCX, we need backend parsing - send as FormData
            // For now, indicate file upload is for these formats
            await performAnalysis(jobDesc, `[FILE: ${cvFile.name}] - PDF/DOCX parsing requires backend support`, useAiParsing);
          }
        } catch {
          await performAnalysis(jobDesc, `[FILE ERROR: Could not read ${cvFile.name}]`, useAiParsing);
        }
      } else {
        await performAnalysis(jobDesc, cvText, useAiParsing);
      }
    }
  }, [inputMode, cvText, cvFile, jobDesc, performAnalysis, useAiParsing]);

  return (
    <>
      <LoadingOverlay isVisible={loading} message="Analyzing CV match..." />
      <div className={styles.container}>
        <h1>RecruitMate - Guest Mode</h1>

        <ScannerControls
          inputMode={inputMode}
          setInputMode={setInputMode}
          isLoggedIn={isLoggedIn}
          isPremium={isPremium}
          useAiParsing={useAiParsing}
          setUseAiParsing={setAiEnabled}
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