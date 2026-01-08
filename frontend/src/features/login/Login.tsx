import { useState } from 'react';
import { isAxiosError } from 'axios';
import { type LoginRequest } from '../../types/api';
import { type ViewMode } from '../../types/ui';
import { authService } from '../../services/authService';
import { ErrorMessage } from '../guest-mode/components/ErrorMessage';
import { LoadingOverlay } from '../../components/LoadingOverlay';
import styles from './Login.module.css';

interface LoginProps {
    onLoginSuccess: (username: string, email: string) => void;
    onViewChange: (view: ViewMode) => void;
}

export const Login = ({ onLoginSuccess, onViewChange }: LoginProps) => {
    const [formData, setFormData] = useState<LoginRequest>({
        username: '',
        password: '',
    });
    const [error, setError] = useState<Error | null>(null);
    const [isLoading, setIsLoading] = useState(false);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
        // Clear error when user starts typing
        if (error) setError(null);
    };

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        setError(null);
        setIsLoading(true);

        try {
            const response = await authService.login(formData);
            onLoginSuccess(response.user.username, response.user.email);
            onViewChange('guestScanner');
        } catch (err) {
            if (isAxiosError(err)) {
                setError(new Error(
                    err.response?.data?.message ||
                    err.response?.data?.detail ||
                    'Login failed. Please check your credentials.'
                ));
            } else {
                setError(err instanceof Error ? err : new Error('An unexpected error occurred'));
            }
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <>
            <LoadingOverlay isVisible={isLoading} message="Logging in..." />
            <div className={styles.container}>
                <div className={styles.formWrapper}>
                    <h1 className={styles.title}>Login</h1>
                <p className={styles.subtitle}>Sign in to your RecruitMate account</p>

                <form onSubmit={handleSubmit} className={styles.form}>
                    <div className={styles.formGroup}>
                        <label htmlFor="username" className={styles.label}>
                            Username or Email
                        </label>
                        <input
                            type="text"
                            id="username"
                            name="username"
                            value={formData.username}
                            onChange={handleChange}
                            placeholder="Enter your username or email"
                            className={styles.input}
                            disabled={isLoading}
                            required
                        />
                    </div>

                    <div className={styles.formGroup}>
                        <label htmlFor="password" className={styles.label}>
                            Password
                        </label>
                        <input
                            type="password"
                            id="password"
                            name="password"
                            value={formData.password}
                            onChange={handleChange}
                            placeholder="Enter your password"
                            className={styles.input}
                            disabled={isLoading}
                            required
                        />
                    </div>

                    {error && <ErrorMessage error={error} />}

                    <button
                        type="submit"
                        className={styles.submitButton}
                        disabled={isLoading || !formData.username || !formData.password}
                    >
                        {isLoading ? 'Logging in...' : 'Login'}
                    </button>
                </form>

                <div className={styles.futureAuthHint}>
                    <p>Social sign-in coming soon!</p>
                    <div className={styles.socialPlaceholder}>
                        <span>Google • Microsoft • Apple</span>
                    </div>
                </div>
            </div>
        </div>
        </>
    );
};
