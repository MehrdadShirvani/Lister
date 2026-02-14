// pages/AuthPage.tsx
import React, { useState } from 'react';
import styles from './AuthPage.module.css';
import { WelcomeMessage } from './WelomeMessage';
import { AuthCard } from './AuthCard';
import { SignInForm } from './SignInForm';
import { SignUpForm } from './SignUpForm';

type AuthMode = 'signin' | 'signup';

export const AuthPage: React.FC = () => {
  const [mode, setMode] = useState<AuthMode>('signin');

  return (
    <div className={styles.container}>
      <div className={styles.content}>
        <WelcomeMessage />
        <AuthCard>
          {mode === 'signin' ? (
            <SignInForm onToggleMode={() => setMode('signup')} />
          ) : (
            <SignUpForm onToggleMode={() => setMode('signin')} />
          )}
        </AuthCard>
      </div>
      
      {/* Decorative elements for warmth */}
      <div className={styles.ambientGlow} />
      <div className={styles.ambientGlow2} />
    </div>
  );
};