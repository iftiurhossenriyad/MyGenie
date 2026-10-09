/* eslint-disable react-refresh/only-export-components */
import {
  createContext,
  useContext,
  useState,
  useEffect,
  type ReactNode,
} from 'react';
import { workspacesApi } from '../lib/workspaces';
import { useAuth } from './AuthContext';
import type { Workspace } from '../types';

interface WorkspaceContextType {
  workspaces: Workspace[];
  currentWorkspace: Workspace | null;
  personalWorkspace: Workspace | null;
  businessWorkspaces: Workspace[];
  loading: boolean;
  setCurrentWorkspace: (workspace: Workspace) => void;
  refreshWorkspaces: () => Promise<void>;
}

const WorkspaceContext = createContext<WorkspaceContextType | undefined>(undefined);

export function WorkspaceProvider({ children }: { children: ReactNode }) {
  const { user } = useAuth();
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [currentWorkspace, setCurrentWorkspaceState] = useState<Workspace | null>(null);
  const [loading, setLoading] = useState(true);

  const personalWorkspace = workspaces.find((w) => w.type === 'personal') || null;
  const businessWorkspaces = workspaces.filter((w) => w.type === 'business');

  const refreshWorkspaces = async () => {
    if (!user) {
      setWorkspaces([]);
      setCurrentWorkspaceState(null);
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      const data = await workspacesApi.list();
      setWorkspaces(data);

      // Restore last selected workspace from localStorage
      const storedId = localStorage.getItem('mygenie_current_workspace_id');
      const stored = storedId
        ? data.find((w) => w.id === parseInt(storedId))
        : null;

      if (stored) {
        setCurrentWorkspaceState(stored);
      } else {
        // Default to personal workspace
        const personal = data.find((w) => w.type === 'personal');
        if (personal) {
          setCurrentWorkspaceState(personal);
          localStorage.setItem(
            'mygenie_current_workspace_id',
            personal.id.toString()
          );
        }
      }
    } catch (err) {
      console.error('Failed to load workspaces', err);
    } finally {
      setLoading(false);
    }
  };

  const setCurrentWorkspace = (workspace: Workspace) => {
    setCurrentWorkspaceState(workspace);
    localStorage.setItem(
      'mygenie_current_workspace_id',
      workspace.id.toString()
    );
  };

  useEffect(() => {
    let cancelled = false;

    const loadWorkspaces = async () => {
      if (!user) {
        if (cancelled) return;
        setWorkspaces([]);
        setCurrentWorkspaceState(null);
        setLoading(false);
        return;
      }

      try {
        const data = await workspacesApi.list();
        if (cancelled) return;
        setWorkspaces(data);

        const storedId = localStorage.getItem('mygenie_current_workspace_id');
        const stored = storedId ? data.find((w) => w.id === parseInt(storedId)) : null;

        if (stored) {
          setCurrentWorkspaceState(stored);
        } else {
          const personal = data.find((w) => w.type === 'personal');
          if (personal) {
            setCurrentWorkspaceState(personal);
            localStorage.setItem('mygenie_current_workspace_id', personal.id.toString());
          }
        }
      } catch (err) {
        console.error('Failed to load workspaces', err);
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    void loadWorkspaces();

    return () => {
      cancelled = true;
    };
  }, [user]);

  return (
    <WorkspaceContext.Provider
      value={{
        workspaces,
        currentWorkspace,
        personalWorkspace,
        businessWorkspaces,
        loading,
        setCurrentWorkspace,
        refreshWorkspaces,
      }}
    >
      {children}
    </WorkspaceContext.Provider>
  );
}

export function useWorkspace() {
  const context = useContext(WorkspaceContext);
  if (!context) {
    throw new Error('useWorkspace must be used within WorkspaceProvider');
  }
  return context;
}