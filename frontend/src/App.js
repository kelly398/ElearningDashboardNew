import React, { useEffect, useState } from 'react';
import { Container, Row, Col } from 'react-bootstrap';
import Sidebar from './components/Sidebar';
import Navbar from './components/Navbar';
import Dashboard from './components/Dashboard';
import Quiz from './components/Quiz';
import Forum from './components/Forum';
import Login from './components/Login';
import './App.css';

function App() {
  const [page, setPage] = useState('login');
  const [user, setUser] = useState(null);
  const [dashboardRefreshKey, setDashboardRefreshKey] = useState(0);
  const [isMobile, setIsMobile] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const handleLogin = (userData) => {
    setUser(userData);
    setPage('dashboard');
  };

  const handleLogout = () => {
    setUser(null);
    setPage('login');
    setDashboardRefreshKey(0);
    setSidebarOpen(false);
  };

  const handleQuizComplete = () => {
    setDashboardRefreshKey((prev) => prev + 1);
  };

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 992);
    };
    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  useEffect(() => {
    if (!user) {
      setSidebarOpen(false);
      return;
    }
    setSidebarOpen(!isMobile);
  }, [isMobile, user]);

  const handleToggleSidebar = () => {
    setSidebarOpen((prev) => !prev);
  };

  const handleCloseSidebar = () => {
    if (isMobile) {
      setSidebarOpen(false);
    }
  };

  const handleNavigate = () => {
    if (isMobile) {
      setSidebarOpen(false);
    }
  };

  const renderPage = () => {
    if (!user) return <Login onLogin={handleLogin} />;
    switch (page) {
      case 'dashboard':
        return <Dashboard user={user} refreshKey={dashboardRefreshKey} />;
      case 'quiz':
        return <Quiz user={user} onQuizComplete={handleQuizComplete} />;
      case 'forum':
        return <Forum user={user} />;
      default:
        return <Dashboard user={user} refreshKey={dashboardRefreshKey} />;
    }
  };

  return (
    <div className="app-container">
      {user && (
        <Navbar
          user={user}
          onToggleSidebar={handleToggleSidebar}
          showToggle={isMobile}
        />
      )}
      <Container fluid>
        <Row>
          {user && (
            <Col
              xs={12}
              md={3}
              lg={2}
              className={`sidebar-col ${isMobile ? 'mobile' : ''} ${sidebarOpen ? 'open' : ''}`}
            >
              <Sidebar setPage={setPage} onLogout={handleLogout} onNavigate={handleNavigate} />
            </Col>
          )}
          <Col className={`main-content ${isMobile ? 'mobile-content' : ''}`}>
            {renderPage()}
          </Col>
        </Row>
      </Container>
      {isMobile && sidebarOpen && <div className="sidebar-overlay" onClick={handleCloseSidebar} />}
    </div>
  );
}

export default App;
