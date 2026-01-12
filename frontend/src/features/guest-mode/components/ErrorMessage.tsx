import { isAxiosError } from 'axios';
import { type FastApiValidationError, type GeneralServerError } from '../../../types/api';
import { HTTP_STATUS } from '../../../constants';
import styles from './ErrorMessage.module.css';
import { memo } from 'react';

interface ErrorMessageProps {
  error: Error | null;
}

export const ErrorMessage = memo(({ error }: ErrorMessageProps) => {
  if (!error) return null;

  if (isAxiosError(error)) {
    if (error.response?.status === HTTP_STATUS.UNPROCESSABLE_ENTITY) {
      const data = error.response.data as FastApiValidationError;

      if (Array.isArray(data.detail)) {
        return (
          <div className={styles.container} role="alert">
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
        <div className={styles.container} role="alert">
          <span className={styles.title}>Validation Error:</span>
          {String(data.detail)}
        </div>
      );
    }

    return (
      <div className={styles.container} role="alert">
        <span className={styles.title}>
          Server Error ({error.response?.status}):
        </span>
        {(error.response?.data as GeneralServerError)?.message || error.message}
      </div>
    );
  }

  // Handle multiline error messages (split by \n)
  const errorLines = error.message.split('\n').filter(line => line.trim());

  if (errorLines.length > 1) {
    return (
      <div className={styles.container} role="alert">
        <ul className={styles.list}>
          {errorLines.map((line, idx) => (
            <li key={idx} className={styles.listItem}>
              {line}
            </li>
          ))}
        </ul>
      </div>
    );
  }

  return (
    <div className={styles.container} role="alert">
      {error.message}
    </div>
  );
});