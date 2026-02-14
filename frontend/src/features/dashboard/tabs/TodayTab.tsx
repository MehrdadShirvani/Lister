import React from 'react';
import styles from './TabStyles.module.css';

export const TodayTab: React.FC = () => {
  return (
    <div className={styles.tabContainer}>
      <div className={styles.section}>
        <h2 className={styles.sectionTitle}>Right now</h2>
        <div className={styles.suggestionCard}>
          <p className={styles.suggestionTime}>You have 25 minutes • Low energy</p>
          <h3 className={styles.suggestionTitle}>Watch that short documentary</h3>
          <div className={styles.suggestionTags}>
            <span className={styles.tag}>Calm</span>
            <span className={styles.tag}>Meaningful</span>
            <span className={styles.tag}>Alone</span>
          </div>
          <div className={styles.suggestionActions}>
            <button className={styles.primaryButton}>Accept</button>
            <button className={styles.secondaryButton}>Show another</button>
          </div>
        </div>
      </div>

      <div className={styles.section}>
        <h2 className={styles.sectionTitle}>Upcoming free time</h2>
        <div className={styles.timeBlocks}>
          <div className={styles.timeBlock}>
            <span className={styles.timeBlockDay}>Today</span>
            <span className={styles.timeBlockHours}>7:00 PM - 9:00 PM</span>
            <span className={styles.timeBlockEnergy}>Medium energy</span>
          </div>
          <div className={styles.timeBlock}>
            <span className={styles.timeBlockDay}>Tomorrow</span>
            <span className={styles.timeBlockHours}>6:30 AM - 7:30 AM</span>
            <span className={styles.timeBlockEnergy}>Low energy</span>
          </div>
        </div>
      </div>

      <div className={styles.section}>
        <button className={styles.randomMomentButton}>
          <span className={styles.randomMomentIcon}>✨</span>
          <span>Random meaningful moment</span>
        </button>
      </div>
    </div>
  );
};