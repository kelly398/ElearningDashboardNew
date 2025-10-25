import React, { useEffect, useState } from 'react';
import { Card, ProgressBar, Badge } from 'react-bootstrap';
import './Dashboard.css';

const Dashboard = ({ userId }) => {
  const [user, setUser] = useState({ username: 'JohnDoe22' });
  const [progress, setProgress] = useState([]);
  const [badges, setBadges] = useState([]);

  // HARDCODED DATA TO MATCH YOUR SCREENSHOT
  useEffect(() => {
    const demoProgress = [
      {
        module_name: "Python Basics",
        status: "Completed",
        score: 90,
        streak: 3
      },
      {
        module_name: "React Fundamentals",
        status: "In Progress",
        score: 65,
        streak: 2
      },
      {
        module_name: "Flask APIs",
        status: "Not Started",
        score: 0,
        streak: 0
      }
    ];

    const demoBadges = [
      {
        name: "Python Pro",
        description: "Completed Python Basics",
        icon: "python.png",
        level: 1
      },
      {
        name: "React Rookie",
        description: "Started React Fundamentals",
        icon: "react.png",
        level: 1
      },
      {
        name: "Consistent Learner",
        description: "Logged in 7 days in a row",
        icon: "streak.png",
        level: 1
      }
    ];

    setProgress(demoProgress);
    setBadges(demoBadges);
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
                <ProgressBar 
                  now={p.score} 
                  label={`${p.score}%`} 
                  animated 
                  striped 
                  variant={
                    p.score >= 80 ? "success" : 
                    p.score >= 50 ? "warning" : 
                    p.score > 0 ? "danger" : "secondary"
                  }
                />
                <small>Streak: {p.streak} days</small>
              </Card.Body>
            </Card>
          ))
        ) : (
          <p>No progress yet. Start a module to see your progress!</p>
        )}
      </section>

      <section className="badges-section mt-4">
        <h4>Your Badges</h4>
        <div className="d-flex flex-wrap gap-3">
          {badges.length > 0 ? (
            badges.map((b, i) => (
              <Card key={i} className="p-3 text-center shadow-sm" style={{ width: '180px' }}>
                <div 
                  className="badge-icon mx-auto mb-2 rounded-circle d-flex align-items-center justify-content-center"
                  style={{ width: 50, height: 50, backgroundColor: '#e9ecef' }}
                >
                  <span style={{ fontSize: '1.5rem' }}>
                    {b.name === "Python Pro" ? "Python" : 
                     b.name === "React Rookie" ? "React" : 
                     "Fire"}
                  </span>
                </div>
                <Badge bg="success" className="mb-1">{b.name} (Lv {b.level})</Badge>
                <Card.Text className="small">{b.description}</Card.Text>
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