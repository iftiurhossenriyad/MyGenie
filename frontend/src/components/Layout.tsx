import { useState, type ReactNode } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useWorkspace } from '../context/WorkspaceContext';
import type { Workspace } from '../types';

interface LayoutProps {
  children: ReactNode;
  title?: string;
}

export default function Layout({ children, title }: LayoutProps) {
  const { user, logout } = useAuth();
  const {
    currentWorkspace,
    personalWorkspace,
    businessWorkspaces,
    setCurrentWorkspace,
  } = useWorkspace();
  const location = useLocation();
  const navigate = useNavigate();
  const [showSwitcher, setShowSwitcher] = useState(false);

  // Business mode based on URL OR current workspace type
  const isBusinessMode = location.pathname.startsWith('/business');

  const personalNavItems = [
    { path: '/dashboard', label: 'Dashboard', labelBn: 'ড্যাশবোর্ড' },
    { path: '/tasks', label: 'Tasks', labelBn: 'টাস্ক' },
    { path: '/notes', label: 'Notes', labelBn: 'নোট' },
    { path: '/appointments', label: 'Appointments', labelBn: 'অ্যাপয়েন্টমেন্ট' },
    { path: '/chat', label: 'AI Chat', labelBn: 'AI চ্যাট' },
  ];

  const businessNavItems = [
    { path: '/business', label: 'Dashboard', labelBn: 'ড্যাশবোর্ড' },
    { path: '/business/profile', label: 'Profile', labelBn: 'প্রোফাইল' },
    { path: '/business/products', label: 'Products', labelBn: 'পণ্য' },
    { path: '/business/orders', label: 'Orders', labelBn: 'অর্ডার' },
    { path: '/business/bookings', label: 'Bookings', labelBn: 'বুকিং' },
    { path: '/business/faqs', label: 'FAQs', labelBn: 'প্রশ্নোত্তর' },
  ];

  const navItems = isBusinessMode ? businessNavItems : personalNavItems;

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleSwitchWorkspace = (workspace: Workspace) => {
    setCurrentWorkspace(workspace);
    setShowSwitcher(false);
    if (workspace.type === 'business') {
      navigate('/business');
    } else {
      navigate('/dashboard');
    }
  };

  return (
    <div className="min-h-screen flex flex-col md:flex-row bg-gray-50">
      {/* Sidebar */}
      <aside className="w-full md:w-64 md:shrink-0 bg-navy text-white flex flex-col">
        {/* Logo */}
        <div className="px-4 py-3 md:p-6 border-b border-navy-light">
          <h1 className="text-xl md:text-2xl font-bold text-gold">MyGenie</h1>
          <p className="hidden sm:block text-xs text-gray-400 mt-1">One Assistant, Endless Possibilities</p>
        </div>

        {/* Mode Switcher */}
        <div className="p-3 md:p-4 border-b border-navy-light relative">
          <button
            onClick={() => setShowSwitcher(!showSwitcher)}
            className="w-full text-left px-3 py-2 rounded-lg bg-navy-light hover:bg-navy-dark transition-colors"
          >
            <div className="text-xs text-gray-400 mb-1">Current Mode</div>
            <div className="flex items-center justify-between">
              <div>
                <div className="font-semibold text-sm">
                  {isBusinessMode && currentWorkspace?.type === 'business'
                    ? currentWorkspace?.name
                    : 'Personal'}
                </div>
                <div className="text-xs text-gray-400">
                  {isBusinessMode ? 'Business Mode' : 'Personal Mode'}
                </div>
              </div>
              <span className="text-gold text-xs">▼</span>
            </div>
          </button>

          {showSwitcher && (
            <div className="absolute left-4 right-4 mt-2 bg-white rounded-lg shadow-lg z-10 overflow-hidden">
              {personalWorkspace && (
                <button
                  onClick={() => handleSwitchWorkspace(personalWorkspace)}
                  className="w-full text-left px-4 py-3 text-navy hover:bg-gray-100 transition-colors border-b border-gray-100"
                >
                  <div className="font-semibold text-sm">Personal Mode</div>
                  <div className="text-xs text-gray-500">Your private workspace</div>
                </button>
              )}

              {businessWorkspaces.length > 0 && (
                <>
                  <div className="px-4 py-2 text-xs text-gray-400 bg-gray-50">
                    Business Workspaces
                  </div>
                  {businessWorkspaces.map((ws) => (
                    <button
                      key={ws.id}
                      onClick={() => handleSwitchWorkspace(ws)}
                      className="w-full text-left px-4 py-3 text-navy hover:bg-gray-100 transition-colors border-b border-gray-100"
                    >
                      <div className="font-semibold text-sm">{ws.name}</div>
                      <div className="text-xs text-gray-500">Business Mode</div>
                    </button>
                  ))}
                </>
              )}

              <Link
                to="/workspaces/new"
                onClick={() => setShowSwitcher(false)}
                className="block w-full text-left px-4 py-3 text-gold hover:bg-gray-50 transition-colors font-semibold text-sm"
              >
                + Create Business Workspace
              </Link>
            </div>
          )}
        </div>

        {/* Navigation */}
        <nav className="flex md:flex-1 md:flex-col gap-2 md:gap-1 p-2 md:p-4 overflow-x-auto">
          {navItems.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`block shrink-0 px-3 py-2 md:px-4 md:py-3 rounded-lg transition-colors ${
                  isActive
                    ? 'bg-gold text-navy font-semibold'
                    : 'text-gray-300 hover:bg-navy-light'
                }`}
              >
                <div className="text-sm md:text-base font-medium whitespace-nowrap">{item.label}</div>
                <div className="hidden md:block text-xs opacity-75 bengali">{item.labelBn}</div>
              </Link>
            );
          })}
        </nav>

        {/* User Section */}
        <div className="flex items-center gap-3 p-3 md:block md:p-4 border-t border-navy-light">
          <div className="min-w-0 flex-1 text-sm text-gray-300 md:mb-2">
            <div className="font-semibold text-white truncate">{user?.name}</div>
            <div className="text-xs truncate">{user?.email}</div>
          </div>
          <button
            onClick={handleLogout}
            className="shrink-0 px-3 py-2 text-sm bg-red-500 hover:bg-red-600 text-white rounded-lg transition-colors md:w-full"
          >
            Sign Out
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="min-w-0 flex-1 flex flex-col">
        <header className="bg-white border-b border-gray-200 px-4 py-3 md:px-8 md:py-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl md:text-2xl font-bold text-navy">
              {title || 'Dashboard'}
            </h2>
            <div className="hidden sm:block text-sm text-gray-500">
              Welcome back, <span className="font-semibold text-navy">{user?.name}</span>
            </div>
          </div>
        </header>

        <div className="min-w-0 flex-1 p-4 md:p-8 overflow-auto">{children}</div>
      </main>
    </div>
  );
}