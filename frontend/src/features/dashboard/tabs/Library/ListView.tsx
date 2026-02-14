// components/dashboard/library/ListView.tsx
import React, { useState } from 'react';
import styles from './ListView.module.css';
import type { ListResponse } from '../../../../types';
import { EditListModal } from './EditListModal';
import { ListCard } from './ListCard';

interface ListViewProps {
  lists: ListResponse[];
  isLoading: boolean;
  onListClick: (list: ListResponse) => void;
  onCreateList: () => void;
  onListsUpdated: () => void;
}

export const ListView: React.FC<ListViewProps> = ({
  lists,
  isLoading,
  onListClick,
  onCreateList,
  onListsUpdated,
}) => {
  const [editingList, setEditingList] = useState<ListResponse | null>(null);

  const handleEdit = (list: ListResponse, e: React.MouseEvent) => {
    e.stopPropagation();
    setEditingList(list);
  };

  if (isLoading) {
    return (
      <div className={styles.loadingContainer}>
        <div className={styles.loadingSpinner} />
        <p>Loading your lists...</p>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <button className={styles.createButton} onClick={onCreateList}>
          <span className={styles.createIcon}>+</span>
          New List
        </button>
      </div>

      {lists.length === 0 ? (
        <div className={styles.emptyState}>
          <div className={styles.emptyStateIcon}>📋</div>
          <h3 className={styles.emptyStateTitle}>No lists yet</h3>
          <p className={styles.emptyStateDescription}>
            Create your first list to start organizing meaningful moments
          </p>
          <button className={styles.emptyStateButton} onClick={onCreateList}>
            Create a list
          </button>
        </div>
      ) : (
        <div className={styles.grid}>
          {lists.map((list) => (
            <ListCard
              key={list.id}
              list={list}
              onClick={() => onListClick(list)}
              onEdit={(e) => handleEdit(list, e)}
            />
          ))}
        </div>
      )}

      {editingList && (
        <EditListModal
          isOpen={!!editingList}
          onClose={() => setEditingList(null)}
          list={editingList}
          onListUpdated={onListsUpdated}
        />
      )}
    </div>
  );
};