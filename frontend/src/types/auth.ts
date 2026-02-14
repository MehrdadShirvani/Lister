import type { AccountResponse } from "./account";

// Signup request
export interface UserSignup {
    first_name: string;
    last_name: string;
    email: string;
    password: string;
}

// Login request
export interface UserLogin {
    username: string;
    password: string;
}

// Token response
export interface TokenResponse {
    access_token: string;
    token_type: string;
}

// Token data (decoded JWT)
export interface TokenData {
    sub?: string; // user_id
    email?: string;
    exp?: number;
}

// Auth state for frontend
export interface AuthState {
    isAuthenticated: boolean;
    user: AccountResponse | null;
    token: string | null;
    loading: boolean;
    error: string | null;
}