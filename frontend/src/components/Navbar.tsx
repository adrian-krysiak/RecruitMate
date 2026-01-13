import { VIEWS, type ViewMode } from "../types/ui";
import { ThemeToggle } from "./ThemeToggle";
import styles from "./Navbar.module.css";
import { memo, useCallback } from "react";

interface NavbarProps {
    currentView: ViewMode;
    onViewChange: (view: ViewMode) => void;
    isLoggedIn: boolean;
    isPremium: boolean;
    onLogout: () => void;
}

export const Navbar = memo(({
    currentView,
    onViewChange,
    isLoggedIn,
    isPremium,
    onLogout,
}: NavbarProps) => {
    const getButtonClass = useCallback((viewName: ViewMode) => {
        return `${styles.navButton} ${currentView === viewName ? styles.active : ""}`;
    }, [currentView]);

    return (
        <nav className={styles.nav} aria-label="Main navigation">
            <button
                className={getButtonClass(VIEWS.GUEST_SCANNER)}
                onClick={() => onViewChange(VIEWS.GUEST_SCANNER)}
                aria-label="Go to Guest Scanner"
                aria-current={currentView === VIEWS.GUEST_SCANNER ? "page" : undefined}
            >
                Guest Scanner
            </button>

            <button
                className={getButtonClass(VIEWS.CV_WRITER)}
                onClick={() => onViewChange(VIEWS.CV_WRITER)}
                disabled={!isLoggedIn || !isPremium}
                aria-label="Go to CV Writer (Premium)"
                aria-current={currentView === VIEWS.CV_WRITER ? "page" : undefined}
                title={!isPremium ? "Premium feature" : ""}
            >
                CV Writer {!isPremium && "🔒"}
            </button>

            <button
                className={getButtonClass(VIEWS.USER_ADVISOR)}
                onClick={() => onViewChange(VIEWS.USER_ADVISOR)}
                disabled={!isLoggedIn || !isPremium}
                aria-label="Go to User Advisor (Premium)"
                aria-current={currentView === VIEWS.USER_ADVISOR ? "page" : undefined}
                title={!isPremium ? "Premium feature" : ""}
            >
                User Advisor {!isPremium && "🔒"}
            </button>

            <div className={styles.spacer}></div>

            <div className={styles.actionsContainer}>
                <button
                    className={getButtonClass(VIEWS.USER_DASHBOARD)}
                    onClick={() => onViewChange(VIEWS.USER_DASHBOARD)}
                    disabled={!isLoggedIn}
                    aria-label="Go to User Dashboard (login required)"
                    aria-current={currentView === VIEWS.USER_DASHBOARD ? "page" : undefined}
                >
                    User Dashboard
                </button>

                <ThemeToggle />

                {isLoggedIn ? (
                    <button
                        className={styles.authButton}
                        onClick={onLogout}
                        aria-label="Logout from your account"
                    >
                        Logout
                    </button>
                ) : (
                    <button
                        className={styles.authButton}
                        onClick={() => onViewChange(VIEWS.LOGIN)}
                        aria-label="Login to your account"
                    >
                        Login
                    </button>
                )}
            </div>
        </nav>
    );
});

Navbar.displayName = 'Navbar';
