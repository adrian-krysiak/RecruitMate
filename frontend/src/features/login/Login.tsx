import { useState, useCallback, memo } from 'react';
import { type LoginRequest } from '../../types/api';
import { VIEWS, type ViewMode } from '../../types/ui';
import { authService } from '../../services/authService';
import { ErrorMessage } from '../guest-mode/components/ErrorMessage';
import { LoadingOverlay } from '../../components/LoadingOverlay';
import { toError } from '../../utils/errorHandler';
import styles from './Login.module.css';

interface LoginProps {
    onLoginSuccess: (username: string, email: string, isPremium?: boolean) => void;
    onViewChange: (view: ViewMode) => void;
}

export const Login = memo(({ onLoginSuccess, onViewChange }: LoginProps) => {
    const [formData, setFormData] = useState<LoginRequest>({
        username_email: '',
        password: '',
    });
    const [showPassword, setShowPassword] = useState(false);
    const [error, setError] = useState<Error | null>(null);
    const [isLoading, setIsLoading] = useState(false);

    const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
        // Clear error when user starts typing
        if (error) setError(null);
    }, [error]);

    const handleSubmit = useCallback(async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        setError(null);
        setIsLoading(true);

        try {
            const response = await authService.login(formData);
            const isPremium = response.user.is_premium ?? false;
            onLoginSuccess(response.user.username, response.user.email, isPremium);
            onViewChange(VIEWS.GUEST_SCANNER);
        } catch (err) {
            setError(toError(err));
        } finally {
            setIsLoading(false);
        }
    }, [formData, onLoginSuccess, onViewChange]);

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
                                id="username_email"
                                name="username_email"
                                value={formData.username_email}
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
                                type={showPassword ? 'text' : 'password'}
                                id="password"
                                name="password"
                                value={formData.password}
                                onChange={handleChange}
                                placeholder="Enter your password"
                                className={styles.input}
                                disabled={isLoading}
                                required

                                autoComplete="current-password"
                            />
                            <label className={styles.checkboxLabel}>
                                <input
                                    type="checkbox"
                                    checked={showPassword}
                                    onChange={() => setShowPassword(prev => !prev)}
                                    disabled={isLoading}
                                    aria-label="Show password"
                                />
                                Show password
                            </label>
                        </div>

                        {error && <ErrorMessage error={error} />}

                        <button
                            type="submit"
                            className={styles.submitButton}
                            disabled={isLoading || !formData.username_email || !formData.password}
                        >
                            {isLoading ? 'Logging in...' : 'Login'}
                        </button>
                    </form>

                    <div className={styles.authSwitch}>
                        <span>Don't have an account?</span>
                        <button
                            type="button"
                            className={styles.linkButton}
                            onClick={() => onViewChange(VIEWS.REGISTER)}
                            disabled={isLoading}
                        >
                            Create one
                        </button>
                    </div>

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
});

Login.displayName = 'Login';
