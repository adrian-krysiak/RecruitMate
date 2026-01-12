import { GuestScanner } from './features/guest-mode/GuestScanner';
import { Login } from './features/login/Login';
import './App.css';
import { useState, useCallback } from 'react';
import { type ViewMode } from './types/ui';
import { Navbar } from './components/Navbar';
import { useAuth } from './hooks/useAuth';
import { Register } from './features/login/Register';
import { ErrorBoundary } from './components/ErrorBoundary';

function App() {
    const [currentView, setCurrentView] = useState<ViewMode>('guestScanner');
    const { userState, handleLogin, handleLogout, handleRegister } = useAuth();

    const onLogout = useCallback(async () => {
        await handleLogout();
        setCurrentView('guestScanner');
    }, [handleLogout]);

    return (
        <ErrorBoundary>
            <div className="app-layout">
                <Navbar
                    currentView={currentView}
                    onViewChange={setCurrentView}
                    isLoggedIn={userState.isLoggedIn}
                    onLogout={onLogout}
                />

                <main style={{ padding: '2rem' }}>
                    {currentView === 'login' && <Login onLoginSuccess={handleLogin} onViewChange={setCurrentView} />}
                    {currentView === 'guestScanner' && <GuestScanner isLoggedIn={userState.isLoggedIn} />}
                    {currentView === 'cvWritter' && <div>CV Writer Component Placeholder</div>}
                    {currentView === 'userAdvisor' && <div>User Advisor Component Placeholder</div>}
                    {currentView === 'userDashboard' && <div>User Dashboard Component Placeholder</div>}
                    {currentView === 'register' && (
                        <Register
                            onRegisterSuccess={handleRegister}
                            onViewChange={setCurrentView}
                        />
                    )}
                </main>
            </div>
        </ErrorBoundary>
    );
}

export default App;