import { type ViewMode } from '../types/ui';
import { ThemeToggle } from './ThemeToggle';
import styles from './Navbar.module.css';

interface NavbarProps {
    currentView: ViewMode;
    onViewChange: (view: ViewMode) => void;
    isLoggedIn: boolean;
    onLogout: () => void;
    onLogin?: () => void;
}

export const Navbar = ({ currentView, onViewChange, isLoggedIn, onLogout, onLogin }: NavbarProps) => {
    
    const getButtonClass = (viewName: ViewMode) => {
        return `${styles.navButton} ${currentView === viewName ? styles.active : ''}`;
    };

    return (
        <nav className={styles.nav}>
            <button 
                className={getButtonClass('guestScanner')}
                onClick={() => onViewChange('guestScanner')}
            >
                Guest Scanner
            </button>

            <button 
                className={getButtonClass('cvWritter')}
                onClick={() => onViewChange('cvWritter')}
                disabled={!isLoggedIn}
            >
                CV Writer
            </button>

            <button 
                className={getButtonClass('userAdvisor')}
                onClick={() => onViewChange('userAdvisor')} 
                disabled={!isLoggedIn}
            >
                User Advisor
            </button>



            <div className={styles.spacer}></div>

            <div className={styles.actionsContainer}>

                <button 
                    className={getButtonClass('userDashboard')}
                    onClick={() => onViewChange('userDashboard')} 
                    disabled={!isLoggedIn}
                >
                    User Dashboard
                </button>
                
                <ThemeToggle />

                {isLoggedIn ? (
                    <button 
                        className={styles.authButton} 
                        onClick={onLogout}
                    >
                        Logout
                    </button>
                ) : (
                   <button 
                        className={styles.authButton} 
                        // to do: view to log in, change state
                        // disabled={}
                        onClick={onLogin}
                   >
                        Login
                   </button>
                )}
            </div>
        </nav>
    );
};