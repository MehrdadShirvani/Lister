// components/dashboard/library/TaskItem.tsx
import React, { useState } from 'react';
import styles from './TaskItem.module.css';
import api from '../../../../services/api';
import type { TaskResponse } from '../../../../types';

interface TaskItemProps {
  task: TaskResponse;
  onEdit: () => void;
  onTaskUpdated: () => void;
}

export const TaskItem: React.FC<TaskItemProps> = ({ task, onEdit, onTaskUpdated }) => {
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this task?')) {
      setIsDeleting(true);
      try {
        await api.Tasks.delete(task.id);
        onTaskUpdated();
      } catch (error) {
        console.error('Failed to delete task:', error);
      } finally {
        setIsDeleting(false);
      }
    }
  };

  const handleComplete = async () => {
    try {
      await api.Tasks.complete(task.id);
      onTaskUpdated();
    } catch (error) {
      console.error('Failed to complete task:', error);
    }
  };

  return (
    <div className={`${styles.taskItem} ${task.completed_at ? styles.completed : ''}`}>
      <div className={styles.taskContent}>
        <div className={styles.taskHeader}>
          <h3 className={styles.taskTitle}>{task.title}</h3>
          <div className={styles.taskActions}>
            <button 
              className={styles.actionButton} 
              onClick={onEdit}
              aria-label="Edit task"
            >
              ✎
            </button>
            <button 
              className={styles.actionButton} 
              onClick={handleDelete}
              disabled={isDeleting}
              aria-label="Delete task"
            >
              {isDeleting ? '...' : '🗑'}
            </button>
          </div>
        </div>

        {task.description && (
          <p className={styles.taskDescription}>{task.description}</p>
        )}

        {task.tags && task.tags.length > 0 && (
          <div className={styles.taskTags}>
            {task.tags.map((tag) => (
              <span key={tag.id} className={styles.taskTag}>
                {tag.title}
              </span>
            ))}
          </div>
        )}

        <div className={styles.taskMeta}>
          {task.estimated_duration && (
            <span className={styles.taskDuration}>
              ⏱ {task.estimated_duration} min
            </span>
          )}
         
          <span className={styles.taskUpdated}>
            Updated {new Date(task.updated_at??task.created_at).toLocaleDateString()}
          </span>
        </div>

        {!task.completed_at && (
          <button 
            className={styles.completeButton}
            onClick={handleComplete}
          >
            ✓ Mark complete
          </button>
        )}
      </div>
    </div>
  );
};