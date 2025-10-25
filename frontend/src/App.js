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


  const handleLogin = (userData) => {
    setUser(userData);
    setPage('dashboard');
  };

  const renderPage = () => {
    if (!user) return <Login onLogin={handleLogin} />;
    switch (page) {
      case 'dashboard': return <Dashboard />;
      case 'quiz': return <Quiz />;
      case 'forum': return <Forum />;
      default: return <Dashboard />;
    }
  };

  return (
    <div className="app-container">
      {user && <Navbar user={user} />}
      <Container fluid>
        <Row>
          {user && <Col xs={2} className="sidebar-col"><Sidebar setPage={setPage} /></Col>}
          <Col>{renderPage()}</Col>
        </Row>
      </Container>
    </div>
  );
}

export default App;
