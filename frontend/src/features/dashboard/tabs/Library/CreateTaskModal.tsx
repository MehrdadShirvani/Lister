// components/dashboard/library/CreateTaskModal.tsx
import React, { useState, useEffect } from 'react';
import styles from './TaskModal.module.css';
import { Task_Status, Task_Type, type TaskCreate } from '../../../../types';
import api from '../../../../services/api';
import { TagSelector } from '../../../Tags/TagSelector';

interface CreateTaskModalProps {
  isOpen: boolean;
  onClose: () => void;
  onTaskCreated: () => void;
  selectedListId?: number;
}

export const CreateTaskModal: React.FC<CreateTaskModalProps> = ({
  isOpen,
  onClose,
  onTaskCreated,
  selectedListId,
}) => {
  const [formData, setFormData] = useState<TaskCreate>({
    title: '',
    type: Task_Type.TASK,
    status: Task_Status.IN_PROGRESS,
    description: '',
    estimated_duration: undefined,
    urls: [],
    tag_ids: [],
    list_id: selectedListId,
  });
  const [newUrl, setNewUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (selectedListId) {
      setFormData(prev => ({ ...prev, list_id: selectedListId }));
    }
  }, [selectedListId]);

  if (!isOpen) return null;

  const handleAddUrl = () => {
    if (newUrl && newUrl.trim()) {
      setFormData({
        ...formData,
        urls: [...(formData.urls || []), newUrl.trim()]
      });
      setNewUrl('');
    }
  };

  const handleRemoveUrl = (urlToRemove: string) => {
    setFormData({
      ...formData,
      urls: formData.urls?.filter(url => url !== urlToRemove) || []
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      await api.Tasks.create(formData);
      onTaskCreated();
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to create task');
    } finally {
      setIsLoading(false);
    }
  };


  useEffect(() => {
    if (selectedListId) {
      setFormData(prev => ({ ...prev, list_ids: [selectedListId] }));
    }
  }, [selectedListId]);

  if (!isOpen) return null;

    return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <div className={styles.modalHeader}>
          <h2 className={styles.modalTitle}>Create New Task</h2>
          <button className={styles.closeButton} onClick={onClose}>×</button>
        </div>

        <form onSubmit={handleSubmit} className={styles.form}>
          {error && (
            <div className={styles.errorContainer}>
              <span className={styles.errorIcon}>🌙</span>
              <p className={styles.errorMessage}>{error}</p>
            </div>
          )}

          <div className={styles.field}>
            <label htmlFor="title" className={styles.label}>
              Task Title *
            </label>
            <input
              type="text"
              id="title"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              className={styles.input}
              placeholder="e.g., Watch that short documentary"
              required
            />
          </div>

          <div className={styles.field}>
            <label htmlFor="description" className={styles.label}>
              Description
            </label>
            <textarea
              id="description"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className={styles.textarea}
              placeholder="What makes this meaningful?"
              rows={3}
            />
          </div>

          <div className={styles.fieldRow}>
            <div className={styles.field}>
              <label htmlFor="duration" className={styles.label}>
                Duration (minutes)
              </label>
              <input
                type="number"
                id="duration"
                value={formData.estimated_duration || ''}
                onChange={(e) => setFormData({ 
                  ...formData, 
                  estimated_duration: e.target.value ? parseInt(e.target.value) : undefined 
                })}
                className={styles.input}
                placeholder="e.g., 25"
                min="1"
              />
            </div>
      
          </div>

       <div className={styles.field}>
            <label className={styles.label}>
              Links / URLs
            </label>
            <div className={styles.urlInputGroup}>
              <input
                type="url"
                value={newUrl}
                onChange={(e) => setNewUrl(e.target.value)}
                className={styles.urlInput}
                placeholder="https://..."
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddUrl())}
              />
              <button
                type="button"
                onClick={handleAddUrl}
                className={styles.addUrlButton}
                disabled={!newUrl.trim()}
              >
                Add
              </button>
            </div>
            
            {formData.urls && formData.urls.length > 0 && (
              <div className={styles.urlList}>
                {formData.urls.map((url, index) => (
                  <div key={index} className={styles.urlItem}>
                    <a href={url} target="_blank" rel="noopener noreferrer" className={styles.urlLink}>
                      {url}
                    </a>
                    <button
                      type="button"
                      onClick={() => handleRemoveUrl(url)}
                      className={styles.removeUrlButton}
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>


          <div className={styles.field}>
            <label className={styles.label}>
              Tags
            </label>
            <TagSelector
              selectedTagIds={formData.tag_ids || []}
              onChange={(tagIds) => setFormData({ ...formData, tag_ids: tagIds })}
            />
          </div>

          <div className={styles.modalFooter}>
            <button
              type="button"
              onClick={onClose}
              className={`${styles.button} ${styles.cancelButton}`}
            >
              Cancel
            </button>
            <button
              type="submit"
              className={`${styles.button} ${styles.submitButton}`}
              disabled={isLoading}
            >
              {isLoading ? 'Creating...' : 'Create Task'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};