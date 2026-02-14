import React from 'react';
import styles from './ListCard.module.css';
import type { ListResponse } from '../../../../types';

interface ListCardProps {
  list: ListResponse;
  onClick: () => void;
  onEdit: (e: React.MouseEvent) => void;
}

export const ListCard: React.FC<ListCardProps> = ({ list, onClick, onEdit }) => {
  const completionPercentage = list.task_count > 0 
    ? Math.round((list.completed_task_count / list.task_count) * 100)
    : 0;

  return (
    <div className={styles.card} onClick={onClick}>
      <div className={styles.cardHeader}>
        <h3 className={styles.title}>{list.title}</h3>
        <button className={styles.editButton} onClick={onEdit} aria-label="Edit list">
          ⋮
        </button>
      </div>
      
      {list.description && (
        <p className={styles.description}>{list.description}</p>
      )}

      <div className={styles.stats}>
        <div className={styles.stat}>
          <span className={styles.statValue}>{list.task_count}</span>
          <span className={styles.statLabel}>tasks</span>
        </div>
        <div className={styles.stat}>
          <span className={styles.statValue}>{list.active_task_count}</span>
          <span className={styles.statLabel}>active</span>
        </div>
        <div className={styles.stat}>
          <span className={styles.statValue}>{list.completed_task_count}</span>
          <span className={styles.statLabel}>done</span>
        </div>
      </div>

      {list.task_count > 0 && (
        <div className={styles.progressContainer}>
          <div 
            className={styles.progressBar} 
            style={{ width: `${completionPercentage}%` }}
          />
          <span className={styles.progressText}>{completionPercentage}% complete</span>
        </div>
      )}

      {list.tags && list.tags.length > 0 && (
        <div className={styles.tags}>
          {list.tags.slice(0, 3).map((tag) => (
            <span key={tag.id} className={styles.tag}>
              {tag.title}
            </span>
          ))}
          {list.tags.length > 3 && (
            <span className={styles.tagMore}>+{list.tags.length - 3}</span>
          )}
        </div>
      )}

      <div className={styles.footer}>
        <span className={styles.updated}>
          Updated {new Date(list.updated_at??list.created_at).toLocaleDateString()}
        </span>
      </div>
    </div>
  );
};