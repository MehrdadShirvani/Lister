import axios, { type AxiosRequestConfig, type AxiosResponse } from 'axios';
import type { UserSignup, AccountResponse, UserLogin, TokenResponse, AccountUpdate, RoleResponse, RoleCreate, RoleUpdate, TimeBlockCreate, TimeBlockResponse, TimeBlockFilterParams, TimeBlockUpdate, TaskCreate, TaskResponse, TaskFilterParams, TaskDetailResponse, TaskUpdate, TaskHierarchyNode, ListCreate, ListResponse, ListFilterParams, ListDetailResponse, ListUpdate, NoteCreate, NoteResponse, NoteFilterParams, NotePreview, NoteUpdate, PlanCreate, PlanResponse, PlanFromSuggestion, PlanFilterParams, PlanUpdate, PlanAction, ListPreview } from '../types';
import type { UserTagCreate, TagResponse, TagUpdate, PublicTagCreate, TagFilterParams } from '../types/tag';
import { useAuthStore } from '../stores/useAuthStore';

// Types imports

axios.defaults.baseURL = import.meta.env.VITE_API_URL

const responseBody = <T>(response: AxiosResponse<T>) => response.data;

const request = {
    get: <T>(url: string, config?: AxiosRequestConfig) =>
        axios.get<T>(url, config).then(responseBody),

    post: <T>(url: string, body: any, config?: AxiosRequestConfig) => {
        if (body instanceof FormData || body instanceof URLSearchParams) {
            return axios.post<T>(url, body, config).then(responseBody);
        }

        // Merge headers for JSON requests
        const jsonConfig: AxiosRequestConfig = {
            headers: {
                'Content-Type': 'application/json',
                ...(config?.headers || {})
            },
            ...config
        };

        return axios.post<T>(url, body, jsonConfig).then(responseBody);
    },

    put: <T>(url: string, body: {}, config?: AxiosRequestConfig) =>
        axios.put<T>(url, body, config).then(responseBody),

    delete: <T>(url: string, config?: AxiosRequestConfig) =>
        axios.delete<T>(url, config).then(responseBody)
};

axios.interceptors.request.use((config) => {
    const access = useAuthStore.getState().access;
    if (access && !config.url?.includes("/auth/login") && !config.url?.includes("/auth/signup")) {
        config.headers.Authorization = `Bearer ${access}`;
    }
    return config;
});

axios.interceptors.response.use(
    (res) => res,
    (error) => {
        if (error.response?.status === 401) {
            useAuthStore.getState().logout(); // TODO: refresh token
        }
        return Promise.reject(error);
    }
);

// ============= AUTH ENDPOINTS =============
const Auth = {
    signup: (data: UserSignup) =>
        request.post<AccountResponse>('/auth/signup', data),

    login: (data: UserLogin) => {
        const formData = new URLSearchParams();
        formData.append('username', data.username);
        formData.append('password', data.password);

        return request.post<TokenResponse>('/auth/login', formData, {
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        });
    },

    getCurrentUser: () =>
        request.get<AccountResponse>('/auth/me'),
};

// ============= ACCOUNT ENDPOINTS =============
const Accounts = {
    // Status endpoints
    // getStatuses: () =>
    //     request.get<AccountStatusResponse[]>('/accounts/statuses'),

    // Account CRUD
    getAll: (params?: { skip?: number; limit?: number }) =>
        request.get<AccountResponse[]>('/accounts/', { params }),

    getById: (id: number) =>
        request.get<AccountResponse>(`/accounts/${id}`),

    update: (id: number, data: AccountUpdate) =>
        request.put<AccountResponse>(`/accounts/${id}`, data),

    // Timezone management
    addTimezone: (id: number, timezone: string) =>
        request.post(`/accounts/${id}/timezones`, { timezone }),

    getTimezones: (id: number) =>
        request.get<string[]>(`/accounts/${id}/timezones`),

    // Roles
    getAvailableRoles: () =>
        request.get<RoleResponse[]>('/accounts/roles/list'),
};

