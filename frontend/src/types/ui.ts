export type ViewMode = 'guestScanner' | 'cvWritter' | 'userAdvisor' | 'userDashboard' | 'login';

export interface UserState {
    isLoggedIn: boolean;
    username: string;
    email: string;
}