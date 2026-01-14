import { lazy, Suspense, useState, useCallback, type ReactNode } from 'react';
import { GuestScanner } from './features/guest-mode/GuestScanner';
import { Login } from './features/login/Login';
import './App.css';
import { VIEWS, type ViewMode } from './types/ui';
import { Navbar } from './components/Navbar';
import { useAuth } from './hooks/useAuth';
import { ErrorBoundary } from './components/ErrorBoundary';
import { LoadingOverlay } from './components/LoadingOverlay';

// Lazy load less frequently used components
const Dashboard = lazy(() => import('./features/dashboard/Dashboard').then(m => ({ default: m.Dashboard })));
const Register = lazy(() => import('./features/login/Register').then(m => ({ default: m.Register })));

// Feature-level error boundary wrapper component
const FeatureErrorBoundary = ({ children }: { children: ReactNode }) => (
    <ErrorBoundary fallback={<div className="error-fallback">Something went wrong. Please try again.</div>}>
        {children}
    </ErrorBoundary>
);

function App() {
    const [currentView, setCurrentView] = useState<ViewMode>(VIEWS.GUEST_SCANNER);
    const { userState, handleLogin, handleLogout, handleRegister } = useAuth();

    const onLogout = useCallback(async () => {
        await handleLogout();
        setCurrentView(VIEWS.GUEST_SCANNER);
    }, [handleLogout]);

    const onProfileUpdate = useCallback(() => {
        // Profile updated successfully
    }, []);

    return (
        <ErrorBoundary>
            <div className="app-layout">
                <Navbar
                    currentView={currentView}
                    onViewChange={setCurrentView}
                    isLoggedIn={userState.isLoggedIn}
                    isPremium={userState.isPremium}
                    onLogout={onLogout}
                />

                <main style={{ padding: '2rem' }}>
                    <Suspense fallback={<LoadingOverlay isVisible={true} message="Loading..." />}>
                        {currentView === VIEWS.LOGIN && (
                            <FeatureErrorBoundary>
                                <Login onLoginSuccess={handleLogin} onViewChange={setCurrentView} />
                            </FeatureErrorBoundary>
                        )}
                        {currentView === VIEWS.GUEST_SCANNER && (
                            <FeatureErrorBoundary>
                                <GuestScanner
                                    key={userState.isLoggedIn ? 'logged-in' : 'logged-out'}
                                    isLoggedIn={userState.isLoggedIn}
                                    isPremium={userState.isPremium}
                                />
                            </FeatureErrorBoundary>
                        )}
                        {currentView === VIEWS.CV_WRITER && (
                            <FeatureErrorBoundary>
                                <div>CV Writer Component Placeholder</div>
                            </FeatureErrorBoundary>
                        )}
                        {currentView === VIEWS.USER_ADVISOR && (
                            <FeatureErrorBoundary>
                                <div>User Advisor Component Placeholder</div>
                            </FeatureErrorBoundary>
                        )}
                        {currentView === VIEWS.USER_DASHBOARD && (
                            <FeatureErrorBoundary>
                                <Dashboard
                                    onViewChange={setCurrentView}
                                    onLogout={onLogout}
                                    onProfileUpdate={onProfileUpdate}
                                />
                            </FeatureErrorBoundary>
                        )}
                        {currentView === VIEWS.REGISTER && (
                            <FeatureErrorBoundary>
                                <Register
                                    onRegisterSuccess={handleRegister}
                                    onViewChange={setCurrentView}
                                />
                            </FeatureErrorBoundary>
                        )}
                    </Suspense>
                </main>
            </div>
        </ErrorBoundary>
    );
}

export default App;