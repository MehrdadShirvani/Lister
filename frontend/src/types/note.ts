import type { Timestamps } from "./base";
import type { TagResponse } from "./tag";

// Formatting data type (flexible)
export interface NoteFormatting {
    theme?: string;
    font_size?: number;
    show_line_numbers?: boolean;
    [key: string]: any;
}

// Base Note
export interface NoteBase {
    title: string;
    content?: string;
    quality_score?: number;
    is_pinned: boolean;
    is_favorite: boolean;
    formatting_data: NoteFormatting;
}

// Note Create
export interface NoteCreate extends NoteBase {
    plan_id?: number;
    parent_note_id?: number;
    tag_ids?: number[];
    related_note_ids?: number[];
    task_ids?: number[];
}

// Note Update
export interface NoteUpdate {
    title?: string;
    content?: string;
    quality_score?: number;
    is_pinned?: boolean;
    is_archived?: boolean;
    is_favorite?: boolean;
    formatting_data?: NoteFormatting;

    // Tag operations
    tag_ids?: number[];
    add_tag_ids?: number[];
    remove_tag_ids?: number[];

    // Related notes operations
    related_note_ids?: number[];
    add_related_note_ids?: number[];
    remove_related_note_ids?: number[];

    // Task operations
    task_ids?: number[];
    add_task_ids?: number[];
    remove_task_ids?: number[];
}

// Related Task (minimal)
export interface RelatedTask {
    id: number;
    title: string;
    status: string;
    priority?: number;
}

// Related Note (minimal)
export interface RelatedNote {
    id: number;
    title: string;
    preview?: string;
}

// Related Plan (minimal)
export interface RelatedPlan {
    id: number;
    task_id?: number;
    time_block_id?: number;
    start_time?: string;
    status: string;
}

// Note Preview (for lists)
export interface NotePreview {
    id: number;
    title: string;
    content_preview?: string;
    created_at: string;
    updated_at?: string;
    is_pinned: boolean;
    is_favorite: boolean;
    word_count: number;
    reading_time_minutes: number;
    tag_count: number;
    has_related_notes: boolean;
    has_tasks: boolean;
}

// Note Response (full)
export interface NoteResponse extends NoteBase, Timestamps {
    id: number;
    account_id: number;
    plan_id?: number;
    parent_note_id?: number;
    last_accessed_at?: string;
    word_count: number;
    reading_time_minutes: number;
    is_archived: boolean;

    // Relations
    tags: TagResponse[];
    parent_note?: NotePreview;
    child_notes: NotePreview[];
    related_notes: RelatedNote[];
    tasks: RelatedTask[];
    plan?: RelatedPlan;
}

// Note Filter Params
export interface NoteFilterParams {
    search?: string;
    tag_ids?: number[];
    is_pinned?: boolean;
    is_favorite?: boolean;
    is_archived?: boolean;
    is_follow_up?: boolean;
    has_plan?: boolean;
    has_tasks?: boolean;
    has_related_notes?: boolean;
    quality_score_min?: number;
    quality_score_max?: number;
    created_after?: string;
    created_before?: string;
    updated_after?: string;
    sort_by?: 'created_at' | 'updated_at' | 'title' | 'quality_score' | 'word_count' | 'reading_time_minutes';
    sort_desc?: boolean;
}