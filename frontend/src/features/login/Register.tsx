import { useState } from 'react';
import { isAxiosError } from 'axios';
import { type RegisterRequest, type RegisterResponse } from '../../types/api';
import { type ViewMode } from '../../types/ui';
import { ErrorMessage } from '../guest-mode/components/ErrorMessage';
import { LoadingOverlay } from '../../components/LoadingOverlay';
import styles from './Register.module.css';

interface RegisterProps {
    onRegisterSuccess: (payload: RegisterRequest) => Promise<RegisterResponse>;
    onViewChange: (view: ViewMode) => void;
}

export const Register = ({ onRegisterSuccess, onViewChange }: RegisterProps) => {
    const [formData, setFormData] = useState<RegisterRequest & { confirmPassword: string }>(
        {
            username: '',
            email: '',
            password: '',
            confirmPassword: ''
        }
    );
    const [error, setError] = useState<Error | null>(null);
    const [isLoading, setIsLoading] = useState(false);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
        if (error) setError(null);
    };

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        setError(null);

        if (formData.password !== formData.confirmPassword) {
            setError(new Error('Passwords do not match.'));
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
    };

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
                                type="password"
                                id="password"
                                name="password"
                                value={formData.password}
                                onChange={handleChange}
                                placeholder="Enter a secure password"
                                className={styles.input}
                                disabled={isLoading}
                                required
                                minLength={6}
                            />
                        </div>

                        <div className={styles.formGroup}>
                            <label htmlFor="confirmPassword" className={styles.label}>Confirm Password</label>
                            <input
                                type="password"
                                id="confirmPassword"
                                name="confirmPassword"
                                value={formData.confirmPassword}
                                onChange={handleChange}
                                placeholder="Re-enter your password"
                                className={styles.input}
                                disabled={isLoading}
                                required
                                minLength={6}
                            />
                        </div>

                        {error && <ErrorMessage error={error} />}

                        <button
                            type="submit"
                            className={styles.submitButton}
                            disabled={
                                isLoading ||
                                !formData.username ||
                                !formData.email ||
                                !formData.password ||
                                !formData.confirmPassword
                            }
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
};
