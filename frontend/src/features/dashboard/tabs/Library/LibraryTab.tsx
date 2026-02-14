// components/dashboard/tabs/LibraryTab.tsx
import React, { useState, useEffect } from 'react';

import styles from './LibraryTab.module.css';
import type { ListResponse, TaskResponse } from '../../../../types';
import api from '../../../../services/api';
import { ListDetailView } from './ListDetailView';
import { TaskView } from './TaskView';
import { ListView } from './ListView';
import { CreateTaskModal } from './CreateTaskModal';
import { EditTaskModal } from './EditTaskModal';
import { CreateListModal } from './CreateListModal';

type ViewMode = 'lists' | 'tasks';
type LibraryView = 'grid' | 'list-detail';

export const LibraryTab: React.FC = () => {
  const [viewMode, setViewMode] = useState<ViewMode>('lists');
  const [libraryView, setLibraryView] = useState<LibraryView>('grid');
  const [selectedList, setSelectedList] = useState<ListResponse | null>(null);
  const [isCreateListModalOpen, setIsCreateListModalOpen] = useState(false);
  const [isCreateTaskModalOpen, setIsCreateTaskModalOpen] = useState(false);
  const [isEditTaskModalOpen, setIsEditTaskModalOpen] = useState(false);
  const [selectedTask, setSelectedTask] = useState<TaskResponse | null>(null);
  const [lists, setLists] = useState<ListResponse[]>([]);
  const [tasks, setTasks] = useState<TaskResponse[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  // Fetch lists
  const fetchLists = async () => {
    setIsLoading(true);
    try {
      const data = await api.Lists.getAll();
      setLists(data);
    } catch (error) {
      console.error('Failed to fetch lists:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Fetch tasks
  const fetchTasks = async () => {
    setIsLoading(true);
    try {
      const data = await api.Tasks.getAll();
      setTasks(data);
    } catch (error) {
      console.error('Failed to fetch tasks:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (viewMode === 'lists') {
      fetchLists();
    } else {
      fetchTasks();
    }
  }, [viewMode]);

  const handleListClick = (list: ListResponse) => {
    setSelectedList(list);
    setLibraryView('list-detail');
  };

  const handleBackToLists = () => {
    setSelectedList(null);
    setLibraryView('grid');
  };

  const handleEditTask = async (taskId: number) => {
    const task = await api.Tasks.getById(taskId);
    setSelectedTask(task);
    setIsEditTaskModalOpen(true);
  };

  const handleTaskUpdated = () => {
    fetchTasks();
    if (selectedList) {
      // Refresh list detail if we're viewing a list
      handleListClick(selectedList);
    }
  };

  const renderContent = () => {
    if (viewMode === 'lists') {
      if (libraryView === 'list-detail' && selectedList) {
        return (
          <ListDetailView
            list={selectedList}
            onBack={handleBackToLists}
            onEditTask={handleEditTask}
            onTaskUpdated={handleTaskUpdated}
          />
        );
      }
      return (
        <ListView
          lists={lists}
          isLoading={isLoading}
          onListClick={handleListClick}
          onCreateList={() => setIsCreateListModalOpen(true)}
          onListsUpdated={fetchLists}
        />
      );
    } else {
      return (
        <TaskView
          tasks={tasks}
          isLoading={isLoading}
          onEditTask={handleEditTask}
          onCreateTask={() => setIsCreateTaskModalOpen(true)}
          onTasksUpdated={fetchTasks}
        />
      );
    }
  };

  return (
    <div className={styles.tabContainer}>
      <div className={styles.libraryHeader}>
        <div className={styles.headerLeft}>
          {viewMode === 'lists' && libraryView === 'list-detail' ? (
            <button className={styles.backButton} onClick={handleBackToLists}>
              ← Back to lists
            </button>
          ) : (
            <h2 className={styles.sectionTitle}>Library</h2>
          )}
        </div>

        <div className={styles.headerControls}>
          <div className={styles.viewModeToggle}>
            <button
              className={`${styles.viewModeButton} ${viewMode === 'lists' ? styles.viewModeActive : ''}`}
              onClick={() => setViewMode('lists')}
            >
              📋 Lists
            </button>
            <button
              className={`${styles.viewModeButton} ${viewMode === 'tasks' ? styles.viewModeActive : ''}`}
              onClick={() => setViewMode('tasks')}
            >
              ✓ Tasks
            </button>
          </div>
        </div>
      </div>

      {renderContent()}

      <CreateListModal
        isOpen={isCreateListModalOpen}
        onClose={() => setIsCreateListModalOpen(false)}
        onListCreated={() => {
          fetchLists();
          setIsCreateListModalOpen(false);
        }}
      />

      <CreateTaskModal
        isOpen={isCreateTaskModalOpen}
        onClose={() => setIsCreateTaskModalOpen(false)}
        onTaskCreated={() => {
          fetchTasks();
          setIsCreateTaskModalOpen(false);
        }}
        selectedListId={selectedList?.id}
      />

      {selectedTask && (
        <EditTaskModal
          isOpen={isEditTaskModalOpen}
          onClose={() => {
            setIsEditTaskModalOpen(false);
            setSelectedTask(null);
          }}
          task={selectedTask}
          onTaskUpdated={handleTaskUpdated}
        />
      )}
    </div>
  );
};