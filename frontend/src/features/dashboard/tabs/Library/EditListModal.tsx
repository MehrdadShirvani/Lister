// components/dashboard/library/EditListModal.tsx
import React, { useState, useEffect } from 'react';
import styles from './ListModal.module.css';
import type { ListResponse, ListUpdate } from '../../../../types';
import api from '../../../../services/api';
import { TagSelector } from '../../../Tags/TagSelector';

interface EditListModalProps {
  isOpen: boolean;
  onClose: () => void;
  list: ListResponse;
  onListUpdated: () => void;
}

export const EditListModal: React.FC<EditListModalProps> = ({
  isOpen,
  onClose,
  list,
  onListUpdated,
}) => {
  const [formData, setFormData] = useState<ListUpdate>({
    title: list.title,
    description: list.description,
    tag_ids: list.tags?.map(t => t.id) || [],
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setFormData({
      title: list.title,
      description: list.description,
      tag_ids: list.tags?.map(t => t.id) || [],
    });
  }, [list]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      await api.Lists.update(list.id, formData);
      onListUpdated();
      onClose();
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to update list');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this list? This action cannot be undone.')) {
      setIsLoading(true);
      try {
        await api.Lists.delete(list.id);
        onListUpdated();
        onClose();
      } catch (err: any) {
        setError(err.response?.data?.message || 'Failed to delete list');
      } finally {
        setIsLoading(false);
      }
    }
  };

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <div className={styles.modalHeader}>
          <h2 className={styles.modalTitle}>Edit List</h2>
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
            <label htmlFor="name" className={styles.label}>
              List Name
            </label>
            <input
              type="text"
              id="name"
              value={formData.title || ''}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              className={styles.input}
              placeholder="e.g., Movies to Reflect On"
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
              placeholder="What's this list about?"
              rows={3}
            />
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
              Delete List
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