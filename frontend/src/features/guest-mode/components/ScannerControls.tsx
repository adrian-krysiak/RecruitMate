import { memo } from 'react';
import styles from '../GuestScanner.module.css';

interface ScannerControlsProps {
  inputMode: 'text' | 'file';
  setInputMode: (mode: 'text' | 'file') => void;
  isLoggedIn: boolean;
  useAiParsing: boolean;
  setUseAiParsing: (val: boolean) => void;
}

export const ScannerControls = memo(({
  inputMode,
  setInputMode,
  isLoggedIn,
  useAiParsing,
  setUseAiParsing
}: ScannerControlsProps) => {
  return (
    <div className={styles.controlsHeader}>
      <div className={styles.tabsContainer} role="tablist">
        <button
          type="button"
          className={`${styles.tabButton} ${inputMode === 'text' ? styles.activeTab : ''}`}
          onClick={() => setInputMode('text')}
          role="tab"
          aria-selected={inputMode === 'text'}
          aria-label="Paste CV as text"
        >
          Paste Text
        </button>
        <button
          type="button"
          className={`${styles.tabButton} ${inputMode === 'file' ? styles.activeTab : ''}`}
          onClick={() => setInputMode('file')}
          role="tab"
          aria-selected={inputMode === 'file'}
          aria-label="Upload CV file"
        >
          Upload File
        </button>
      </div>

      <div className={`${styles.toggleContainer} ${!isLoggedIn ? styles.disabledControl : ''}`}>
        <span>AI Deep Analysis</span>
        <label className={styles.switch}>
          <input
            type="checkbox"
            checked={useAiParsing}
            onChange={(e) => setUseAiParsing(e.target.checked)}
            disabled={!isLoggedIn}
            aria-label="Enable AI deep analysis (requires login)"
          />
          <span className={styles.slider}></span>
        </label>
      </div>
    </div>
  );
});