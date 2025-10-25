import React from 'react';
import { ListGroup } from 'react-bootstrap';

const Sidebar = ({ setPage }) => (
  <div className="p-3">
    <h5 className="text-white mb-3">Menu</h5>
    <ListGroup variant="flush">
      <ListGroup.Item action onClick={() => setPage('dashboard')}>Dashboard</ListGroup.Item>
      <ListGroup.Item action onClick={() => setPage('quiz')}>Quiz</ListGroup.Item>
      <ListGroup.Item action onClick={() => setPage('forum')}>Forum</ListGroup.Item>
    </ListGroup>
  </div>
);

export default Sidebar;
