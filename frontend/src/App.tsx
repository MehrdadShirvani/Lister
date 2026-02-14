import { Navigate, Route, BrowserRouter as Router, Routes } from 'react-router-dom';
import './App.css'
import { AuthPage } from './features/Auth/AuthPage';
import { useAuthStore } from './stores/useAuthStore';
import './styles/global.css';
import { DashboardPage } from './features/dashboard/DashboardPage';
import { NoteEditorPage } from './features/dashboard/tabs/Notes/NoteEditorPage';

const PrivateRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const isAuthenticated = useAuthStore((state) => state.isLoggedIn);
  return isAuthenticated ? <>{children}</> : <Navigate to="/auth" />;
};

function App() {
   return ( <Router>
      <Routes>
        <Route path="/auth" element={<AuthPage />} />
        <Route
          path="/dashboard"
          element={
            <PrivateRoute>
              <DashboardPage />  
            </PrivateRoute>
          }
        />
        <Route
          path="/notes/:id"
          element={
            <PrivateRoute>
              <NoteEditorPage />
            </PrivateRoute>
          }
        />
        <Route path="/" element={<Navigate to="/auth" />} />
      </Routes>
    </Router>
)}

export default App
