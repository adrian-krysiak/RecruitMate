// View name constants for type-safe navigation
export const VIEWS = {
    GUEST_SCANNER: 'guestScanner',
    CV_WRITER: 'cvWriter',
    USER_ADVISOR: 'userAdvisor',
    USER_DASHBOARD: 'userDashboard',
    LOGIN: 'login',
    REGISTER: 'register',
} as const;

export type ViewMode = (typeof VIEWS)[keyof typeof VIEWS];

export interface UserState {
    isLoggedIn: boolean;
    username: string;
    email: string;
    firstName?: string;
    lastName?: string;
    birthDate?: string;
    fullName?: string;
    isPremium: boolean;
}