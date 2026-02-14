// components/dashboard/SettingsModal.tsx
import React from 'react';
import styles from './SettingsModal.module.css';
import { useAuthStore } from '../../stores/useAuthStore';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({ isOpen, onClose }) => {
  const { logout } = useAuthStore();

  if (!isOpen) return null;

  const handleLogout = () => {
    logout();
    onClose();
    window.location.href = '/auth';
  };

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <div className={styles.modalHeader}>
          <h2 className={styles.modalTitle}>Settings</h2>
          <button className={styles.closeButton} onClick={onClose}>×</button>
        </div>

        <div className={styles.modalContent}>
          <div className={styles.profileSection}>
            <div className={styles.profileAvatar}>
              {/* {user?.first_name?.[0]}{user?.last_name?.[0]} */}
            </div>
            <div className={styles.profileInfo}>
              {/* <h3>{user?.first_name} {user?.last_name}</h3>
              <p>{user?.email}</p> */}
            </div>
          </div>

          <div className={styles.settingsSection}>
            <h3 className={styles.settingsSectionTitle}>Preferences</h3>
            
            <div className={styles.settingItem}>
              <div>
                <div className={styles.settingLabel}>Quiet Mode</div>
                <div className={styles.settingDescription}>Pause suggestions, hide overdue</div>
              </div>
              <label className={styles.switch}>
                <input type="checkbox" />
                <span className={styles.slider}></span>
              </label>
            </div>

            <div className={styles.settingItem}>
              <div>
                <div className={styles.settingLabel}>Reflection Required</div>
                <div className={styles.settingDescription}>Always reflect after completing plans</div>
              </div>
              <label className={styles.switch}>
                <input type="checkbox" defaultChecked />
                <span className={styles.slider}></span>
              </label>
            </div>

            <div className={styles.settingItem}>
              <div>
                <div className={styles.settingLabel}>Daily Suggestions</div>
                <div className={styles.settingDescription}>Maximum per day</div>
              </div>
              <select className={styles.select}>
                <option>1</option>
                <option selected>2</option>
                <option>3</option>
                <option>4</option>
                <option>5</option>
              </select>
            </div>
          </div>

          <div className={styles.settingsSection}>
            <h3 className={styles.settingsSectionTitle}>Account</h3>
            
            <button className={styles.menuButton}>
              Edit Profile
            </button>
            
            <button className={styles.menuButton}>
              Notification Settings
            </button>
            
            <button className={styles.menuButton}>
              Data & Privacy
            </button>
            
            <button className={`${styles.menuButton} ${styles.dangerButton}`} onClick={handleLogout}>
              Sign Out
            </button>
          </div>

          <div className={styles.modalFooter}>
            <p className={styles.version}>Life Curator v0.1.0</p>
          </div>
        </div>
      </div>
    </div>
  );
};