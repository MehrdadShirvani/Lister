// components/dashboard/library/EditTaskModal.tsx
import React, { useState, useEffect } from 'react';
import styles from './TaskModal.module.css';
import type { TaskResponse, TaskUpdate } from '../../../../types';
import api from '../../../../services/api';
import { TagSelector } from '../../../Tags/TagSelector';

interface EditTaskModalProps {
  isOpen: boolean;
  onClose: () => void;
  task: TaskResponse;
  onTaskUpdated: () => void;
}

export const EditTaskModal: React.FC<EditTaskModalProps> = ({
  isOpen,
  onClose,
  task,
  onTaskUpdated,
}) => {
  const [formData, setFormData] = useState<TaskUpdate>({
    title: task.title,
    description: task.description,
    estimated_duration: task.estimated_duration,
    urls: task.urls.map(t => t.url),
    tag_ids: task.tags?.map(t => t.id) || [],
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setFormData({
      title: task.title,
      description: task.description,
      estimated_duration: task.estimated_duration,
      urls: task.urls.map(t => t.url),
      tag_ids: task.tags?.map(t => t.id) || [],
    });
  }, [task]);

  if (!isOpen) return null;
  const [newUrl, setNewUrl] = useState('');
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
      await api.Tasks.update(task.id, formData);
      onTaskUpdated();
      onClose();
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to update task');
    } finally {
      setIsLoading(false);
    }
  };


  
  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this task?')) {
      setIsLoading(true);
      try {
        await api.Tasks.delete(task.id);
        onTaskUpdated();
        onClose();
      } catch (err: any) {
        setError(err.response?.data?.message || 'Failed to delete task');
      } finally {
        setIsLoading(false);
      }
    }
  };

  // const commitmentLevels = [
  //   'Zero Commitment',
  //   'Low Commitment',
  //   'Medium Commitment',
  //   'High Commitment',
  //   'One-shot',
  //   'Ongoing',
  // ];

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <div className={styles.modalHeader}>
          <h2 className={styles.modalTitle}>Edit Task</h2>
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
              required
            />
          </div>

          <div className={styles.field}>
            <label htmlFor="description" className={styles.label}>
              Description
            </label>
            <textarea
              id="description"
              value={formData.description || ''}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className={styles.textarea}
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
                min="1"
              />
            </div>

            {/* <div className={styles.field}>
              <label htmlFor="commitment" className={styles.label}>
                Commitment Level
              </label>
              <select
                id="commitment"
                value={formData.commitment_level || ''}
                onChange={(e) => setFormData({ ...formData, commitment_level: e.target.value })}
                className={styles.select}
              >
                <option value="">Select level</option>
                {commitmentLevels.map(level => (
                  <option key={level} value={level}>{level}</option>
                ))}
              </select>
            </div> */}
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
              onClick={handleDelete}
              className={`${styles.button} ${styles.deleteButton}`}
              disabled={isLoading}
            >
              Delete Task
            </button>
            <div className={styles.footerActions}>
              <button
                type="button"
                onClick={onClose}
                className={`${styles.button} ${styles.cancelButton}`}
                disabled={isLoading}
              >
                Cancel
              </button>
              <button
                type="submit"
                className={`${styles.button} ${styles.submitButton}`}
                disabled={isLoading}
              >
                {isLoading ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
};