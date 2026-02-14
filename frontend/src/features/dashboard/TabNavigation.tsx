import React from 'react';
import styles from './TabNavigation.module.css';
import type { TabType } from './DashboardPage';

interface TabNavigationProps {
  activeTab: TabType;
  onTabChange: (tab: TabType) => void;
}

interface TabItem {
  id: TabType;
  label: string;
  icon: string;
}

const tabs: TabItem[] = [
  { id: 'today', label: 'Today', icon: '🌅' },
  { id: 'explore', label: 'Explore', icon: '🔍' },
  { id: 'library', label: 'Library', icon: '📚' },
  { id: 'plans', label: 'Plans', icon: '✨' },
  { id: 'notes', label: 'Notes', icon: '📝' },
];

export const TabNavigation: React.FC<TabNavigationProps> = ({ activeTab, onTabChange }) => {
  return (
    <nav className={styles.navigation}>
      <div className={styles.tabBar}>
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={`${styles.tab} ${activeTab === tab.id ? styles.tabActive : ''}`}
            aria-label={tab.label}
          >
            <span className={styles.tabIcon}>{tab.icon}</span>
            <span className={styles.tabLabel}>{tab.label}</span>
            {activeTab === tab.id && <span className={styles.tabIndicator} />}
          </button>
        ))}
      </div>
    </nav>
  );
};