// Base timestamp interface
export interface Timestamps {
    created_at: string; // ISO datetime
    updated_at?: string; // ISO datetime
}

// Generic response wrapper
export interface ApiResponse<T> {
    data: T;
    message?: string;
    status: number;
}

// Pagination params
export interface PaginationParams {
    skip?: number;
    limit?: number;
}

// Paginated response
export interface PaginatedResponse<T> {
    items: T[];
    total: number;
    skip: number;
    limit: number;
}