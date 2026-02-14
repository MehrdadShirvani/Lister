import type { Timestamps } from './base';
import type { ListPreview } from './list';
import type { NotePreview } from './note';
import type { PlanPreview } from './plan';
import type { RoleResponse } from './role';
import type { TaskPreview } from './task';
import type { TimeBlockPreview } from './timeblock';

// Account Status
export interface AccountStatus {
    id: number;
    title: string;
}

// Account Base
export interface AccountBase {
    first_name: string;
    last_name: string;
    email: string;
}

// Account Create
export interface AccountCreate extends AccountBase {
    password: string;
}

// Account Update
export interface AccountUpdate {
    first_name?: string;
    last_name?: string;
    email?: string;
    account_status_id?: number;
    account_role_id?: number;
    password?: string;
}

// Account Response
export interface AccountResponse extends AccountBase, Timestamps {
    id: number;
    account_status_id: number;
    account_role_id: number;
    join_date: string;
    timezones?: string[];
    role_name?: string;
    status_title?: string;

    full_name: string;
}

export interface AccountDetail extends AccountResponse {
    role?: RoleResponse;
    account_status?: AccountStatus;
    lists?: ListPreview[];
    tasks?: TaskPreview[];
    //   notifications?: NotificationPreview[];
    notes?: NotePreview[];
    time_blocks?: TimeBlockPreview[];
    plans?: PlanPreview[];
}