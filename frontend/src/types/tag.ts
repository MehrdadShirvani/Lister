import type { Timestamps } from './base';

// Tag types enum
export const TAG_TYPES = {
  MOOD: "Mood",
  ENERGY: "Energy",
  VIBE: "Vibe",
  CONTEXT: "Context",
  SOCIAL: "Social",
  COMMITMENT: "Commitment",
  SUBJECT: "Subject"
} as const;

export type TagType = typeof TAG_TYPES[keyof typeof TAG_TYPES];

// Base Tag
export interface TagBase {
  title: string;
  type?: TagType | string;
  description?: string;
}

// User Tag Create
export interface UserTagCreate extends TagBase { }

// Public Tag Create
export interface PublicTagCreate extends TagBase {
  is_public: boolean;
}

// Tag Update
export interface TagUpdate {
  title?: string;
  type?: TagType | string;
  description?: string;
}

// Tag Response
export interface TagResponse extends TagBase, Timestamps {
  id: number;
  account_id?: number;
  is_public: boolean;
}

// Tag Filter Params
export interface TagFilterParams {
  type?: TagType | string;
  is_public?: boolean;
  search?: string;
  created_by_me?: boolean;
  skip?: number;
  limit?: number;
}



export const TAG_TYPE_COLORS: Record<TagType, { bg: string; text: string }> = {
  [TAG_TYPES.MOOD]: { bg: 'rgba(212, 185, 140, 0.15)', text: '#D4B98C' },
  [TAG_TYPES.ENERGY]: { bg: 'rgba(139, 168, 136, 0.15)', text: '#8BA888' },
  [TAG_TYPES.VIBE]: { bg: 'rgba(146, 146, 206, 0.15)', text: '#9292CE' },
  [TAG_TYPES.CONTEXT]: { bg: 'rgba(223, 160, 136, 0.15)', text: '#DFA088' },
  [TAG_TYPES.SOCIAL]: { bg: 'rgba(191, 107, 107, 0.15)', text: '#BF6B6B' },
  [TAG_TYPES.COMMITMENT]: { bg: 'rgba(126, 156, 186, 0.15)', text: '#7E9CBA' },
  [TAG_TYPES.SUBJECT]: { bg: 'rgba(170, 142, 166, 0.15)', text: '#AA8EA6' },
};

// Common tag suggestions for quick selection
export const COMMON_TAGS: Record<string, string[]> = {
  [TAG_TYPES.MOOD]: ['Calm', 'Cozy', 'Light', 'Reflective', 'Melancholic', 'Joyful', 'Playful', 'Cathartic', 'Nostalgic', 'Meaningful'],
  [TAG_TYPES.ENERGY]: ['Very Low', 'Low', 'Medium', 'High', 'Very High'],
  [TAG_TYPES.VIBE]: ['Slow', 'Warm', 'Chill', 'Minimal', 'Intimate', 'Dark', 'Absurd', 'Epic'],
  [TAG_TYPES.CONTEXT]: ['Late Night', 'After Work', 'Weekend', 'Rainy Day', 'Short Break', 'Long Session', 'Background', 'Focused'],
  [TAG_TYPES.SOCIAL]: ['Alone', 'With Friends', 'With Partner', 'Family Friendly', 'Crowd', 'Passive Together'],
  [TAG_TYPES.COMMITMENT]: ['Zero Commitment', 'Low Commitment', 'Medium Commitment', 'High Commitment', 'One-shot', 'Ongoing'],
  [TAG_TYPES.SUBJECT]: ['Film', 'Series', 'Book', 'Music', 'Podcast', 'Game', 'Documentary', 'Art', 'Learning-for-fun', 'Random'],
};