import React from 'react';
import { ListGroup, Button } from 'react-bootstrap';

const Sidebar = ({ setPage, onLogout, onNavigate }) => {
  const handleNavigate = (page) => {
    setPage(page);
    if (onNavigate) {
      onNavigate();
    }
  };

  const handleLogout = () => {
    onLogout();
    if (onNavigate) {
      onNavigate();
    }
  };

  return (
    <div className="p-3">
      <h5 className="text-white mb-3">Menu</h5>
      <ListGroup variant="flush" className="mb-3">
        <ListGroup.Item action onClick={() => handleNavigate('dashboard')}>Dashboard</ListGroup.Item>
        <ListGroup.Item action onClick={() => handleNavigate('quiz')}>Quiz</ListGroup.Item>
        <ListGroup.Item action onClick={() => handleNavigate('forum')}>Forum</ListGroup.Item>
      </ListGroup>
      <Button
        variant="outline-light"
        className="w-100"
        onClick={handleLogout}
      >
        Logout
      </Button>
    </div>
  );
};

export default Sidebar;
