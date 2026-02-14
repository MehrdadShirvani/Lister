import React from 'react';
import styles from './WelcomeMessage.module.css';

export const WelcomeMessage: React.FC = () => {
  return (
    <div className={styles.container}>
      <h1 className={styles.title}>
        Life
        <span className={styles.titleAccent}>Curator</span>
      </h1>
      <p className={styles.subtitle}>
        A gentle companion for the moments that matter
      </p>
      <div className={styles.messageContainer}>
        <p className={styles.message}>
          "A place for the small, meaningful things you want to experience."
        </p>
        <p className={styles.message}>
          No pressure. No streaks. Just moments, thoughtfully suggested.
        </p>
      </div>
      <div className={styles.features}>
        <div className={styles.feature}>
          <span className={styles.featureDot} />
          <span>Reflective by design</span>
        </div>
        <div className={styles.feature}>
          <span className={styles.featureDot} />
          <span>Intelligent suggestions</span>
        </div>
        <div className={styles.feature}>
          <span className={styles.featureDot} />
          <span>Calm, always</span>
        </div>
      </div>
    </div>
  );
};