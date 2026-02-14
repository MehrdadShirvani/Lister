// components/dashboard/tags/CreateTagModal.tsx
import React, { useState } from 'react';
import styles from './CreateTagModal.module.css';
import type { TagType } from '../../types';
import { TAG_TYPES } from '../../types/tag';
import api from '../../services/api';

interface CreateTagModalProps {
  isOpen: boolean;
  onClose: () => void;
  onTagCreated: (tag: any) => void;
  initialType?: TagType;
  initialName?: string;
}

export const CreateTagModal: React.FC<CreateTagModalProps> = ({
  isOpen,
  onClose,
  onTagCreated,
  initialType,
  initialName,
}) => {
  const [formData, setFormData] = useState({
    title: initialName || '',
    type: initialType || TAG_TYPES.MOOD,
    description: '',
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      const newTag = await api.Tags.createUserTag({
        title: formData.title,
        type: formData.type,
        description: formData.description || undefined,
      });
      onTagCreated(newTag);
      onClose();
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to create tag');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <div className={styles.modalHeader}>
          <h2 className={styles.modalTitle}>Create New Tag</h2>
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
              Tag Name *
            </label>
            <input
              type="text"
              id="title"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              className={styles.input}
              placeholder="e.g., Cozy, Reflective, Late Night"
              required
              autoFocus
            />
          </div>

          <div className={styles.field}>
            <label htmlFor="type" className={styles.label}>
              Tag Type
            </label>
            <select
              id="type"
              value={formData.type}
              onChange={(e) => setFormData({ ...formData, type: e.target.value as TagType })}
              className={styles.select}
            >
              {Object.values(TAG_TYPES).map(type => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>
          </div>

          <div className={styles.field}>
            <label htmlFor="description" className={styles.label}>
              Description (optional)
            </label>
            <textarea
              id="description"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className={styles.textarea}
              placeholder="What does this tag mean to you?"
              rows={3}
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
              disabled={isLoading || !formData.title.trim()}
            >
              {isLoading ? 'Creating...' : 'Create Tag'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};