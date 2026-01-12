import { useCallback, type ReactNode } from 'react';
import { useState } from 'react';
import { type UserState } from '../types/ui';
import { authService } from '../services/authService';
import { type RegisterRequest, type RegisterResponse } from '../types/api';
import { AuthContext } from './AuthContextDef';

interface AuthProviderProps {
    children: ReactNode;
}

export const AuthProvider = ({ children }: AuthProviderProps) => {
    const [userState, setUserState] = useState<UserState>(() => {
        try {
            const storedUser = authService.getStoredUser();
            const storedToken = authService.getStoredToken();

            if (storedUser && storedToken) {
                return {
                    isLoggedIn: true,
                    username: storedUser.username,
                    email: storedUser.email
                };
            }
        } catch (error) {
            console.error('Error loading stored auth state:', error);
        }
        return { isLoggedIn: false, username: '', email: '' };
    });

    const [isLoading, setIsLoading] = useState(false);

    const handleLogin = useCallback((username: string, email: string) => {
        setUserState({ isLoggedIn: true, username, email });
    }, []);

    const handleLogout = useCallback(async () => {
        setIsLoading(true);
        try {
            await authService.logout();
            setUserState({ isLoggedIn: false, username: '', email: '' });
        } finally {
            setIsLoading(false);
        }
    }, []);

    const handleRegister = useCallback(async (payload: RegisterRequest): Promise<RegisterResponse> => {
        setIsLoading(true);
        try {
            const response = await authService.register(payload);
            setUserState({
                isLoggedIn: true,
                username: response.user.username,
                email: response.user.email
            });
            return response;
        } finally {
            setIsLoading(false);
        }
    }, []);

    const value = {
        userState,
        handleLogin,
        handleLogout,
        handleRegister,
        isLoading
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
