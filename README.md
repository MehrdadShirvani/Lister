# Lister

A reflective, intelligent life companion app for storing and surfacing meaningful experiences at the right moment.

## Overview

Life Curator is not a productivity task manager. It's a calm, warm space for the small meaningful things you want to experience someday. The app suggests them when the time is right, helps you actually experience them, and encourages reflection afterward.

## Core Features

- **Tasks** - Meaningful experiences you want to have (not chores)
- **Lists** - Thematic containers for organizing tasks
- **Tags** - Typed tagging system (Mood, Energy, Vibe, Context, Social, Commitment, Subject)
- **Time Blocks** - Define when you're free for suggestions
- **Suggestion Engine** - suggests tasks based on time, energy, and preferences
- **Plans** - Accepted suggestions scheduled for completion
- **Notes** - Rich text notes with reflection support

## Tech Stack

- **Frontend**: React 18 with TypeScript
- **State Management**: Zustand
- **Routing**: React Router v6
- **Styling**: CSS Modules
- **Rich Text Editor**: TipTap
- **Date Handling**: date-fns
- **HTTP Client**: Axios

## Project Structure

```
src/
├── components/
│   ├── auth/           # Authentication components
│   ├── dashboard/      # Dashboard layout and navigation
│   ├── library/        # Lists and tasks management
│   ├── notes/          # Notes grid and cards
│   └── tags/           # Tag selector and management
├── pages/
│   ├── AuthPage.tsx    # Login/signup page
│   ├── DashboardPage.tsx # Main dashboard with tabs
│   └── NoteEditorPage.tsx # Note creation/editing
├── services/
│   └── api.ts          # API client with interceptors
├── stores/
│   ├── authStore.ts    # Authentication state
│   └── ...             # Other stores
├── styles/
│   └── global.css      # Global styles and variables
└── types/              # TypeScript type definitions
```

## Key Design Decisions

### Responsive Design
- Mobile-first approach
- Bottom navigation on mobile, top tabs on desktop
- Adaptive grids and layouts
- Touch-friendly tap targets

### Tag System
Tags are typed and color-coded:
- Mood: Calm, Cozy, Reflective, etc.
- Energy: Very Low to Very High
- Vibe: Slow, Warm, Chill, etc.
- Context: Late Night, Weekend, etc.
- Social: Alone, With Friends, etc.
- Commitment: Zero to High
- Subject: Film, Book, Music, etc.

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   npm install
   ```
3. Create a `.env` file with your API URL:
   ```
   REACT_APP_API_URL=http://localhost:3000/api
   ```
4. Start the development server:
   ```bash
   npm start
   ```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `REACT_APP_API_URL` | Backend API URL | `http://localhost:3000/api` |

## Available Scripts

- `npm start` - Start development server
- `npm build` - Build for production
- `npm test` - Run tests
- `npm eject` - Eject from Create React App

## API Integration

The app expects a REST API with the following endpoints:

### Auth
- `POST /auth/signup` - Create account
- `POST /auth/login` - Get access token
- `GET /auth/me` - Get current user

### Tasks
- `GET /tasks` - List tasks
- `POST /tasks` - Create task
- `GET /tasks/:id` - Get task
- `PUT /tasks/:id` - Update task
- `DELETE /tasks/:id` - Delete task
- `POST /tasks/:id/complete` - Mark complete

### Lists
- `GET /lists` - List lists
- `POST /lists` - Create list
- `GET /lists/:id` - Get list
- `GET /lists/:id/detail` - Get list with tasks
- `PUT /lists/:id` - Update list
- `DELETE /lists/:id` - Delete list

### Tags
- `GET /tags` - List tags
- `POST /tags/user` - Create user tag
- `PUT /tags/user/:id` - Update user tag
- `DELETE /tags/user/:id` - Delete user tag

### Notes
- `GET /notes` - List notes
- `POST /notes` - Create note
- `GET /notes/:id` - Get note
- `PUT /notes/:id` - Update note
- `DELETE /notes/:id` - Delete note
- `POST /notes/:id/pin` - Toggle pin
- `POST /notes/:id/favorite` - Toggle favorite

## Contributing

1. Follow the existing code style and patterns
2. Maintain the calm, warm tone in UI and copy
3. Ensure responsive design works on all screen sizes
4. Test on both desktop and mobile