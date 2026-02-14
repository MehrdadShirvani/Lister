// components/dashboard/notes/NoteFilterBar.tsx
import React, { useState, useEffect } from 'react';
import styles from './NoteFilterBar.module.css';
import type { NoteFilterParams } from '../../../../types';
import type { TagResponse } from '../../../../types/tag';
import api from '../../../../services/api';

interface NoteFilterBarProps {
  filters: NoteFilterParams;
  onFilterChange: (filters: NoteFilterParams) => void;
  searchQuery: string;
  onSearchChange: (query: string) => void;
}

export const NoteFilterBar: React.FC<NoteFilterBarProps> = ({
  filters,
  onFilterChange,
  searchQuery,
  onSearchChange,
}) => {
  const [tags, setTags] = useState<TagResponse[]>([]);
  const [showFilters, setShowFilters] = useState(false);
  const [selectedTagIds, setSelectedTagIds] = useState<number[]>(filters.tag_ids || []);

  useEffect(() => {
    fetchTags();
  }, []);

  const fetchTags = async () => {
    try {
      const data = await api.Tags.getAll();
      setTags(data);
    } catch (error) {
      console.error('Failed to fetch tags:', error);
    }
  };

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onSearchChange(e.target.value);
  };

  const handleFilterChange = (key: keyof NoteFilterParams, value: any) => {
    onFilterChange({ ...filters, [key]: value });
  };

  const handleTagToggle = (tagId: number) => {
    const newTagIds = selectedTagIds.includes(tagId)
      ? selectedTagIds.filter(id => id !== tagId)
      : [...selectedTagIds, tagId];
    
    setSelectedTagIds(newTagIds);
    onFilterChange({ ...filters, tag_ids: newTagIds });
  };

  const handleSortChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const [sort_by, sort_desc] = e.target.value.split(':');
    onFilterChange({ 
      ...filters, 
      sort_by: sort_by as any,
      sort_desc: sort_desc === 'desc'
    });
  };

  const clearFilters = () => {
    setSelectedTagIds([]);
    onFilterChange({});
    onSearchChange('');
  };

  const getSortValue = () => {
    if (!filters.sort_by) return 'updated_at:desc';
    return `${filters.sort_by}:${filters.sort_desc ? 'desc' : 'asc'}`;
  };

  return (
    <div className={styles.container}>
      <div className={styles.searchBar}>
        <span className={styles.searchIcon}>🔍</span>
        <input
          type="text"
          placeholder="Search notes..."
          value={searchQuery}
          onChange={handleSearchChange}
          className={styles.searchInput}
        />
        <button
          className={`${styles.filterToggle} ${showFilters ? styles.active : ''}`}
          onClick={() => setShowFilters(!showFilters)}
        >
          ⚙️
        </button>
      </div>

      {showFilters && (
        <div className={styles.filtersPanel}>
          <div className={styles.filterSection}>
            <h4 className={styles.filterTitle}>Sort by</h4>
            <select
              value={getSortValue()}
              onChange={handleSortChange}
              className={styles.sortSelect}
            >
              <option value="updated_at:desc">Recently updated</option>
              <option value="created_at:desc">Recently created</option>
              <option value="title:asc">Title A-Z</option>
              <option value="title:desc">Title Z-A</option>
              <option value="quality_score:desc">Highest quality</option>
              <option value="word_count:desc">Longest</option>
              <option value="reading_time_minutes:desc">Longest read</option>
            </select>
          </div>

          <div className={styles.filterSection}>
            <h4 className={styles.filterTitle}>Status</h4>
            <div className={styles.checkboxGroup}>
              <label className={styles.checkbox}>
                <input
                  type="checkbox"
                  checked={filters.is_pinned || false}
                  onChange={(e) => handleFilterChange('is_pinned', e.target.checked || undefined)}
                />
                <span>Pinned only</span>
              </label>
              <label className={styles.checkbox}>
                <input
                  type="checkbox"
                  checked={filters.is_favorite || false}
                  onChange={(e) => handleFilterChange('is_favorite', e.target.checked || undefined)}
                />
                <span>Favorites only</span>
              </label>
              <label className={styles.checkbox}>
                <input
                  type="checkbox"
                  checked={filters.has_tasks || false}
                  onChange={(e) => handleFilterChange('has_tasks', e.target.checked || undefined)}
                />
                <span>Has linked tasks</span>
              </label>
              <label className={styles.checkbox}>
                <input
                  type="checkbox"
                  checked={filters.has_related_notes || false}
                  onChange={(e) => handleFilterChange('has_related_notes', e.target.checked || undefined)}
                />
                <span>Has related notes</span>
              </label>
            </div>
          </div>

          <div className={styles.filterSection}>
            <h4 className={styles.filterTitle}>Tags</h4>
            <div className={styles.tagList}>
              {tags.map(tag => (
                <button
                  key={tag.id}
                  className={`${styles.tagButton} ${selectedTagIds.includes(tag.id) ? styles.tagSelected : ''}`}
                  onClick={() => handleTagToggle(tag.id)}
                >
                  {tag.title}
                </button>
              ))}
            </div>
          </div>

          <div className={styles.filterActions}>
            <button className={styles.clearButton} onClick={clearFilters}>
              Clear all filters
            </button>
          </div>
        </div>
      )}
    </div>
  );
};