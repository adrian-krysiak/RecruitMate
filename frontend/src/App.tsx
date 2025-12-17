import { GuestScanner } from './features/guest-mode/GuestScanner';
import './App.css';
import { useState } from 'react';
import { type ViewMode, type UserState } from './types/ui';
import { Navbar } from './components/Navbar';
import { authService } from './services/authService';

function App() {
    const [currentView, setCurrentView] = useState<ViewMode>('guestScanner');
    const [userState, setUserState] = useState<UserState>({
        isLoggedIn: false,
        username: '',
        email: ''
    });

    const handleLogout = async () => {
        await authService.logout();
        setUserState({ isLoggedIn: false, username: '', email: '' });
        setCurrentView('guestScanner');
    };

    const handleLogin = () => {
        // Placeholder login logic
        setUserState({ isLoggedIn: true, username: 'JohnDoe', email: 'john.doe@example.com' });
    };

    return (
        <div className="app-layout">
            <Navbar
                currentView={currentView}
                onViewChange={setCurrentView}
                isLoggedIn={userState.isLoggedIn}
                onLogout={handleLogout}
                onLogin={handleLogin}
            />

            <main style={{ padding: '2rem' }}>
                {currentView === 'guestScanner' && <GuestScanner isLoggedIn={userState.isLoggedIn} />}
                {currentView === 'cvWritter' && <div>CV Writter Component Placeholder</div>}
                {currentView === 'userAdvisor' && <div>User Advisor Component Placeholder</div>}
                {currentView === 'userDashboard' && <div>User Dashboard Component Placeholder</div>}
            </main>
        </div>
    );
}

export default App;