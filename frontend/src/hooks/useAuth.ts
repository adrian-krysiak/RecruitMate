import { useState, useCallback } from 'react';
import { type UserState } from '../types/ui';
import { authService } from '../services/authService';
import { type RegisterRequest, type RegisterResponse, type User } from '../types/api';

export const useAuth = () => {
    const [userState, setUserState] = useState<UserState>(() => {
        const storedUser = authService.getStoredUser();
        const storedToken = authService.getStoredToken();

        if (storedUser && storedToken) {
            return {
                isLoggedIn: true,
                username: storedUser.username,
                email: storedUser.email,
                firstName: storedUser.first_name,
                lastName: storedUser.last_name,
                birthDate: storedUser.birth_date,
                fullName: storedUser.full_name,
                isPremium: storedUser.is_premium ?? false
            };
        }
        return { isLoggedIn: false, username: '', email: '', isPremium: false };
    });

    const handleLogin = useCallback((username: string, email: string, isPremium: boolean = false) => {
        setUserState({ isLoggedIn: true, username, email, isPremium });
    }, []);

    const handleLogout = useCallback(async () => {
        await authService.logout();
        setUserState({ isLoggedIn: false, username: '', email: '', isPremium: false });
    }, []);

    const handleRegister = useCallback(async (payload: RegisterRequest): Promise<RegisterResponse> => {
        const response = await authService.register(payload);
        setUserState({
            isLoggedIn: true,
            username: response.user.username,
            email: response.user.email,
            isPremium: false
        });
        return response;
    }, []);

    const updateProfile = useCallback((user: User) => {
        setUserState((prev) => ({
            ...prev,
            username: user.username || prev.username,
            email: user.email || prev.email,
            firstName: user.first_name,
            lastName: user.last_name,
            birthDate: user.birth_date,
            fullName: user.full_name,
            isPremium: user.is_premium
        }));
    }, []);

    return {
        userState,
        handleLogin,
        handleLogout,
        handleRegister,
        updateProfile
    };
};
