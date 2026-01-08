import { useState } from 'react';
import { type UserState } from '../types/ui';
import { authService } from '../services/authService';

export const useAuth = () => {
    const [userState, setUserState] = useState<UserState>(() => {
        const storedUser = authService.getStoredUser();
        const storedToken = authService.getStoredToken();

        if (storedUser && storedToken) {
            return {
                isLoggedIn: true,
                username: storedUser.username,
                email: storedUser.email
            };
        }
        return { isLoggedIn: false, username: '', email: '' };
    });

    const handleLogin = (username: string, email: string) => {
        setUserState({ isLoggedIn: true, username, email });
    };

    const handleLogout = async () => {
        await authService.logout();
        setUserState({ isLoggedIn: false, username: '', email: '' });
    };

    return {
        userState,
        handleLogin,
        handleLogout
    };
};
