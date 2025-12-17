import styles from '../GuestScanner.module.css';

interface ScannerControlsProps {
  inputMode: 'text' | 'file';
  setInputMode: (mode: 'text' | 'file') => void;
  isLoggedIn: boolean;
  useAiParsing: boolean;
  setUseAiParsing: (val: boolean) => void;
}

export const ScannerControls = ({
  inputMode,
  setInputMode,
  isLoggedIn,
  useAiParsing,
  setUseAiParsing
}: ScannerControlsProps) => {
  return (
    <div className={styles.controlsHeader}>
      <div className={styles.tabsContainer}>
        <button
          type="button"
          className={`${styles.tabButton} ${inputMode === 'text' ? styles.activeTab : ''}`}
          onClick={() => setInputMode('text')}
        >
          Paste Text
        </button>
        <button
          type="button"
          className={`${styles.tabButton} ${inputMode === 'file' ? styles.activeTab : ''}`}
          onClick={() => setInputMode('file')}
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
          />
          <span className={styles.slider}></span>
        </label>
      </div>
    </div>
  );
};