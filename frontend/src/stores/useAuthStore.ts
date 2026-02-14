import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { TokenData, TokenResponse } from '../types';
import { jwtDecode } from "jwt-decode";

interface AuthState {
    isLoggedIn: boolean;
    accountId: string | null;
    access: string | null;
    showLoginModal: boolean;
    setShowLoginModal: (value: boolean) => void;
    login: (response: TokenResponse) => void;
    logout: () => void;
}

export function decodeToken(token: string): TokenData {
    try {
        return jwtDecode<TokenData>(token);
    } catch (error) {
        console.error('Invalid token:', error);
        return {};
    }
}

export const useAuthStore = create<AuthState>()(
    persist(
        (set) => ({
            isLoggedIn: false,
            accountId: null,
            access: null,
            showLoginModal: false,
            setShowLoginModal: (value) =>
                set(() => ({
                    showLoginModal: value,
                })),
            login: (response) =>
                set(() => ({
                    access: response.access_token,
                    accountId: decodeToken(response.access_token).sub,
                    isLoggedIn: true,
                })),
            logout: () =>
                set(() => ({
                    access: null,
                    user: null,
                    isLoggedIn: false,
                })),
        }),
        {
            name: 'auth-storage',
            partialize: (state) => ({
                access: state.access,
                accountId: state.accountId,
                isLoggedIn: state.isLoggedIn,
            }),
        }
    )
);
