// components/dashboard/library/TaskView.tsx
import React, { useState } from 'react';
import { TaskItem } from './TaskItem';
import styles from './TaskView.module.css';
import type { TaskResponse } from '../../../../types';

interface TaskViewProps {
  tasks: TaskResponse[];
  isLoading: boolean;
  onEditTask: (task: number) => void;
  onCreateTask: () => void;
  onTasksUpdated: () => void;
}

export const TaskView: React.FC<TaskViewProps> = ({
  tasks,
  isLoading,
  onEditTask,
  onCreateTask,
  onTasksUpdated,
}) => {
  const [filter, setFilter] = useState<'all' | 'active' | 'completed'>('all');
  const [search, setSearch] = useState('');

  const filteredTasks = tasks
    .filter(task => {
      if (filter === 'active') return !task.completed_at;
      if (filter === 'completed') return task.completed_at;
      return true;
    })
    .filter(task => 
      search === '' || 
      task.title.toLowerCase().includes(search.toLowerCase()) ||
      task.description?.toLowerCase().includes(search.toLowerCase())
    )
    .sort((a, b) => new Date(b.updated_at ?? b.created_at).getTime() - new Date(a.updated_at ?? a.created_at).getTime());

  if (isLoading) {
    return (
      <div className={styles.loadingContainer}>
        <div className={styles.loadingSpinner} />
        <p>Loading tasks...</p>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div className={styles.searchBar}>
          <span className={styles.searchIcon}>🔍</span>
          <input
            type="text"
            placeholder="Search tasks..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className={styles.searchInput}
          />
        </div>
        
        <button className={styles.createButton} onClick={onCreateTask}>
          <span className={styles.createIcon}>+</span>
          New Task
        </button>
      </div>

      <div className={styles.filters}>
        <button
          className={`${styles.filterButton} ${filter === 'all' ? styles.filterActive : ''}`}
          onClick={() => setFilter('all')}
        >
          All ({tasks.length})
        </button>
        <button
          className={`${styles.filterButton} ${filter === 'active' ? styles.filterActive : ''}`}
          onClick={() => setFilter('active')}
        >
          Active ({tasks.filter(t => !t.completed_at).length})
        </button>
        <button
          className={`${styles.filterButton} ${filter === 'completed' ? styles.filterActive : ''}`}
          onClick={() => setFilter('completed')}
        >
          Completed ({tasks.filter(t => t.completed_at).length})
        </button>
      </div>

      {filteredTasks.length === 0 ? (
        <div className={styles.emptyState}>
          <div className={styles.emptyStateIcon}>✓</div>
          <h3 className={styles.emptyStateTitle}>No tasks found</h3>
          <p className={styles.emptyStateDescription}>
            {search ? 'Try a different search' : 'Create your first task to get started'}
          </p>
          {!search && (
            <button className={styles.emptyStateButton} onClick={onCreateTask}>
              Create a task
            </button>
          )}
        </div>
      ) : (
        <div className={styles.tasksList}>
          {filteredTasks.map((task) => (
            <TaskItem
              key={task.id}
              task={task}
              onEdit={() => onEditTask(task.id)}
              onTaskUpdated={onTasksUpdated}
            />
          ))}
        </div>
      )}
    </div>
  );
};