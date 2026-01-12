import { type ChangeEvent, memo } from 'react';
import { FILE_UPLOAD, MATCH_CONFIG } from '../../../constants';
import styles from '../GuestScanner.module.css';

interface CVInputSectionProps {
  inputMode: 'text' | 'file';
  cvText: string;
  setCvText: (text: string) => void;
  cvFile: File | null;
  setCvFile: (file: File | null) => void;
  loading: boolean;
}

export const CVInputSection = memo(({
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
        minLength={MATCH_CONFIG.MIN_CV_LENGTH}
        onChange={(e) => setCvText(e.target.value)}
        disabled={loading}
        aria-label="CV Text"
        required
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
        accept={FILE_UPLOAD.ACCEPTED_FORMATS}
        onChange={handleFileChange}
        disabled={loading}
        aria-label="Upload CV file"
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
});