// ============= ROLE ENDPOINTS =============
const Roles = {
    getAll: (params?: { skip?: number; limit?: number }) =>
        request.get<RoleResponse[]>('/roles/', { params }),

    getById: (id: number) =>
        request.get<RoleResponse>(`/roles/${id}`),

    create: (data: RoleCreate) =>
        request.post<RoleResponse>('/roles/', data),

    update: (id: number, data: RoleUpdate) =>
        request.put<RoleResponse>(`/roles/${id}`, data),

    delete: (id: number) =>
        request.delete(`/roles/${id}`),
};

// ============= TAG ENDPOINTS =============
const Tags = {
    // User tags (private)
    createUserTag: (data: UserTagCreate) =>
        request.post<TagResponse>('/tags/user', data),

    updateUserTag: (id: number, data: TagUpdate) =>
        request.put<TagResponse>(`/tags/user/${id}`, data),

    deleteUserTag: (id: number) =>
        request.delete(`/tags/user/${id}`),

    // Public tags (admin)
    createPublicTag: (data: PublicTagCreate) =>
        request.post<TagResponse>('/tags/public', data),

    updatePublicTag: (id: number, data: TagUpdate) =>
        request.put<TagResponse>(`/tags/public/${id}`, data),

    deletePublicTag: (id: number) =>
        request.delete(`/tags/public/${id}`),

    // Listing and filtering
    getAll: (params?: TagFilterParams) =>
        request.get<TagResponse[]>('/tags/', { params }),

    getById: (id: number) =>
        request.get<TagResponse>(`/tags/${id}`),

    getTypes: () =>
        request.get<string[]>('/tags/types'),
};

// ============= TIMEBLOCK ENDPOINTS =============
const TimeBlocks = {
    // CRUD
    create: (data: TimeBlockCreate) =>
        request.post<TimeBlockResponse>('/timeblocks/', data),

    getAll: (params?: TimeBlockFilterParams & { skip?: number; limit?: number }) =>
        request.get<TimeBlockResponse[]>('/timeblocks/', { params }),

    getById: (id: number) =>
        request.get<TimeBlockResponse>(`/timeblocks/${id}`),

    update: (id: number, data: TimeBlockUpdate) =>
        request.put<TimeBlockResponse>(`/timeblocks/${id}`, data),

    delete: (id: number) =>
        request.delete(`/timeblocks/${id}`),

    // Special queries
    getUpcoming: (days?: number) =>
        request.get<TimeBlockResponse[]>('/timeblocks/upcoming', { params: { days } }),

    getEnergyLevels: () =>
        request.get<{ level: string; tag_id: number; description?: string; is_public: boolean }[]>('/timeblocks/energy-levels'),

    // Bulk operations
    createBulk: (data: TimeBlockCreate[]) =>
        request.post<TimeBlockResponse[]>('/timeblocks/bulk', data),
};

// ============= TASK ENDPOINTS =============
const Tasks = {
    // CRUD
    create: (data: TaskCreate) =>
        request.post<TaskResponse>('/tasks/', data),

    getAll: (params?: TaskFilterParams & { skip?: number; limit?: number }) =>
        request.get<TaskResponse[]>('/tasks/', { params }),

    getById: (id: number) =>
        request.get<TaskResponse>(`/tasks/${id}`),

    getDetail: (id: number) =>
        request.get<TaskDetailResponse>(`/tasks/${id}/detail`),

    update: (id: number, data: TaskUpdate) =>
        request.put<TaskResponse>(`/tasks/${id}`, data),

    delete: (id: number) =>
        request.delete(`/tasks/${id}`),

    // Hierarchy
    getHierarchy: (rootTaskId?: number) =>
        request.get<TaskHierarchyNode[]>('/tasks/hierarchy', { params: { root_task_id: rootTaskId } }),

    // Special queries
    getWithFuturePlans: () =>
        request.get<TaskResponse[]>('/tasks/with-future-plans'),

    getByTag: (tagId: number) =>
        request.get<TaskResponse[]>(`/tasks/by-tag/${tagId}`),

    // Operations
    complete: (id: number) =>
        request.post<TaskResponse>(`/tasks/${id}/complete`, {}),

    duplicate: (id: number) =>
        request.post<TaskResponse>(`/tasks/${id}/duplicate`, {}),
};

