import React from 'react';
import { ListGroup, Button } from 'react-bootstrap';

const Sidebar = ({ setPage, onLogout }) => (
  <div className="p-3">
    <h5 className="text-white mb-3">Menu</h5>
    <ListGroup variant="flush" className="mb-3">
      <ListGroup.Item action onClick={() => setPage('dashboard')}>Dashboard</ListGroup.Item>
      <ListGroup.Item action onClick={() => setPage('quiz')}>Quiz</ListGroup.Item>
      <ListGroup.Item action onClick={() => setPage('forum')}>Forum</ListGroup.Item>
    </ListGroup>
    <Button
      variant="outline-light"
      className="w-100"
      onClick={onLogout}
    >
      Logout
    </Button>
  </div>
);

export default Sidebar;
