// components/dashboard/tabs/NotesTab.tsx
import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import styles from './NotesTab.module.css';
import api from '../../../../services/api';
import type { NotePreview, NoteFilterParams } from '../../../../types';
import { NoteFilterBar } from './NoteFilterBar';
import { NoteCard } from './NoteCard';

export const NotesTab: React.FC = () => {
  const navigate = useNavigate();
  const [notes, setNotes] = useState<NotePreview[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [filters, setFilters] = useState<NoteFilterParams>({});
  const [searchQuery, setSearchQuery] = useState('');

  const fetchNotes = useCallback(async () => {
    setIsLoading(true);
    try {
      const params: any = { ...filters };
      if (searchQuery) {
        params.search = searchQuery;
      }
      const data = await api.Notes.getAll(params);
      setNotes(data);
    } catch (error) {
      console.error('Failed to fetch notes:', error);
    } finally {
      setIsLoading(false);
    }
  }, [filters, searchQuery]);

  useEffect(() => {
    fetchNotes();
  }, [fetchNotes]);

  const handleCreateNote = () => {
    navigate('/notes/new');
  };

  const handleEditNote = (noteId: number) => {
    navigate(`/notes/${noteId}`);
  };

  const handleTogglePin = async (noteId: number) => {
    try {
      await api.Notes.togglePin(noteId);
      fetchNotes(); // Refresh the list
    } catch (error) {
      console.error('Failed to toggle pin:', error);
    }
  };

  const handleToggleFavorite = async (noteId: number) => {
    try {
      await api.Notes.toggleFavorite(noteId);
      fetchNotes();
    } catch (error) {
      console.error('Failed to toggle favorite:', error);
    }
  };

  const handleDeleteNote = async (noteId: number) => {
    if (window.confirm('Are you sure you want to delete this note?')) {
      try {
        await api.Notes.delete(noteId);
        fetchNotes();
      } catch (error) {
        console.error('Failed to delete note:', error);
      }
    }
  };

  // Separate pinned and unpinned notes
  const { pinnedNotes, unpinnedNotes } = useMemo(() => {
    return {
      pinnedNotes: notes.filter(n => n.is_pinned),
      unpinnedNotes: notes.filter(n => !n.is_pinned)
    };
  }, [notes]);

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h2 className={styles.title}>Notes</h2>
        <button className={styles.createButton} onClick={handleCreateNote}>
          <span className={styles.createIcon}>+</span>
          New Note
        </button>
      </div>

      <NoteFilterBar
        filters={filters}
        onFilterChange={setFilters}
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
      />

      {isLoading ? (
        <div className={styles.loadingContainer}>
          <div className={styles.loadingSpinner} />
          <p>Loading notes...</p>
        </div>
      ) : (
        <div className={styles.notesContainer}>
          {pinnedNotes.length > 0 && (
            <div className={styles.section}>
              <div className={styles.sectionHeader}>
                <span className={styles.sectionIcon}>📌</span>
                <h3 className={styles.sectionTitle}>Pinned</h3>
              </div>
              <div className={styles.notesGrid}>
                {pinnedNotes.map(note => (
                  <NoteCard
                    key={note.id}
                    note={note}
                    onEdit={() => handleEditNote(note.id)}
                    onTogglePin={() => handleTogglePin(note.id)}
                    onToggleFavorite={() => handleToggleFavorite(note.id)}
                    onDelete={() => handleDeleteNote(note.id)}
                  />
                ))}
              </div>
            </div>
          )}

          {unpinnedNotes.length > 0 && (
            <div className={styles.section}>
              <div className={styles.sectionHeader}>
                <span className={styles.sectionIcon}>📝</span>
                <h3 className={styles.sectionTitle}>All Notes</h3>
              </div>
              <div className={styles.notesGrid}>
                {unpinnedNotes.map(note => (
                  <NoteCard
                    key={note.id}
                    note={note}
                    onEdit={() => handleEditNote(note.id)}
                    onTogglePin={() => handleTogglePin(note.id)}
                    onToggleFavorite={() => handleToggleFavorite(note.id)}
                    onDelete={() => handleDeleteNote(note.id)}
                  />
                ))}
              </div>
            </div>
          )}

          {notes.length === 0 && !isLoading && (
            <div className={styles.emptyState}>
              <div className={styles.emptyStateIcon}>📝</div>
              <h3 className={styles.emptyStateTitle}>No notes yet</h3>
              <p className={styles.emptyStateDescription}>
                Create your first note to start capturing your thoughts and reflections.
              </p>
              <button className={styles.emptyStateButton} onClick={handleCreateNote}>
                Create a note
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
};