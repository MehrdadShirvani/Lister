// pages/NoteEditorPage.tsx
import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import styles from './NoteEditorPage.module.css';
import type { NoteCreate, NoteResponse, NoteUpdate } from '../../../../types';
import api from '../../../../services/api';
import { TagSelector } from '../../../Tags/TagSelector';
import { RichTextEditor } from './RichTextEditor';

export const NoteEditorPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const isNewNote = id === 'new';

  const [note, setNote] = useState<NoteResponse | null>(null);
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [selectedTagIds, setSelectedTagIds] = useState<number[]>([]);
  const [isPinned, setIsPinned] = useState(false);
  const [isFavorite, setIsFavorite] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch note if editing
  useEffect(() => {
    if (!isNewNote && id) {
      fetchNote(parseInt(id));
    }
  }, [isNewNote, id]);

  const fetchNote = async (noteId: number) => {
    setIsLoading(true);
    try {
      const data = await api.Notes.getById(noteId);
      setNote(data);
      setTitle(data.title);
      setContent(data.content || '');
      setSelectedTagIds(data.tags.map(t => t.id));
      setIsPinned(data.is_pinned);
      setIsFavorite(data.is_favorite);
    } catch (error) {
      console.error('Failed to fetch note:', error);
      setError('Failed to load note');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = useCallback(async () => {
    if (!title.trim()) {
      setError('Title is required');
      return;
    }

    setIsSaving(true);
    setError(null);

    try {
      if (isNewNote) {
        const noteData: NoteCreate = {
          title,
          content,
          is_pinned: isPinned,
          is_favorite: isFavorite,
          formatting_data: {},
          tag_ids: selectedTagIds,
        };
        const created = await api.Notes.create(noteData);
        navigate(`/notes/${created.id}`);
      } else if (note) {
        const noteData: NoteUpdate = {
          title,
          content,
          is_pinned: isPinned,
          is_favorite: isFavorite,
          tag_ids: selectedTagIds,
        };
        await api.Notes.update(note.id, noteData);
        // Refresh note data
        fetchNote(note.id);
      }
    } catch (error) {
      console.error('Failed to save note:', error);
      setError('Failed to save note');
    } finally {
      setIsSaving(false);
    }
  }, [isNewNote, note, title, content, isPinned, isFavorite, selectedTagIds, navigate]);

  const handleCancel = () => {
    navigate('/dashboard?tab=notes');
  };

  if (isLoading) {
    return (
      <div className={styles.loadingContainer}>
        <div className={styles.loadingSpinner} />
        <p>Loading note...</p>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <div className={styles.headerLeft}>
          <button className={styles.backButton} onClick={handleCancel}>
            ← Back to notes
          </button>
          <h1 className={styles.title}>
            {isNewNote ? 'Create New Note' : 'Edit Note'}
          </h1>
        </div>
        <div className={styles.headerActions}>
          <button
            className={`${styles.iconButton} ${isPinned ? styles.active : ''}`}
            onClick={() => setIsPinned(!isPinned)}
            title={isPinned ? 'Unpin' : 'Pin'}
          >
            📌
          </button>
          <button
            className={`${styles.iconButton} ${isFavorite ? styles.active : ''}`}
            onClick={() => setIsFavorite(!isFavorite)}
            title={isFavorite ? 'Remove from favorites' : 'Add to favorites'}
          >
            ⭐
          </button>
          <button className={styles.saveButton} onClick={handleSave} disabled={isSaving}>
            {isSaving ? 'Saving...' : 'Save'}
          </button>
        </div>
      </div>

      {error && (
        <div className={styles.errorContainer}>
          <span className={styles.errorIcon}>🌙</span>
          <p className={styles.errorMessage}>{error}</p>
        </div>
      )}

      <div className={styles.content}>
        <div className={styles.mainSection}>
          <input
            type="text"
            className={styles.titleInput}
            placeholder="Note title..."
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />

          <RichTextEditor
            content={content}
            onChange={setContent}
            placeholder="Start writing your thoughts..."
            maxLength={10000}
          />
        </div>

        <div className={styles.sidebar}>
          <div className={styles.sidebarSection}>
            <h3 className={styles.sectionTitle}>Tags</h3>
            <TagSelector
              selectedTagIds={selectedTagIds}
              onChange={setSelectedTagIds}
            />
          </div>

          {note && (
            <>
              {note.word_count > 0 && (
                <div className={styles.sidebarSection}>
                  <h3 className={styles.sectionTitle}>Stats</h3>
                  <div className={styles.stats}>
                    <div className={styles.stat}>
                      <span className={styles.statLabel}>Words</span>
                      <span className={styles.statValue}>{note.word_count}</span>
                    </div>
                    <div className={styles.stat}>
                      <span className={styles.statLabel}>Reading time</span>
                      <span className={styles.statValue}>{note.reading_time_minutes} min</span>
                    </div>
                    <div className={styles.stat}>
                      <span className={styles.statLabel}>Created</span>
                      <span className={styles.statValue}>
                        {new Date(note.created_at).toLocaleDateString()}
                      </span>
                    </div>
                    {note.updated_at && note.updated_at !== note.created_at && (
                      <div className={styles.stat}>
                        <span className={styles.statLabel}>Updated</span>
                        <span className={styles.statValue}>
                          {new Date(note.updated_at).toLocaleDateString()}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {(note.related_notes?.length > 0 || note.tasks?.length > 0) && (
                <div className={styles.sidebarSection}>
                  <h3 className={styles.sectionTitle}>Related</h3>
                  
                  {note.tasks && note.tasks.length > 0 && (
                    <div className={styles.relatedGroup}>
                      <h4 className={styles.relatedTitle}>Tasks</h4>
                      <div className={styles.relatedList}>
                        {note.tasks.map(task => (
                          <div key={task.id} className={styles.relatedItem}>
                            <span className={styles.relatedIcon}>✓</span>
                            <span className={styles.relatedName}>{task.title}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {note.related_notes && note.related_notes.length > 0 && (
                    <div className={styles.relatedGroup}>
                      <h4 className={styles.relatedTitle}>Related Notes</h4>
                      <div className={styles.relatedList}>
                        {note.related_notes.map(relatedNote => (
                          <div key={relatedNote.id} className={styles.relatedItem}>
                            <span className={styles.relatedIcon}>📝</span>
                            <span className={styles.relatedName}>{relatedNote.title}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};