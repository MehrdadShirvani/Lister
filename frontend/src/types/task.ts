import type { Timestamps } from './base';
import type { ListPreview } from './list';
import type { TagResponse } from './tag';

// Task status enum
export const Task_Status = {
    NOT_STARTED: "not_started",
    IN_PROGRESS: "in_progress",
    COMPLETED: "completed",
    BLOCKED: "blocked",
    CANCELLED: "cancelled"
} as const

export type TaskStatus = typeof Task_Status[keyof typeof Task_Status];

// Task type enum
export const Task_Type = {
    TASK: "task",
    PROJECT: "project",
    MILESTONE: "milestone",
    RECURRING: "recurring"
} as const
export type TaskType = typeof Task_Type[keyof typeof Task_Type];

// URL for task
export interface TaskUrl {
    url: string;
    created_at: string;
}

// Base Task
export interface TaskBase {
    title: string;
    type: TaskType;
    description?: string;
    scheduled_date?: string; // ISO date
    estimated_duration?: number; // minutes
    priority?: number;
    status: TaskStatus;
}

// Task Create
export interface TaskCreate extends TaskBase {
    list_id?: number;
    parent_task_id?: number;
    tag_ids?: number[];
    urls?: string[];
}

// Task Update
export interface TaskUpdate {
    title?: string;
    description?: string;
    type?: TaskType;
    list_id?: number;
    parent_task_id?: number;
    scheduled_date?: string;
    estimated_duration?: number;
    priority?: number;
    status?: TaskStatus;
    completed_at?: string;

    // Tag operations
    tag_ids?: number[]; // Replace all
    add_tag_ids?: number[];
    remove_tag_ids?: number[];

    // URL operations
    urls?: string[]; // Replace all
    add_urls?: string[];
    remove_urls?: string[];
}

// Task Response (basic)
export interface TaskResponse extends TaskBase, Timestamps {
    id: number;
    account_id: number;
    list_id?: number;
    parent_task_id?: number;
    completed_at?: string;

    // Relations
    tags: TagResponse[];
    urls: TaskUrl[];
    subtask_count: number;
}

// Task Preview (for lists)
export interface TaskPreview {
    id: number;
    title: string;
    description?: string;
    status: TaskStatus;
    created_at: string,
    updated_at?: string,
    priority?: number;
    scheduled_date?: string;
    has_subtasks: boolean;
    subtask_count: number;
}

// Task Hierarchy Node
export interface TaskHierarchyNode {
    id: number;
    title: string;
    description?: string;
    type: string;
    status: string;
    priority?: number;
    scheduled_date?: string;
    depth: number;
    children: TaskHierarchyNode[];
}

// Task Detail Response
export interface TaskDetailResponse extends TaskResponse {
    parent_task?: TaskResponse;
    subtasks: TaskResponse[];
    lists: ListPreview[];
}

// Task Filter Params
export interface TaskFilterParams {
    list_id?: number;
    status?: TaskStatus;
    type?: TaskType;
    priority_min?: number;
    priority_max?: number;
    scheduled_before?: string;
    scheduled_after?: string;
    has_parent?: boolean;
    parent_task_id?: number;
    tag_ids?: number[];
    search?: string;
    is_completed?: boolean;
    is_planned?: boolean;
}