// ============= LIST ENDPOINTS =============
const Lists = {
    // CRUD
    create: (data: ListCreate) =>
        request.post<ListResponse>('/lists/', data),

    getAll: (params?: ListFilterParams & { skip?: number; limit?: number }) =>
        request.get<ListResponse[]>('/lists/', { params }),

    getById: (id: number) =>
        request.get<ListResponse>(`/lists/${id}`),

    getDetail: (id: number) =>
        request.get<ListDetailResponse>(`/lists/${id}/detail`),

    getHierarchy: (id: number) =>
        request.get<TaskHierarchyNode[]>(`/lists/${id}/hierarchy`),

    update: (id: number, data: ListUpdate) =>
        request.put<ListResponse>(`/lists/${id}`, data),

    delete: (id: number) =>
        request.delete(`/lists/${id}`),

    // Special queries
    getByTag: (tagId: number) =>
        request.get<ListResponse[]>(`/lists/by-tag/${tagId}`),

    // Operations
    archive: (id: number) =>
        request.post<ListResponse>(`/lists/${id}/archive`, {}),

    moveTasks: (sourceListId: number, targetListId: number) =>
        request.post<{ message: string; source_list: string; target_list: string }>(
            '/lists/move-tasks',
            {},
            { params: { source_list_id: sourceListId, target_list_id: targetListId } }
        ),

    // Bulk operations
    createBulk: (data: ListCreate[]) =>
        request.post<ListResponse[]>('/lists/bulk', data),
};

// ============= NOTE ENDPOINTS =============
const Notes = {
    // CRUD
    create: (data: NoteCreate) =>
        request.post<NoteResponse>('/notes/', data),

    getAll: (params?: NoteFilterParams & { skip?: number; limit?: number }) =>
        request.get<NotePreview[]>('/notes/', { params }),

    search: (query: string, limit?: number) =>
        request.get<NotePreview[]>('/notes/search', { params: { q: query, limit } }),

    getById: (id: number) =>
        request.get<NoteResponse>(`/notes/${id}`),

    update: (id: number, data: NoteUpdate) =>
        request.put<NoteResponse>(`/notes/${id}`, data),

    delete: (id: number) =>
        request.delete(`/notes/${id}`),

    // Special queries
    getByTag: (tagId: number) =>
        request.get<NotePreview[]>(`/notes/by-tag/${tagId}`),

    getByTask: (taskId: number) =>
        request.get<NoteResponse[]>(`/notes/by-task/${taskId}`),

    // Operations
    togglePin: (id: number) =>
        request.post<NoteResponse>(`/notes/${id}/pin`, {}),

    toggleFavorite: (id: number) =>
        request.post<NoteResponse>(`/notes/${id}/favorite`, {}),

    archive: (id: number) =>
        request.post<NoteResponse>(`/notes/${id}/archive`, {}),

    restore: (id: number) =>
        request.post<NoteResponse>(`/notes/${id}/restore`, {}),

    duplicate: (id: number) =>
        request.post<NoteResponse>(`/notes/${id}/duplicate`, {}),

    // Plan follow-up
    createFromPlan: (planId: number) =>
        request.post<NoteResponse>(`/notes/from-plan/${planId}`, {}),

    // Bulk operations
    createBulk: (data: NoteCreate[]) =>
        request.post<NoteResponse[]>('/notes/bulk', data),
};

