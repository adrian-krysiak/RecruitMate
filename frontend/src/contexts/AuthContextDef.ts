import { createContext } from "react";
import { type UserState } from "../types/ui";
import { type RegisterRequest, type RegisterResponse } from "../types/api";

export interface AuthContextType {
  userState: UserState;
  handleLogin: (username: string, email: string) => void;
  handleLogout: () => Promise<void>;
  handleRegister: (payload: RegisterRequest) => Promise<RegisterResponse>;
  isLoading: boolean;
}

export const AuthContext = createContext<AuthContextType | undefined>(
  undefined
);
