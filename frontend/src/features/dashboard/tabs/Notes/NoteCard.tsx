// components/dashboard/notes/NoteCard.tsx
import React, { useState } from 'react';
import styles from './NoteCard.module.css';
import type { NotePreview } from '../../../../types';
import { formatDistanceToNow } from 'date-fns';

interface NoteCardProps {
  note: NotePreview;
  onEdit: () => void;
  onTogglePin: () => void;
  onToggleFavorite: () => void;
  onDelete: () => void;
}

export const NoteCard: React.FC<NoteCardProps> = ({
  note,
  onEdit,
  onTogglePin,
  onToggleFavorite,
  onDelete,
}) => {
  const [showActions, setShowActions] = useState(false);

  const formattedDate = note.updated_at 
    ? formatDistanceToNow(new Date(note.updated_at), { addSuffix: true })
    : formatDistanceToNow(new Date(note.created_at), { addSuffix: true });

  const readingTime = note.reading_time_minutes === 1 
    ? '1 min read' 
    : `${note.reading_time_minutes} min read`;

  return (
    <div 
      className={styles.card}
      onMouseEnter={() => setShowActions(true)}
      onMouseLeave={() => setShowActions(false)}
    >
      <div className={styles.cardHeader}>
        <div className={styles.titleSection}>
          <h3 className={styles.title}>{note.title}</h3>
          <div className={styles.badges}>
            {note.is_pinned && <span className={styles.pinBadge}>📌</span>}
            {note.is_favorite && <span className={styles.favoriteBadge}>⭐</span>}
          </div>
        </div>
        
        {showActions && (
          <div className={styles.actions}>
            <button className={styles.actionButton} onClick={onEdit} title="Edit">
              ✎
            </button>
            <button className={styles.actionButton} onClick={onTogglePin} title="Toggle pin">
              📌
            </button>
            <button className={styles.actionButton} onClick={onToggleFavorite} title="Toggle favorite">
              ⭐
            </button>
            <button className={styles.actionButton} onClick={onDelete} title="Delete">
              🗑
            </button>
          </div>
        )}
      </div>

      {note.content_preview && (
        <div className={styles.preview}>
          <p>{note.content_preview}</p>
        </div>
      )}

      <div className={styles.cardFooter}>
        <div className={styles.metadata}>
          <span className={styles.date}>{formattedDate}</span>
          <span className={styles.separator}>·</span>
          <span className={styles.readingTime}>{readingTime}</span>
          {note.word_count > 0 && (
            <>
              <span className={styles.separator}>·</span>
              <span className={styles.wordCount}>{note.word_count} words</span>
            </>
          )}
        </div>

        <div className={styles.stats}>
          {note.tag_count > 0 && (
            <span className={styles.stat} title={`${note.tag_count} tags`}>
              🏷️ {note.tag_count}
            </span>
          )}
          {note.has_related_notes && (
            <span className={styles.stat} title="Has related notes">
              🔗
            </span>
          )}
          {note.has_tasks && (
            <span className={styles.stat} title="Has linked tasks">
              ✓
            </span>
          )}
        </div>
      </div>
    </div>
  );
};