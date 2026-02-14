// components/dashboard/library/ListDetailView.tsx
import React, { useState, useEffect } from 'react';
import { TaskItem } from './TaskItem';
import { EditListModal } from './EditListModal';
import styles from './ListDetailView.module.css';
import api from '../../../../services/api';
import type { ListResponse, TaskResponse } from '../../../../types';
import { CreateTaskModal } from './CreateTaskModal';

interface ListDetailViewProps {
  list: ListResponse;
  onBack: () => void;
  onEditTask: (task: number) => void;
  onTaskUpdated: () => void;
}

export const ListDetailView: React.FC<ListDetailViewProps> = ({
  list,
  onBack,
  onEditTask,
  onTaskUpdated,
}) => {
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [tasks, setTasks] = useState<TaskResponse[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isCreateTaskOpen, setIsCreateTaskOpen] = useState(false);

  const fetchListTasks = async () => {
    setIsLoading(true);
    try {
      // const detail = await api.Lists.getDetail(list.id);
      const tasks = await api.Tasks.getAll({list_id : list.id});
      setTasks(tasks || []);
    } catch (error) {
      console.error('Failed to fetch list tasks:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchListTasks();
  }, [list.id]);

  const sortedTasks = [...tasks].sort((a, b) => 
    new Date(b.updated_at ?? b.created_at).getTime() - new Date(a.updated_at ?? a.created_at).getTime()
  );

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <button className={styles.backButton} onClick={onBack}>
          ←
        </button>
        <div className={styles.headerContent}>
          <h1 className={styles.title}>{list.title}</h1>
          {list.description && (
            <p className={styles.description}>{list.description}</p>
          )}
          {list.tags && list.tags.length > 0 && (
            <div className={styles.tags}>
              {list.tags.map((tag) => (
                <span key={tag.id} className={styles.tag}>
                  {tag.title}
                </span>
              ))}
            </div>
          )}
        </div>
        <button 
          className={styles.editButton}
          onClick={() => setIsEditModalOpen(true)}
        >
          Edit list
        </button>
      </div>

      <div className={styles.content}>
        <div className={styles.tasksHeader}>
          <h2 className={styles.tasksTitle}>Tasks in this list</h2>
          <button 
            className={styles.addTaskButton}
            onClick={() => setIsCreateTaskOpen(true)}
          >
            + Add task
          </button>
        </div>

        {isLoading ? (
          <div className={styles.loadingContainer}>
            <div className={styles.loadingSpinner} />
            <p>Loading tasks...</p>
          </div>
        ) : sortedTasks.length === 0 ? (
          <div className={styles.emptyTasks}>
            <p>No tasks in this list yet</p>
            <button 
              className={styles.createFirstTaskButton}
              onClick={() => setIsCreateTaskOpen(true)}
            >
              Create your first task
            </button>
          </div>
        ) : (
          <div className={styles.tasksList}>
            {sortedTasks.map((task) => (
              <TaskItem
                key={task.id}
                task={task}
                onEdit={() => onEditTask(task.id)}
                onTaskUpdated={onTaskUpdated}
              />
            ))}
          </div>
        )}
      </div>

      <EditListModal
        isOpen={isEditModalOpen}
        onClose={() => setIsEditModalOpen(false)}
        list={list}
        onListUpdated={() => {
          onTaskUpdated(); // Refresh parent
          setIsEditModalOpen(false);
        }}
      />

      {isCreateTaskOpen && (
        <CreateTaskModal
          isOpen={isCreateTaskOpen}
          onClose={() => setIsCreateTaskOpen(false)}
          onTaskCreated={() => {
            fetchListTasks();
            setIsCreateTaskOpen(false);
          }}
          selectedListId={list.id}
        />
      )}
    </div>
  );
};