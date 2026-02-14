import React from 'react';
import styles from './Header.module.css';
import { useAuthStore } from '../../stores/useAuthStore';

interface HeaderProps {
  onSettingsClick: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onSettingsClick }) => {
  const { accountId } = useAuthStore();
  
  // Get initials for avatar
  const getInitials = () => {
    if (!accountId) return '?';
    return "M"
  };

  // Get current greeting based on time
//   const getGreeting = () => {
//     const hour = new Date().getHours();
//     if (hour < 12) return 'Good morning';
//     if (hour < 17) return 'Good afternoon';
//     return 'Good evening';
//   };

  return (
    <header className={styles.header}>
      <div className={styles.headerContent}>
        <div className={styles.greeting}>
          <h1 className={styles.greetingText}>
            {/* {getGreeting()}, {user?.first_name || 'friend'} */}
          </h1>
          <p className={styles.date}>
            {new Date().toLocaleDateString('en-US', { 
              weekday: 'long', 
              month: 'long', 
              day: 'numeric' 
            })}
          </p>
        </div>

        <button 
          onClick={onSettingsClick}
          className={styles.avatarButton}
          aria-label="Settings"
        >
          <div className={styles.avatar}>
            <span className={styles.avatarInitials}>{getInitials()}</span>
          </div>
          <div className={styles.avatarGlow} />
        </button>
      </div>
    </header>
  );
};