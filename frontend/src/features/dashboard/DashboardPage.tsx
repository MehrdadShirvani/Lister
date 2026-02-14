// pages/DashboardPage.tsx
import React, { useState } from 'react';
import styles from './DashboardPage.module.css';
import { Header } from './Header';
import { SettingsModal } from './SettingsModal';
import { TabNavigation } from './TabNavigation';
import { ExploreTab } from './tabs/ExploreTab';
import { LibraryTab } from './tabs/Library/LibraryTab';
import { NotesTab } from './tabs/Notes/NotesTab';
import { PlansTab } from './tabs/PlansTab';
import { TodayTab } from './tabs/TodayTab';

export type TabType = 'today' | 'explore' | 'library' | 'plans' | 'notes';

export const DashboardPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>('today');
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  const renderTab = () => {
    switch (activeTab) {
      case 'today':
        return <TodayTab />;
      case 'explore':
        return <ExploreTab />;
      case 'library':
        return <LibraryTab />;
      case 'plans':
        return <PlansTab />;
      case 'notes':
        return <NotesTab />;
      default:
        return <TodayTab />;
    }
  };

  return (
    <div className={styles.container}>
      <Header onSettingsClick={() => setIsSettingsOpen(true)} />
      
      <main className={styles.main}>
        <div className={styles.tabContent}>
          {renderTab()}
        </div>
      </main>

      <TabNavigation activeTab={activeTab} onTabChange={setActiveTab} />

      <SettingsModal 
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
      />
    </div>
  );
};