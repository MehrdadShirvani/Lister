import React from 'react';
import styles from './TabStyles.module.css';

export const PlansTab: React.FC = () => {
  return (
    <div className={styles.tabContainer}>
      <div className={styles.section}>
        <h2 className={styles.sectionTitle}>Upcoming</h2>
        <div className={styles.plansList}>
          <div className={styles.planCard}>
            <div className={styles.planTime}>Today, 7:30 PM</div>
            <div className={styles.planContent}>
              <h3 className={styles.planTitle}>Watch "Samsara"</h3>
              <div className={styles.planTags}>
                <span className={styles.tag}>Reflective</span>
                <span className={styles.tag}>Calm</span>
              </div>
              <div className={styles.planStatus}>
                <span className={`${styles.statusBadge} ${styles.statusUpcoming}`}>
                  Upcoming
                </span>
              </div>
            </div>
          </div>

          <div className={styles.planCard}>
            <div className={styles.planTime}>Tomorrow, 6:45 AM</div>
            <div className={styles.planContent}>
              <h3 className={styles.planTitle}>Morning pages</h3>
              <div className={styles.planTags}>
                <span className={styles.tag}>Creative</span>
                <span className={styles.tag}>Alone</span>
              </div>
              <div className={styles.planStatus}>
                <span className={`${styles.statusBadge} ${styles.statusUpcoming}`}>
                  Upcoming
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className={styles.section}>
        <h2 className={styles.sectionTitle}>Awaiting reflection</h2>
        <div className={styles.plansList}>
          <div className={`${styles.planCard} ${styles.planCardAwaiting}`}>
            <div className={styles.planTime}>Yesterday, 8:00 PM</div>
            <div className={styles.planContent}>
              <h3 className={styles.planTitle}>Listen to "Music for Airports"</h3>
              <div className={styles.planTags}>
                <span className={styles.tag}>Ambient</span>
                <span className={styles.tag}>Calm</span>
              </div>
              <div className={styles.planStatus}>
                <span className={`${styles.statusBadge} ${styles.statusAwaiting}`}>
                  Reflection needed
                </span>
              </div>
              <button className={styles.reflectionButton}>
                Add reflection
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className={styles.section}>
        <h2 className={styles.sectionTitle}>Completed</h2>
        <div className={styles.plansList}>
          <div className={`${styles.planCard} ${styles.planCardCompleted}`}>
            <div className={styles.planTime}>2 days ago</div>
            <div className={styles.planContent}>
              <h3 className={styles.planTitle}>Read "The Poetry of Rumi"</h3>
              <div className={styles.planTags}>
                <span className={styles.tag}>Poetry</span>
                <span className={styles.tag}>Reflective</span>
              </div>
              <div className={styles.planStatus}>
                <span className={`${styles.statusBadge} ${styles.statusCompleted}`}>
                  Completed
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};