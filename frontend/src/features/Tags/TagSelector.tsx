// components/dashboard/tags/TagSelector.tsx
import React, { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import styles from './TagSelector.module.css';

import { CreateTagModal } from './CreateTagModal';
import api from '../../services/api';
import type { TagType } from '../../types';
import { type TagResponse, TAG_TYPES, COMMON_TAGS, TAG_TYPE_COLORS } from '../../types/tag';

interface TagSelectorProps {
  selectedTagIds: number[];
  onChange: (tagIds: number[]) => void;
  filterTypes?: TagType[];
  showCreate?: boolean;
}

export const TagSelector: React.FC<TagSelectorProps> = React.memo(({
  selectedTagIds,
  onChange,
  filterTypes,
  showCreate = true,
}) => {
  const [tags, setTags] = useState<TagResponse[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [selectedType, setSelectedType] = useState<TagType | 'all'>('all');
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [collapsedGroups, setCollapsedGroups] = useState<Record<string, boolean>>({});
  const searchInputRef = useRef<HTMLInputElement>(null);
  const initialFetchDone = useRef(false);

  // Fetch tags only once on mount
  const fetchTags = useCallback(async () => {
    setIsLoading(true);
    try {
      const params: any = {};
      if (filterTypes && filterTypes.length > 0) {
        // If we have filterTypes, we might want to pass them to the API
        // But since the API might not support multiple types, we'll fetch all and filter client-side
      }
      const data = await api.Tags.getAll(params);
      setTags(data);
    } catch (error) {
      console.error('Failed to fetch tags:', error);
    } finally {
      setIsLoading(false);
    }
  }, [filterTypes]);

  useEffect(() => {
    if (!initialFetchDone.current) {
      fetchTags();
      initialFetchDone.current = true;
    }
  }, [fetchTags]);

  // Memoize filtered tags to prevent recalculating on every render
  const filteredTags = useMemo(() => {
    let filtered = [...tags];

    // Apply type filter
    if (selectedType !== 'all') {
      filtered = filtered.filter(tag => tag.type === selectedType);
    } else if (filterTypes && filterTypes.length > 0) {
      filtered = filtered.filter(tag => tag.type && filterTypes.includes(tag.type as TagType));
    }

    // Apply search filter
    if (search) {
      const searchLower = search.toLowerCase();
      filtered = filtered.filter(tag => 
        tag.title.toLowerCase().includes(searchLower) ||
        tag.description?.toLowerCase().includes(searchLower)
      );
    }

    // Sort by type then name
    filtered.sort((a, b) => {
      if (a.type === b.type) {
        return a.title.localeCompare(b.title);
      }
      return (a.type || '').localeCompare(b.type || '');
    });

    return filtered;
  }, [tags, search, selectedType, filterTypes]);

  // Memoize tags by type
  const tagsByType = useMemo(() => {
    return filteredTags.reduce((acc, tag) => {
      const type = tag.type || 'Other';
      if (!acc[type]) {
        acc[type] = [];
      }
      acc[type].push(tag);
      return acc;
    }, {} as Record<string, TagResponse[]>);
  }, [filteredTags]);

  // Handlers
  const handleTagToggle = useCallback((tagId: number) => {
    if (selectedTagIds.includes(tagId)) {
      onChange(selectedTagIds.filter(id => id !== tagId));
    } else {
      onChange([...selectedTagIds, tagId]);
    }
  }, [selectedTagIds, onChange]);

  const handleQuickTagSelect = useCallback(async (type: TagType, tagName: string) => {
    // Check if tag already exists
    const existingTag = tags.find(t => t.type === type && t.title === tagName);
    if (existingTag) {
      handleTagToggle(existingTag.id);
      return;
    }

    // Create new tag
    try {
      const newTag = await api.Tags.createUserTag({
        title: tagName,
        type: type,
      });
      setTags(prev => [...prev, newTag]);
      handleTagToggle(newTag.id);
    } catch (error) {
      console.error('Failed to create tag:', error);
    }
  }, [tags, handleTagToggle]);

  const toggleGroup = useCallback((type: string) => {
    setCollapsedGroups(prev => ({
      ...prev,
      [type]: !prev[type]
    }));
  }, []);

  const handleClearSearch = useCallback(() => setSearch(''), []);
  
  const handleTypeChange = useCallback((e: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedType(e.target.value as TagType | 'all');
  }, []);

  const handleSearchChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setSearch(e.target.value);
  }, []);

  const handleCreateModalOpen = useCallback(() => setIsCreateModalOpen(true), []);
  
  const handleCreateModalClose = useCallback(() => setIsCreateModalOpen(false), []);
  
  const handleTagCreated = useCallback((newTag: TagResponse) => {
    setTags(prev => [...prev, newTag]);
    setIsCreateModalOpen(false);
  }, []);

  const handleClearAll = useCallback(() => {
    onChange([]);
  }, [onChange]);

  // Get available types from tags
  const availableTypes = useMemo(() => Object.keys(tagsByType).sort(), [tagsByType]);

  return (
    <div className={styles.container}>
      {/* Search and filter bar */}
      <div className={styles.toolbar}>
        <div className={styles.searchBar}>
          <span className={styles.searchIcon}>🔍</span>
          <input
            ref={searchInputRef}
            type="text"
            placeholder="Search tags..."
            value={search}
            onChange={handleSearchChange}
            className={styles.searchInput}
          />
          {search && (
            <button
              className={styles.clearSearch}
              onClick={handleClearSearch}
              type="button"
            >
              ×
            </button>
          )}
        </div>

        <select
          value={selectedType}
          onChange={handleTypeChange}
          className={styles.typeFilter}
        >
          <option value="all">All types</option>
          {Object.values(TAG_TYPES).map(type => (
            <option key={type} value={type}>{type}</option>
          ))}
        </select>
      </div>

      {/* Quick suggestions */}
      {search === '' && selectedType !== 'all' && COMMON_TAGS[selectedType] && (
        <div className={styles.quickSuggestions}>
          <div className={styles.suggestionsHeader}>
            <span className={styles.suggestionsTitle}>Quick add</span>
          </div>
          <div className={styles.suggestionsList}>
            {COMMON_TAGS[selectedType].map(tagName => {
              const existingTag = tags.find(t => t.type === selectedType && t.title === tagName);
              const exists = !!existingTag;
              const isSelected = exists ? selectedTagIds.includes(existingTag.id) : false;
              
              return (
                <button
                  key={tagName}
                  className={`${styles.suggestionChip} ${isSelected ? styles.suggestionSelected : ''}`}
                  onClick={() => handleQuickTagSelect(selectedType as TagType, tagName)}
                  disabled={exists && isSelected}
                  type="button"
                >
                  {tagName}
                  {exists && !isSelected && ' +'}
                  {isSelected && ' ✓'}
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Selected tags summary */}
      {selectedTagIds.length > 0 && (
        <div className={styles.selectedSummary}>
          <span className={styles.selectedCount}>
            {selectedTagIds.length} tag{selectedTagIds.length !== 1 ? 's' : ''} selected
          </span>
          <button
            className={styles.clearAll}
            onClick={handleClearAll}
            type="button"
          >
            Clear all
          </button>
        </div>
      )}

      {/* Tags by type */}
      <div className={styles.tagsContainer}>
        {isLoading ? (
          <div className={styles.loadingContainer}>
            <div className={styles.loadingSpinner} />
            <p>Loading tags...</p>
          </div>
        ) : filteredTags.length === 0 ? (
          <div className={styles.emptyState}>
            <p>No tags found</p>
            {search && (
              <button
                className={styles.createTagButton}
                onClick={handleCreateModalOpen}
                type="button"
              >
                Create "{search}"
              </button>
            )}
          </div>
        ) : (
          Object.entries(tagsByType).map(([type, typeTags]) => (
            <div key={type} className={styles.tagGroup}>
              <div 
                className={styles.tagGroupHeader}
                onClick={() => toggleGroup(type)}
              >
                <span className={styles.tagGroupTitle}>
                  {type}
                  <span className={styles.tagGroupCount}>({typeTags.length})</span>
                </span>
                <button className={styles.collapseButton} type="button">
                  {collapsedGroups[type] ? '▶' : '▼'}
                </button>
              </div>
              
              {!collapsedGroups[type] && (
                <div className={styles.tagGroupContent}>
                  {typeTags.map(tag => {
                    const isSelected = selectedTagIds.includes(tag.id);
                    const colors = TAG_TYPE_COLORS[tag.type as TagType] || { 
                      bg: 'var(--color-bg-tertiary)', 
                      text: 'var(--color-text-secondary)' 
                    };
                    
                    return (
                      <button
                        key={tag.id}
                        className={`${styles.tagButton} ${isSelected ? styles.tagSelected : ''}`}
                        onClick={() => handleTagToggle(tag.id)}
                        style={{
                          '--tag-bg': colors.bg,
                          '--tag-color': colors.text,
                        } as React.CSSProperties}
                        type="button"
                      >
                        <span className={styles.tagName}>{tag.title}</span>
                        {tag.description && (
                          <span className={styles.tagTooltip}>{tag.description}</span>
                        )}
                      </button>
                    );
                  })}
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {/* Create new tag button */}
      {showCreate && (
        <div className={styles.createSection}>
          <button
            className={styles.createButton}
            onClick={handleCreateModalOpen}
            type="button"
          >
            <span className={styles.createIcon}>+</span>
            Create new tag
          </button>
        </div>
      )}

      {/* Create tag modal */}
      <CreateTagModal
        isOpen={isCreateModalOpen}
        onClose={handleCreateModalClose}
        onTagCreated={handleTagCreated}
        initialType={selectedType !== 'all' ? selectedType : undefined}
        initialName={search || undefined}
      />
    </div>
  );
});

TagSelector.displayName = 'TagSelector';