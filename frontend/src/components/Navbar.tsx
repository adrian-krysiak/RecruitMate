import { type ViewMode } from "../types/ui";
import { ThemeToggle } from "./ThemeToggle";
import styles from "./Navbar.module.css";
import { memo, useCallback } from "react";

interface NavbarProps {
    currentView: ViewMode;
    onViewChange: (view: ViewMode) => void;
    isLoggedIn: boolean;
    onLogout: () => void;
}

export const Navbar = memo(({
    currentView,
    onViewChange,
    isLoggedIn,
    onLogout,
}: NavbarProps) => {
    const getButtonClass = useCallback((viewName: ViewMode) => {
        return `${styles.navButton} ${currentView === viewName ? styles.active : ""}`;
    }, [currentView]);

    return (
        <nav className={styles.nav} aria-label="Main navigation">
            <button
                className={getButtonClass("guestScanner")}
                onClick={() => onViewChange("guestScanner")}
                aria-label="Go to Guest Scanner"
                aria-current={currentView === "guestScanner" ? "page" : undefined}
            >
                Guest Scanner
            </button>

            <button
                className={getButtonClass("cvWritter")}
                onClick={() => onViewChange("cvWritter")}
                disabled={!isLoggedIn}
                aria-label="Go to CV Writer (login required)"
                aria-current={currentView === "cvWritter" ? "page" : undefined}
            >
                CV Writer
            </button>

            <button
                className={getButtonClass("userAdvisor")}
                onClick={() => onViewChange("userAdvisor")}
                disabled={!isLoggedIn}
                aria-label="Go to User Advisor (login required)"
                aria-current={currentView === "userAdvisor" ? "page" : undefined}
            >
                User Advisor
            </button>

            <div className={styles.spacer}></div>

            <div className={styles.actionsContainer}>
                <button
                    className={getButtonClass("userDashboard")}
                    onClick={() => onViewChange("userDashboard")}
                    disabled={!isLoggedIn}
                    aria-label="Go to User Dashboard (login required)"
                    aria-current={currentView === "userDashboard" ? "page" : undefined}
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
                        onClick={() => onViewChange('login')}
                        aria-label="Login to your account"
                    >
                        Login
                    </button>
                )}
            </div>
        </nav>
    );
});
