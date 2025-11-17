import React from 'react';
import { Navbar, Button } from 'react-bootstrap';

const CustomNavbar = ({ user, onToggleSidebar, showToggle }) => (
  <Navbar className="navbar-custom px-3" expand="lg">
    <div className="d-flex align-items-center">
      {showToggle && (
        <Button
          variant="outline-light"
          size="sm"
          className="me-3 sidebar-toggle-btn d-lg-none"
          onClick={onToggleSidebar}
        >
          ☰
        </Button>
      )}
      <Navbar.Brand className="text-light">E-Learning Dashboard</Navbar.Brand>
    </div>
    <Navbar.Text className="text-light ms-auto">
      Welcome, {user.username}
    </Navbar.Text>
  </Navbar>
);

export default CustomNavbar;
