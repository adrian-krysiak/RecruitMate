import styles from './LoadingOverlay.module.css';

interface LoadingOverlayProps {
    isVisible: boolean;
    message?: string;
}

export const LoadingOverlay = ({ isVisible, message = 'Loading...' }: LoadingOverlayProps) => {
    if (!isVisible) return null;

    return (
        <div className={styles.overlay}>
            <div className={styles.content}>
                <div className={styles.spinner}></div>
                <p className={styles.message}>{message}</p>
            </div>
        </div>
    );
};
