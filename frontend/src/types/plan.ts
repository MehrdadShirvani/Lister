import type { Timestamps } from './base';
import type { TaskPreview } from './task';
import type { NotePreview } from './note';
import type { TimeBlockPreview } from './timeblock';

// Plan status enum
export type PlanStatus = {
  PLANNED: "planned",
  IN_PROGRESS: "in_progress",
  COMPLETED: "completed",
  CANCELLED: "cancelled",
  MISSED: "missed"
}

// Base Plan
export interface PlanBase {
  task_id?: number;
  note_id?: number;
  time_block_id?: number;
  start_time?: string;
  end_time?: string;
  status: PlanStatus;
  progress: number; // 0-100
  notes?: string;
}

// Plan Create (manual)
export interface PlanCreate extends PlanBase { }

// Plan from Suggestion
export interface PlanFromSuggestion {
  suggestion_task_id: number;
  suggestion_time_block_id: number;
  suggestion_title: string;
  start_time?: string;
  end_time?: string;
  notes?: string;
}

// Plan Update
export interface PlanUpdate {
  task_id?: number;
  note_id?: number;
  time_block_id?: number;
  start_time?: string;
  end_time?: string;
  actual_start_time?: string;
  actual_end_time?: string;
  status?: PlanStatus;
  progress?: number;
  notes?: string;
}

// Plan Action
export interface PlanAction {
  action: 'start' | 'pause' | 'resume' | 'complete' | 'cancel';
  timestamp?: string;
  notes?: string;
}

// Plan Response
export interface PlanResponse extends PlanBase, Timestamps {
  id: number;
  account_id: number;
  actual_start_time?: string;
  actual_end_time?: string;
  completion_rate: number;

  // Related data
  task_title?: string;
  task_status?: string;
  note_title?: string;
  time_block_title?: string;

  // Suggestion source
  from_suggestion: boolean;
  suggestion_details?: {
    task_id: number;
    time_block_id: number;
    title: string;
  };
}

// Plan Preview (for lists)
export interface PlanPreview {
  id: number;
  task_id?: number;
  task_title?: string;
  start_time?: string;
  end_time?: string;
  status: PlanStatus;
  progress: number;
}

// Plan Detail
export interface PlanDetail extends PlanResponse {
  task?: TaskPreview;
  note?: NotePreview;
  time_block?: TimeBlockPreview;
}

// Plan Filter Params
export interface PlanFilterParams {
  status?: PlanStatus;
  task_id?: number;
  time_block_id?: number;
  has_note?: boolean;
  date_from?: string;
  date_to?: string;
  is_recurring?: boolean;
  progress_min?: number;
  progress_max?: number;
  from_suggestion?: boolean;
}