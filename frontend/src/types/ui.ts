export type ViewMode = 'guestScanner' | 'cvWritter' | 'userAdvisor' | 'userDashboard' | 'login' | 'register';

export interface UserState {
    isLoggedIn: boolean;
    username: string;
    email: string;
}