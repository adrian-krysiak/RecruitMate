import { useState } from 'react';
import { type UserState } from '../types/ui';
import { authService } from '../services/authService';
import { type RegisterRequest, type RegisterResponse } from '../types/api';

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

    const handleRegister = async (payload: RegisterRequest): Promise<RegisterResponse> => {
        const response = await authService.register(payload);
        setUserState({
            isLoggedIn: true,
            username: response.user.username,
            email: response.user.email
        });
        return response;
    };

    return {
        userState,
        handleLogin,
        handleLogout,
        handleRegister
    };
};
