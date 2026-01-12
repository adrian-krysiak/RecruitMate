import { useState, useCallback, memo } from 'react';
import { isAxiosError } from 'axios';
import { type RegisterRequest, type RegisterResponse } from '../../types/api';
import { type ViewMode } from '../../types/ui';
import { MATCH_CONFIG } from '../../constants';
import { validateEmail, validatePassword, validateUsername } from '../../utils/validation';
import { ErrorMessage } from '../guest-mode/components/ErrorMessage';
import { LoadingOverlay } from '../../components/LoadingOverlay';
import styles from './Register.module.css';

interface RegisterProps {
    onRegisterSuccess: (payload: RegisterRequest) => Promise<RegisterResponse>;
    onViewChange: (view: ViewMode) => void;
}

export const Register = memo(({ onRegisterSuccess, onViewChange }: RegisterProps) => {
    const [formData, setFormData] = useState<RegisterRequest & { confirmPassword: string }>(
        {
            username: '',
            email: '',
            password: '',
            confirmPassword: ''
        }
    );
    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);
    const [error, setError] = useState<Error | null>(null);
    const [isLoading, setIsLoading] = useState(false);

    const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
        if (error) setError(null);
    }, [error]);

    const handleSubmit = useCallback(async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        setError(null);

        // Client-side validations
        const usernameValidation = validateUsername(formData.username);
        if (!usernameValidation.isValid) {
            setError(new Error(usernameValidation.errors.join('\n')));
            return;
        }

        if (!validateEmail(formData.email)) {
            setError(new Error('Please enter a valid email address.'));
            return;
        }

        if (formData.password !== formData.confirmPassword) {
            setError(new Error('Passwords do not match.'));
            return;
        }

        const passwordValidation = validatePassword(formData.password);
        if (!passwordValidation.isValid) {
            setError(new Error(passwordValidation.errors.join('\n')));
            return;
        }

        setIsLoading(true);
        try {
            await onRegisterSuccess({
                username: formData.username,
                email: formData.email,
                password: formData.password
            });
            onViewChange('userDashboard');
        } catch (err) {
            if (isAxiosError(err)) {
                setError(new Error(
                    err.response?.data?.message ||
                    err.response?.data?.detail ||
                    'Registration failed. Please review your details.'
                ));
            } else {
                setError(err instanceof Error ? err : new Error('An unexpected error occurred'));
            }
        } finally {
            setIsLoading(false);
        }
    }, [formData, onRegisterSuccess, onViewChange]);

    return (
        <>
            <LoadingOverlay isVisible={isLoading} message="Creating your account..." />
            <div className={styles.container}>
                <div className={styles.formWrapper}>
                    <h1 className={styles.title}>Create Account</h1>
                    <p className={styles.subtitle}>Join RecruitMate in seconds</p>

                    <form onSubmit={handleSubmit} className={styles.form}>
                        <div className={styles.formGroup}>
                            <label htmlFor="username" className={styles.label}>Username</label>
                            <input
                                type="text"
                                id="username"
                                name="username"
                                value={formData.username}
                                onChange={handleChange}
                                placeholder="Choose a username"
                                className={styles.input}
                                disabled={isLoading}
                                required
                            />
                        </div>

                        <div className={styles.formGroup}>
                            <label htmlFor="email" className={styles.label}>Email</label>
                            <input
                                type="email"
                                id="email"
                                name="email"
                                value={formData.email}
                                onChange={handleChange}
                                placeholder="you@example.com"
                                className={styles.input}
                                disabled={isLoading}
                                required
                            />
                        </div>

                        <div className={styles.formGroup}>
                            <label htmlFor="password" className={styles.label}>Password</label>
                            <input
                                type={showPassword ? 'text' : 'password'}
                                id="password"
                                name="password"
                                value={formData.password}
                                onChange={handleChange}
                                placeholder="Enter a secure password"
                                className={styles.input}
                                disabled={isLoading}
                                required
                                minLength={MATCH_CONFIG.MIN_PASSWORD_LENGTH}
                                autoComplete="new-password"
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

                        <div className={styles.formGroup}>
                            <label htmlFor="confirmPassword" className={styles.label}>Confirm Password</label>
                            <input
                                type={showConfirmPassword ? 'text' : 'password'}
                                id="confirmPassword"
                                name="confirmPassword"
                                value={formData.confirmPassword}
                                onChange={handleChange}
                                placeholder="Re-enter your password"
                                className={styles.input}
                                disabled={isLoading}
                                required
                                minLength={MATCH_CONFIG.MIN_PASSWORD_LENGTH}
                                autoComplete="new-password"
                            />
                            <label className={styles.checkboxLabel}>
                                <input
                                    type="checkbox"
                                    checked={showConfirmPassword}
                                    onChange={() => setShowConfirmPassword(prev => !prev)}
                                    disabled={isLoading}
                                    aria-label="Show confirm password"
                                />
                                Show password
                            </label>
                        </div>

                        {error && <ErrorMessage error={error} />}

                        <button
                            type="submit"
                            className={styles.submitButton}
                            disabled={isLoading}
                        >
                            {isLoading ? 'Creating account...' : 'Create account'}
                        </button>
                    </form>

                    <div className={styles.authSwitch}>
                        <span>Already have an account?</span>
                        <button
                            type="button"
                            className={styles.linkButton}
                            onClick={() => onViewChange('login')}
                            disabled={isLoading}
                        >
                            Back to login
                        </button>
                    </div>
                </div>
            </div>
        </>
    );
});
