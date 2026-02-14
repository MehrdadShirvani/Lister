import type { Timestamps } from "./base";
import type { TagResponse } from "./tag";
import type { TaskHierarchyNode, TaskPreview } from "./task";

// Base List
export interface ListBase {
    title: string;
    description?: string;
    priority?: number;
    status: "active" | "archived" | "frozen" | "completed";
}

// List Create
export interface ListCreate extends ListBase {
    tag_ids?: number[];
}

// List Update
export interface ListUpdate {
    title?: string;
    description?: string;
    priority?: number;
    status?: "active" | "archived" | "frozen" | "completed";

    // Tag operations
    tag_ids?: number[]; // Replace all
    add_tag_ids?: number[];
    remove_tag_ids?: number[];
}

// List Response (basic)
export interface ListResponse extends ListBase, Timestamps {
    id: number;
    account_id: number;

    // Stats
    task_count: number;
    completed_task_count: number;
    active_task_count: number;

    // Tags
    tags: TagResponse[];
}

// List Preview (for dropdowns, etc.)
export interface ListPreview {
    id: number;
    title: string;
    task_count: number;
    priority?: number;
}

// List Detail Response
export interface ListDetailResponse extends ListResponse {
    tasks: TaskPreview[];
    task_hierarchy: TaskHierarchyNode[];
    total_subtasks: number;
    estimated_total_duration?: number;
}

// List Filter Params
export interface ListFilterParams {
    status?: "active" | "archived" | "frozen" | "completed";
    priority_min?: number;
    priority_max?: number;
    tag_ids?: number[];
    search?: string;
    has_tasks?: boolean;
    created_after?: string;
    created_before?: string;
}