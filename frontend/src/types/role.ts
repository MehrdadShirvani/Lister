import type { Timestamps } from './base';

// Role Base
export interface RoleBase {
    name: string;
    description?: string;
    level: number;
}

// Role Create
export interface RoleCreate extends RoleBase { }

// Role Update
export interface RoleUpdate {
    name?: string;
    description?: string;
    level?: number;
}

// Role Response
export interface RoleResponse extends RoleBase, Timestamps {
    id: number;
}