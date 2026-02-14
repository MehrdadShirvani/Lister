// components/auth/SignInForm.tsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import type { UserLogin } from '../../types/auth';
import styles from './AuthForm.module.css';
import { useAuthStore } from '../../stores/useAuthStore';
import api from '../../services/api';

interface SignInFormProps {
  onToggleMode: () => void;
}

export const SignInForm: React.FC<SignInFormProps> = ({ onToggleMode }) => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState<UserLogin>({
    username: '',
    password: '',
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [focusedField, setFocusedField] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    // Clear error when user starts typing
    if (error) setError(null);
  };

  const handleFocus = (fieldName: string) => {
    setFocusedField(fieldName);
  };

  const handleBlur = () => {
    setFocusedField(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const response = await api.Auth.login(formData);
      // Assuming the login function returns TokenResponse
      useAuthStore.getState().login(response);
      navigate('/dashboard');
    } catch (err: any) {
      // Handle different types of errors gracefully
      let errorMessage = 'Unable to sign in. Please try again.';
      if (err.response) {
        if (err.response.status === 401) {
          errorMessage = 'The email or password you entered is incorrect.';
        } else if (err.response.status === 404) {
          errorMessage = 'No account found with this email address.';
        } else if (err.response.data?.message) {
          errorMessage = err.response.data.message;
        }
      } else if (err.request) {
        // The request was made but no response was received
        errorMessage = 'Unable to connect. Please check your connection.';
      }
      
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className={styles.form}>
      <h2 className={styles.formTitle}>Welcome back</h2>
      <p className={styles.formSubtitle}>Sign in to continue your journey</p>
      
      {error && (
        <div className={styles.errorContainer}>
          <span className={styles.errorIcon}>🌙</span>
          <p className={styles.errorMessage}>{error}</p>
        </div>
      )}
      
      <div className={styles.fields}>
        <div className={styles.field}>
          <label 
            htmlFor="username" 
            className={`${styles.label} ${focusedField === 'username' ? styles.labelFocused : ''}`}
          >
            Email
          </label>
          <div className={styles.inputWrapper}>
            <input
              type="email"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              onFocus={() => handleFocus('username')}
              onBlur={handleBlur}
              className={`${styles.input} ${error && !formData.username ? styles.inputError : ''}`}
              placeholder="your@email.com"
              disabled={isLoading}
              required
              autoComplete="email"
            />
            {focusedField === 'username' && (
              <span className={styles.inputGlow} />
            )}
          </div>
        </div>

        <div className={styles.field}>
          <label 
            htmlFor="password" 
            className={`${styles.label} ${focusedField === 'password' ? styles.labelFocused : ''}`}
          >
            Password
          </label>
          <div className={styles.inputWrapper}>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              onFocus={() => handleFocus('password')}
              onBlur={handleBlur}
              className={`${styles.input} ${error && !formData.password ? styles.inputError : ''}`}
              placeholder="••••••••"
              disabled={isLoading}
              required
              autoComplete="current-password"
            />
            {focusedField === 'password' && (
              <span className={styles.inputGlow} />
            )}
          </div>
        </div>
      </div>

      <button 
        type="submit" 
        className={styles.submitButton}
        disabled={isLoading}
      >
        {isLoading ? (
          <span className={styles.loadingContainer}>
            <span className={styles.loadingDots}>
              <span>.</span><span>.</span><span>.</span>
            </span>
            <span className={styles.loadingText}>Signing in</span>
          </span>
        ) : (
          'Sign in'
        )}
      </button>

      <div className={styles.toggle}>
        <span className={styles.toggleText}>New here?</span>
        <button 
          type="button"
          onClick={onToggleMode}
          className={styles.toggleButton}
          disabled={isLoading}
        >
          Create an account
        </button>
      </div>

      {/*  */}
      <div className={styles.demoHint}>
        <span className={styles.demoHintIcon}>✨</span>
        <span className={styles.demoHintText}>Start now</span>
      </div>
    </form>
  );
};