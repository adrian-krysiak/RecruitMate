export type ViewMode = 'guestScanner' | 'cvWritter' | 'userAdvisor' | 'userDashboard';

export interface UserState {
    isLoggedIn: boolean;
    username: string;
    email: string;
}