import React, { useEffect, useState } from 'react';
import { Card, ProgressBar, Badge } from 'react-bootstrap';
import axios from 'axios';
import './Dashboard.css'; // Optional CSS for animations

const Dashboard = ({ userId }) => {
  const [user, setUser] = useState({});
  const [progress, setProgress] = useState([]);
  const [badges, setBadges] = useState([]);

 useEffect(() => {
  const fetchDashboardData = async () => {
    try {
      const res = await fetch(`http://localhost:5000/dashboard-data/1`);
      const data = await res.json();
      setUser(data.user || {});
      setProgress(data.progress || []);
      setBadges(data.badges || []);
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setUser({});
      setProgress([]);
      setBadges([]);
    }
  };

  fetchDashboardData();
}, []);



  return (
    <div className="dashboard-container p-3">
      <h2>Welcome, {user.username || 'Learner'}!</h2>

      <section className="progress-section mt-4">
        <h4>Your Learning Progress</h4>
        {progress.length > 0 ? (
          progress.map((p, i) => (
            <Card key={i} className="mb-3 shadow-sm">
              <Card.Body>
                <Card.Title>{p.module_name}</Card.Title>
                <Card.Text>Status: <strong>{p.status}</strong></Card.Text>
                <ProgressBar now={p.score} label={`${p.score}%`} animated striped />
                <small>🔥 Streak: {p.streak} days</small>
              </Card.Body>
            </Card>
          ))
        ) : (
          <p>No progress yet. Start a module to see your progress!</p>
        )}
      </section>

      <section className="badges-section mt-4">
        <h4>Your Badges</h4>
        <div className="d-flex flex-wrap">
          {badges.length > 0 ? (
            badges.map((b, i) => (
              <Card key={i} className="p-3 m-2 shadow-sm text-center" style={{ width: '160px' }}>
                <img
                  src={`/static/icons/${b.icon}`}
                  alt={b.name}
                  className="badge-icon mb-2"
                />
                <Badge bg="success" className="mb-2">{b.name} (Lv {b.level})</Badge>
                <Card.Text>{b.description}</Card.Text>
              </Card>
            ))
          ) : (
            <p>No badges earned yet.</p>
          )}
        </div>
      </section>
    </div>
  );
};

export default Dashboard;