// ============= SUGGESTION ENDPOINTS =============
const Suggestions = {
    // User endpoints
    // getAll: (params?: SuggestionFilterParams & { skip?: number; limit?: number }) =>
    //     request.get<SuggestionResponseSchema[]>('/suggestions/', { params }),

    // getPendingCount: () =>
    //     request.get<{ count: number }>('/suggestions/pending/count'),

    // getById: (taskId: number, timeBlockId: number, title: string) =>
    //     request.get<SuggestionResponseSchema>(`/suggestions/${taskId}/${timeBlockId}/${encodeURIComponent(title)}`),

    // respond: (taskId: number, timeBlockId: number, title: string, response: SuggestionResponseType) =>
    //     request.post(`/suggestions/${taskId}/${timeBlockId}/${encodeURIComponent(title)}/respond`, response),

    // accept: (taskId: number, timeBlockId: number, title: string, notes?: string) =>
    //     request.post<{ action: string; plan?: { id: number; status: string } }>(
    //         `/suggestions/${taskId}/${timeBlockId}/${encodeURIComponent(title)}/accept`,
    //         { notes }
    //     ),

    // reject: (taskId: number, timeBlockId: number, title: string, notes?: string) =>
    //     request.post(`/suggestions/${taskId}/${timeBlockId}/${encodeURIComponent(title)}/reject`, { notes }),

    // dismiss: (taskId: number, timeBlockId: number, title: string) =>
    //     request.post(`/suggestions/${taskId}/${timeBlockId}/${encodeURIComponent(title)}/dismiss`, {}),

    // // System endpoints (for suggestion algorithm)
    // generate: (suggestions: SuggestionCreate[]) =>
    //     request.post<SuggestionResponseSchema[]>('/suggestions/generate', suggestions),

    // cleanup: () =>
    //     request.post<{ message: string }>('/suggestions/cleanup', {}),
};

// ============= PLAN ENDPOINTS =============
const Plans = {
    // CRUD
    create: (data: PlanCreate) =>
        request.post<PlanResponse>('/plans/', data),

    createFromSuggestion: (data: PlanFromSuggestion) =>
        request.post<PlanResponse>('/plans/from-suggestion', data),

    getAll: (params?: PlanFilterParams & { skip?: number; limit?: number }) =>
        request.get<PlanResponse[]>('/plans/', { params }),

    getToday: () =>
        request.get<PlanResponse[]>('/plans/today'),

    getUpcoming: (days?: number) =>
        request.get<PlanResponse[]>('/plans/upcoming', { params: { days } }),

    getById: (id: number) =>
        request.get<PlanResponse>(`/plans/${id}`),

    update: (id: number, data: PlanUpdate) =>
        request.put<PlanResponse>(`/plans/${id}`, data),

    delete: (id: number) =>
        request.delete(`/plans/${id}`),

    // Actions
    action: (id: number, action: PlanAction) =>
        request.post<PlanResponse>(`/plans/${id}/action`, action),

    start: (id: number, notes?: string) =>
        request.post<PlanResponse>(`/plans/${id}/start`, { notes }),

    complete: (id: number, notes?: string) =>
        request.post<PlanResponse>(`/plans/${id}/complete`, { notes }),

    cancel: (id: number, notes?: string) =>
        request.post<PlanResponse>(`/plans/${id}/cancel`, { notes }),
};

// ============= DASHBOARD / AGGREGATE ENDPOINTS =============
const Dashboard = {
    getOverview: () =>
        request.get<{
            tasks: {
                total: number;
                completed: number;
                pending: number;
                overdue: number;
            };
            plans: {
                today: number;
                upcoming: number;
            };
            suggestions: {
                pending: number;
            };
            notes: {
                recent: NotePreview[];
                pinned: NotePreview[];
            };
            lists: ListPreview[];
        }>('/dashboard/overview'),

    getSchedule: (date?: string) =>
        request.get<{
            timeblocks: TimeBlockResponse[];
            plans: PlanResponse[];
        }>('/dashboard/schedule', { params: { date } }),
};

// ============= EXPORT ALL API ENDPOINTS =============
const api = {
    Auth,
    Accounts,
    Roles,
    Tags,
    TimeBlocks,
    Tasks,
    Lists,
    Notes,
    Suggestions,
    Plans,
    Dashboard,
};

export default api;

// Also export individual modules for selective imports
export {
    Auth,
    Accounts,
    Roles,
    Tags,
    TimeBlocks,
    Tasks,
    Lists,
    Notes,
    Suggestions,
    Plans,
    Dashboard,
};