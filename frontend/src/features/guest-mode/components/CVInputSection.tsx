import { type ChangeEvent } from 'react';
import styles from '../GuestScanner.module.css';

interface CVInputSectionProps {
  inputMode: 'text' | 'file';
  cvText: string;
  setCvText: (text: string) => void;
  cvFile: File | null;
  setCvFile: (file: File | null) => void;
  loading: boolean;
}

export const CVInputSection = ({
  inputMode,
  cvText,
  setCvText,
  cvFile,
  setCvFile,
  loading
}: CVInputSectionProps) => {

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setCvFile(e.target.files[0]);
    }
  };

  if (inputMode === 'text') {
    return (
      <textarea
        className={styles.textarea}
        placeholder="Paste CV text here..."
        value={cvText}
        minLength={50}
        onChange={(e) => setCvText(e.target.value)}
        disabled={loading}
      />
    );
  }

  return (
    <div className={styles.fileUploadArea}>
      <p>Supported formats: PDF, DOCX, TXT</p>
      <input
        type="file"
        id="cv-upload"
        className={styles.fileInput}
        accept=".pdf,.docx,.txt"
        onChange={handleFileChange}
        disabled={loading}
      />
      <label htmlFor="cv-upload" className={styles.uploadLabel}>
        {loading ? 'Uploading...' : 'Choose File'}
      </label>

      {cvFile && (
        <div className={styles.fileName}>
          Selected: {cvFile.name}
        </div>
      )}
    </div>
  );
};