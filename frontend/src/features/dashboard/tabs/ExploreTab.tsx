import React from 'react';
import styles from './TabStyles.module.css';

export const ExploreTab: React.FC = () => {
  return (
    <div className={styles.tabContainer}>
      <div className={styles.section}>
        <h2 className={styles.sectionTitle}>How are you feeling?</h2>
        
        <div className={styles.tagGroups}>
          <div className={styles.tagGroup}>
            <h3 className={styles.tagGroupTitle}>Mood</h3>
            <div className={styles.tagGroupItems}>
              <button className={`${styles.tagButton} ${styles.tagButtonActive}`}>Calm</button>
              <button className={styles.tagButton}>Cozy</button>
              <button className={styles.tagButton}>Reflective</button>
              <button className={styles.tagButton}>Playful</button>
              <button className={styles.tagButton}>Nostalgic</button>
            </div>
          </div>

          <div className={styles.tagGroup}>
            <h3 className={styles.tagGroupTitle}>Energy</h3>
            <div className={styles.tagGroupItems}>
              <button className={styles.tagButton}>Very Low</button>
              <button className={styles.tagButton}>Low</button>
              <button className={`${styles.tagButton} ${styles.tagButtonActive}`}>Medium</button>
              <button className={styles.tagButton}>High</button>
            </div>
          </div>

          <div className={styles.tagGroup}>
            <h3 className={styles.tagGroupTitle}>Social</h3>
            <div className={styles.tagGroupItems}>
              <button className={`${styles.tagButton} ${styles.tagButtonActive}`}>Alone</button>
              <button className={styles.tagButton}>With Friends</button>
              <button className={styles.tagButton}>With Partner</button>
            </div>
          </div>

          <div className={styles.tagGroup}>
            <h3 className={styles.tagGroupTitle}>Context</h3>
            <div className={styles.tagGroupItems}>
              <button className={styles.tagButton}>Late Night</button>
              <button className={styles.tagButton}>Weekend</button>
              <button className={`${styles.tagButton} ${styles.tagButtonActive}`}>Short Break</button>
              <button className={styles.tagButton}>Long Session</button>
            </div>
          </div>
        </div>
      </div>

      <div className={styles.section}>
        <h2 className={styles.sectionTitle}>Suggestions for you</h2>
        <div className={styles.exploreGrid}>
          {[1, 2, 3].map((item) => (
            <div key={item} className={styles.exploreCard}>
              <h3 className={styles.exploreCardTitle}>Watch: "Baraka" (1992)</h3>
              <p className={styles.exploreCardDescription}>A cinematic meditation on Earth</p>
              <div className={styles.exploreCardTags}>
                <span className={styles.tag}>Reflective</span>
                <span className={styles.tag}>Low energy</span>
                <span className={styles.tag}>Alone</span>
              </div>
              <span className={styles.exploreCardDuration}>97 min</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};