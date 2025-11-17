import React, { useState } from 'react';
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

  const handleLogin = (userData) => {
    setUser(userData);
    setPage('dashboard');
  };

  const handleLogout = () => {
    setUser(null);
    setPage('login');
    setDashboardRefreshKey(0);
  };

  const handleQuizComplete = () => {
    setDashboardRefreshKey((prev) => prev + 1);
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
      {user && <Navbar user={user} />}
      <Container fluid>
        <Row>
          {user && (
            <Col xs={2} className="sidebar-col">
              <Sidebar setPage={setPage} onLogout={handleLogout} />
            </Col>
          )}
          <Col className="main-content">{renderPage()}</Col>
        </Row>
      </Container>
    </div>
  );
}

export default App;
