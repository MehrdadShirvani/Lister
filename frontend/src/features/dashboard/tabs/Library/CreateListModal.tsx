import React, { useState } from 'react';
import styles from './ListModal.module.css';
import type { ListCreate } from '../../../../types';
import api from '../../../../services/api';
import { TagSelector } from '../../../Tags/TagSelector';

interface CreateListModalProps {
  isOpen: boolean;
  onClose: () => void;
  onListCreated: () => void;
}

export const CreateListModal: React.FC<CreateListModalProps> = ({
  isOpen,
  onClose,
  onListCreated,
}) => {
  const [formData, setFormData] = useState<ListCreate>({
    title: '',
    status: "active",
    description: '',
    tag_ids: [],
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      await api.Lists.create(formData);
      onListCreated();
      setFormData({ title: '', description: '', tag_ids: [], status:"active" });
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to create list');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <div className={styles.modalHeader}>
          <h2 className={styles.modalTitle}>Create New List</h2>
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
              List Name
            </label>
            <input
              type="text"
              id="title"
              value={formData.title}
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
              value={formData.description}
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
              {isLoading ? 'Creating...' : 'Create List'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};