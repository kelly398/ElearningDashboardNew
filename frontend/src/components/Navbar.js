import React from 'react';
import { Navbar } from 'react-bootstrap';

const CustomNavbar = ({ user }) => (
  <Navbar className="navbar-custom px-3" expand="lg">
    <Navbar.Brand className="text-light">E-Learning Dashboard</Navbar.Brand>
    <Navbar.Text className="text-light ms-auto">
      Welcome, {user.username}
    </Navbar.Text>
  </Navbar>
);

export default CustomNavbar;
