import { memo } from 'react';
import styles from '../GuestScanner.module.css';

interface ScannerControlsProps {
  inputMode: 'text' | 'file';
  setInputMode: (mode: 'text' | 'file') => void;
  isLoggedIn: boolean;
  isPremium: boolean;
  useAiParsing: boolean;
  setUseAiParsing: (val: boolean) => void;
}

export const ScannerControls = memo(({
  inputMode,
  setInputMode,
  isLoggedIn,
  isPremium,
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

      <div className={`${styles.toggleContainer} ${!isLoggedIn || !isPremium ? styles.disabledControl : ''}`}>
        <span>AI Deep Analysis {!isPremium && "🔒"}</span>
        <label className={styles.switch}>
          <input
            type="checkbox"
            checked={useAiParsing}
            onChange={(e) => setUseAiParsing(e.target.checked)}
            disabled={!isLoggedIn || !isPremium}
            aria-label={!isPremium ? "AI analysis (Premium feature)" : "Enable AI deep analysis"}
            title={!isPremium ? "Premium feature" : ""}
          />
          <span className={styles.slider}></span>
        </label>
      </div>
    </div>
  );
});