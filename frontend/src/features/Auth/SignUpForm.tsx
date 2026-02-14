// components/auth/SignUpForm.tsx
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import type { UserSignup } from '../../types/auth';
import styles from './AuthForm.module.css';
import api from '../../services/api';
import { useAuthStore } from '../../stores/useAuthStore';

interface SignUpFormProps {
  onToggleMode: () => void;
}

export const SignUpForm: React.FC<SignUpFormProps> = ({ onToggleMode }) => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState<UserSignup>({
    first_name: '',
    last_name: '',
    email: '',
    password: '',
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
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

  const validateForm = (): boolean => {
    if (formData.password.length < 8) {
      setError('Password should be at least 8 characters for your security.');
      return false;
    }
    
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      setError('Please enter a valid email address.');
      return false;
    }
    
    return true;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setIsLoading(true);
    setError(null);
    setSuccess(null);

    try {
      await api.Auth.signup(formData);
      
      // Show success message
      setSuccess('Account created successfully!');
      
      // Optional: Auto-login after signup
      try {
        const loginResponse = await api.Auth.login({
          username: formData.email,
          password: formData.password,
        });
        useAuthStore.getState().login(loginResponse);
        
        // Short delay to show success message before redirect
        setTimeout(() => {
          navigate('/dashboard');
        }, 1500);
      } catch (loginErr) {
        // If auto-login fails, just show success and let user sign in manually
        setTimeout(() => {
          onToggleMode(); // Switch to sign in
        }, 2000);
      }
      
    } catch (err: any) {
      // Handle different types of errors gracefully
      let errorMessage = 'Unable to create account. Please try again.';
      
      if (err.response) {
        if (err.response.status === 409) {
          errorMessage = 'An account with this email already exists. Would you like to sign in instead?';
        } else if (err.response.status === 400) {
          // Handle validation errors from server
          if (err.response.data?.errors) {
            const validationErrors = Object.values(err.response.data.errors).join(' ');
            errorMessage = validationErrors;
          } else if (err.response.data?.message) {
            errorMessage = err.response.data.message;
          }
        } else if (err.response.data?.message) {
          errorMessage = err.response.data.message;
        }
      } else if (err.request) {
        errorMessage = 'Unable to connect. Please check your connection and try again.';
      }
      
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className={styles.form}>
      <h2 className={styles.formTitle}>Begin your journey</h2>
      <p className={styles.formSubtitle}>Create an account to start curating</p>
      
      {error && (
        <div className={styles.errorContainer}>
          <span className={styles.errorIcon}>🌙</span>
          <p className={styles.errorMessage}>{error}</p>
        </div>
      )}
      
      {success && (
        <div className={styles.successContainer}>
          <span className={styles.successIcon}>✨</span>
          <p className={styles.successMessage}>{success}</p>
        </div>
      )}
      
      <div className={styles.fields}>
        <div className={styles.fieldRow}>
          <div className={styles.field}>
            <label 
              htmlFor="first_name" 
              className={`${styles.label} ${focusedField === 'first_name' ? styles.labelFocused : ''}`}
            >
              First name
            </label>
            <div className={styles.inputWrapper}>
              <input
                type="text"
                id="first_name"
                name="first_name"
                value={formData.first_name}
                onChange={handleChange}
                onFocus={() => handleFocus('first_name')}
                onBlur={handleBlur}
                className={styles.input}
                placeholder="Alex"
                disabled={isLoading}
                required
                autoComplete="given-name"
              />
              {focusedField === 'first_name' && (
                <span className={styles.inputGlow} />
              )}
            </div>
          </div>

          <div className={styles.field}>
            <label 
              htmlFor="last_name" 
              className={`${styles.label} ${focusedField === 'last_name' ? styles.labelFocused : ''}`}
            >
              Last name
            </label>
            <div className={styles.inputWrapper}>
              <input
                type="text"
                id="last_name"
                name="last_name"
                value={formData.last_name}
                onChange={handleChange}
                onFocus={() => handleFocus('last_name')}
                onBlur={handleBlur}
                className={styles.input}
                placeholder="Chen"
                disabled={isLoading}
                required
                autoComplete="family-name"
              />
              {focusedField === 'last_name' && (
                <span className={styles.inputGlow} />
              )}
            </div>
          </div>
        </div>

        <div className={styles.field}>
          <label 
            htmlFor="email" 
            className={`${styles.label} ${focusedField === 'email' ? styles.labelFocused : ''}`}
          >
            Email
          </label>
          <div className={styles.inputWrapper}>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              onFocus={() => handleFocus('email')}
              onBlur={handleBlur}
              className={`${styles.input} ${error && !formData.email ? styles.inputError : ''}`}
              placeholder="your@email.com"
              disabled={isLoading}
              required
              autoComplete="email"
            />
            {focusedField === 'email' && (
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
              placeholder="Choose a secure password"
              disabled={isLoading}
              required
              autoComplete="new-password"
              minLength={8}
            />
            {focusedField === 'password' && (
              <span className={styles.inputGlow} />
            )}
          </div>
          <div className={styles.passwordRequirements}>
            <span className={`${styles.requirement} ${formData.password.length >= 8 ? styles.requirementMet : ''}`}>
              {formData.password.length >= 8 ? '✓' : '○'} At least 8 characters
            </span>
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
            <span className={styles.loadingText}>Creating account</span>
          </span>
        ) : (
          'Create account'
        )}
      </button>

      <div className={styles.toggle}>
        <span className={styles.toggleText}>Already have an account?</span>
        <button 
          type="button"
          onClick={onToggleMode}
          className={styles.toggleButton}
          disabled={isLoading}
        >
          Sign in
        </button>
      </div>
    </form>
  );
};