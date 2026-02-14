import React from 'react';
import styles from './AuthCard.module.css';

interface AuthCardProps {
  children: React.ReactNode;
}

export const AuthCard: React.FC<AuthCardProps> = ({ children }) => {
  return (
    <div className={styles.card}>
      <div className={styles.cardInner}>{children}</div>
    </div>
  );
};