import type { Timestamps } from './base';
import type { TagResponse } from './tag';

// Recurrence options
export type RecurrenceType = {
  NONE: "none",
  DAILY: "daily",
  WEEKLY: "weekly",
  MONTHLY: "monthly",
  WEEKDAYS: "weekdays",
  WEEKENDS: "weekends"
}

// Block type options
export type BlockType = {
  WORK: "work",
  PERSONAL: "personal",
  BREAK: "break",
  MEETING: "meeting",
  TASK: "task",
  FOCUS: "focus",
  GENERAL: "general"
}

// Block status options
export type BlockStatus = {
  PLANNED: "planned",
  IN_PROGRESS: "in_progress",
  COMPLETED: "completed",
  CANCELLED: "cancelled"
}

// Energy info
export interface EnergyInfo {
  level?: string; // Very Low, Low, Medium, High, Very High
  tag_id?: number;
}

// Base TimeBlock
export interface TimeBlockBase {
  title: string;
  description?: string;
  start_time: string; // ISO datetime
  end_time: string; // ISO datetime
  block_type: BlockType;
  status: BlockStatus;
  is_recurring: boolean;
  recurrence_rule?: RecurrenceType;
  day_of_week?: number; // 0-6
}

// TimeBlock Create
export interface TimeBlockCreate extends TimeBlockBase {
  energy_tag_ids?: number[];
  other_tag_ids?: number[];
}

// TimeBlock Update
export interface TimeBlockUpdate {
  title?: string;
  description?: string;
  start_time?: string;
  end_time?: string;
  block_type?: BlockType;
  status?: BlockStatus;
  is_recurring?: boolean;
  recurrence_rule?: RecurrenceType;
  day_of_week?: number;
  energy_tag_ids?: number[];
  other_tag_ids?: number[];
}

// TimeBlock Response
export interface TimeBlockResponse extends TimeBlockBase, Timestamps {
  id: number;
  account_id: number;

  // Tags organized
  energy_tag: EnergyInfo | null;
  other_tags: TagResponse[];
}

// Preview for lists
export interface TimeBlockPreview {
  id: number;
  title: string;
  start_time: string;
  end_time: string;
  block_type: BlockType;
  status: BlockStatus;
  energy_level?: string;
}

// TimeBlock Filter Params
export interface TimeBlockFilterParams {
  start_date?: string;
  end_date?: string;
  block_type?: BlockType;
  status?: BlockStatus;
  is_recurring?: boolean;
  energy_level?: string;
  tag_ids?: number[];
  search?: string;
}