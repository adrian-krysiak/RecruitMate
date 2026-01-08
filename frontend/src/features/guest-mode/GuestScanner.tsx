import { useState, useEffect, type FormEvent } from 'react';
import { useMatchAnalysis } from '../../hooks/useMatchAnalysis';
import { MatchResults } from './components/MatchResults';
import { ErrorMessage } from "./components/ErrorMessage";
import { ScannerControls } from './components/ScannerControls';
import { CVInputSection } from './components/CVInputSection';
import { LoadingOverlay } from '../../components/LoadingOverlay';
import styles from './GuestScanner.module.css';

interface GuestScannerProps {
  isLoggedIn?: boolean;
}

export const GuestScanner = ({ isLoggedIn = false }: GuestScannerProps) => {
  const [jobDesc, setJobDesc] = useState('');
  const [cvText, setCvText] = useState('');
  const [cvFile, setCvFile] = useState<File | null>(null);
  const [useAiParsing, setUseAiParsing] = useState(isLoggedIn);

  const [inputMode, setInputMode] = useState<'text' | 'file'>(() => {
    return (sessionStorage.getItem('guestScannerInputMode') as 'text' | 'file') || 'text';
  });

  const { result, loading, error, performAnalysis } = useMatchAnalysis();

  useEffect(() => {
    sessionStorage.setItem('guestScannerInputMode', inputMode);
  }, [inputMode]);


  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    const hasCv = inputMode === 'text' ? cvText.length >= 50 : !!cvFile;

    if (jobDesc && hasCv) {
      if (inputMode === 'file' && cvFile) {
        console.log("Sending file:", cvFile.name);
        await performAnalysis(jobDesc, `[FILE UPLOADED: ${cvFile.name}]`);
      } else {
        await performAnalysis(jobDesc, cvText);
      }
    }
  };

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
            minLength={50}
            onChange={(e) => setJobDesc(e.target.value)}
            disabled={loading}
          />
        </div>

        <button
          type="submit"
          disabled={loading || !jobDesc || (inputMode === 'text' ? !cvText : !cvFile)}
          className={styles.button}
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