import { useState, useEffect, useCallback, memo, useMemo } from 'react';
import { VIEWS, type ViewMode } from '../../types/ui';
import { type User } from '../../types/api';
import { authService } from '../../services/authService';
import { ErrorMessage } from '../guest-mode/components/ErrorMessage';
import { LoadingOverlay } from '../../components/LoadingOverlay';
import { toError } from '../../utils/errorHandler';
import styles from './Dashboard.module.css';

interface DashboardProps {
    onViewChange: (view: ViewMode) => void;
    onLogout: () => Promise<void>;
    onProfileUpdate?: (user: User) => void;
}

export const Dashboard = memo(({
    onViewChange,
    onLogout,
    onProfileUpdate
}: DashboardProps) => {
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [isSaving, setIsSaving] = useState(false);
    const [error, setError] = useState<Error | null>(null);
    const [successMessage, setSuccessMessage] = useState('');
    const [formData, setFormData] = useState({
        username: '',
        first_name: '',
        last_name: '',
        birth_date: ''
    });

    useEffect(() => {
        const loadProfile = async () => {
            try {
                setIsLoading(true);
                const profile = await authService.getUserProfile();
                setUser(profile);
                setSuccessMessage('');
                setFormData({
                    username: profile.username || '',
                    first_name: profile.first_name || '',
                    last_name: profile.last_name || '',
                    birth_date: profile.birth_date || ''
                });
            } catch (err) {
                setError(toError(err));
            } finally {
                setIsLoading(false);
            }
        };

        loadProfile();
    }, []);

    const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
        if (error) setError(null);
        if (successMessage) setSuccessMessage('');
    }, [error, successMessage]);

    const handleSubmit = useCallback(async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        setError(null);
        setSuccessMessage('');
        setIsSaving(true);

        try {
            const updated = await authService.updateUserProfile({
                username: formData.username,
                first_name: formData.first_name,
                last_name: formData.last_name,
                birth_date: formData.birth_date || undefined
            });
            setUser(updated);
            onProfileUpdate?.(updated);
            setSuccessMessage('Profile updated successfully!');
        } catch (err) {
            setError(toError(err));
        } finally {
            setIsSaving(false);
        }
    }, [formData, onProfileUpdate]);

    const handleDeleteAccount = useCallback(async () => {
        if (!window.confirm(
            'Are you sure you want to delete your account? This action cannot be undone.'
        )) {
            return;
        }

        setIsSaving(true);
        try {
            await authService.deleteAccount();
            await onLogout();
            onViewChange(VIEWS.GUEST_SCANNER);
        } catch (err) {
            setError(toError(err));
        } finally {
            setIsSaving(false);
        }
    }, [onLogout, onViewChange]);

    const displayFullName = useMemo(() => {
        if (!user?.full_name || user.full_name === user.username) return 'Not set';
        return user.full_name;
    }, [user]);

    if (isLoading) {
        return <LoadingOverlay isVisible={true} message="Loading profile..." />;
    }

    return (
        <>
            <LoadingOverlay isVisible={isSaving} message="Saving changes..." />
            <div className={styles.container}>
                <div className={styles.formWrapper}>
                    <h1 className={styles.title}>My Profile</h1>
                    <p className={styles.subtitle}>Manage your account information</p>

                    {user && (
                        <div className={`${styles.userInfo} ${styles.userInfoGrid}`}>
                            <div className={`${styles.infoPair} ${styles.infoEmail}`}>
                                <span className={styles.infoLabel}>Email</span>
                                <span className={styles.infoValue}>{user.email}</span>
                            </div>
                            <div className={`${styles.infoPair} ${styles.infoFullName}`}>
                                <span className={styles.infoLabel}>Full Name</span>
                                <span className={styles.infoValue}>{displayFullName}</span>
                            </div>
                            <div className={`${styles.infoPair} ${styles.infoStatus}`}>
                                <span className={styles.infoLabel}>Status</span>
                                <span className={`${styles.badge} ${user.is_premium ? styles.badgePremium : styles.badgeStandard}`}>
                                    {user.is_premium ? 'Premium Member' : 'Standard Member'}
                                </span>
                            </div>
                        </div>
                    )}

                    {successMessage && (
                        <div className={styles.successMessage} role="status">{successMessage}</div>
                    )}

                    <form onSubmit={handleSubmit} className={styles.form}>
                        <div className={styles.formGroup}>
                            <label htmlFor="username" className={styles.label}>
                                Username
                            </label>
                            <input
                                type="text"
                                id="username"
                                name="username"
                                value={formData.username}
                                onChange={handleChange}
                                className={styles.input}
                                disabled={isSaving}
                                required
                            />
                        </div>

                        <div className={styles.formGroup}>
                            <label htmlFor="first_name" className={styles.label}>
                                First Name
                            </label>
                            <input
                                type="text"
                                id="first_name"
                                name="first_name"
                                value={formData.first_name}
                                onChange={handleChange}
                                className={styles.input}
                                disabled={isSaving}
                            />
                        </div>

                        <div className={styles.formGroup}>
                            <label htmlFor="last_name" className={styles.label}>
                                Last Name
                            </label>
                            <input
                                type="text"
                                id="last_name"
                                name="last_name"
                                value={formData.last_name}
                                onChange={handleChange}
                                className={styles.input}
                                disabled={isSaving}
                            />
                        </div>

                        <div className={styles.formGroup}>
                            <label htmlFor="birth_date" className={styles.label}>
                                Birth Date
                            </label>
                            <input
                                type="date"
                                id="birth_date"
                                name="birth_date"
                                value={formData.birth_date}
                                onChange={handleChange}
                                className={styles.input}
                                disabled={isSaving}
                            />
                        </div>

                        {error && <ErrorMessage error={error} />}

                        <div className={styles.buttonGroup}>
                            <button
                                type="submit"
                                className={styles.submitButton}
                                disabled={isSaving}
                            >
                                {isSaving ? 'Saving...' : 'Save Changes'}
                            </button>
                            <button
                                type="button"
                                className={styles.deleteButton}
                                onClick={handleDeleteAccount}
                                disabled={isSaving}
                            >
                                Delete Account
                            </button>
                        </div>
                    </form>
                </div>
            </div>
        </>
    );
});

Dashboard.displayName = 'Dashboard';
