import { isAxiosError } from 'axios';
import { type FastApiValidationError, type GeneralServerError } from '../../../types/api';
import styles from './ErrorMessage.module.css';

interface ErrorMessageProps {
  error: Error | null;
}

export const ErrorMessage = ({ error }: ErrorMessageProps) => {
  if (!error) return null;

  if (isAxiosError(error)) {
    if (error.response?.status === 422) {
      const data = error.response.data as FastApiValidationError;

      if (Array.isArray(data.detail)) {
        return (
          <div className={styles.container}>
            <span className={styles.title}>Validation Failed:</span>
            <ul className={styles.list}>
              {data.detail.map((err, idx) => {
                const fieldName = err.loc[err.loc.length - 1];
                return (
                  <li key={idx} className={styles.listItem}>
                    <span className={styles.field}>{fieldName}</span>: {err.msg}
                  </li>
                );
              })}
            </ul>
          </div>
        );
      }

      return (
        <div className={styles.container}>
          <span className={styles.title}>Validation Error:</span>
          {String(data.detail)}
        </div>
      );
    }

    return (
      <div className={styles.container}>
        <span className={styles.title}>
            Server Error ({error.response?.status}):
        </span>
        {(error.response?.data as GeneralServerError)?.message || error.message}
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <span className={styles.title}>Application Error:</span>
      {error.message}
    </div>
  );
};