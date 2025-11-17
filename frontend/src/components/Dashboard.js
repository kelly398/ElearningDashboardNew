import React, { useEffect, useState } from 'react';
import { Card, ProgressBar, Badge } from 'react-bootstrap';
import './Dashboard.css';

const Dashboard = ({ userId }) => {
  const [user] = useState({ username: 'Learner' });
  const [progress, setProgress] = useState([]);
  const [badges, setBadges] = useState([]);

  // HARDCODED DATA — MATCHING YOUR MASTER'S & SCREENSHOT
  useEffect(() => {
    const demoProgress = [
      {
        module_name: "Cloud Computing",
        status: "Completed",
        score: 100,  // 100% = Completed
        streak: 3
      },
      {
        module_name: "Web Design with JavaScript",
        status: "In Progress",
        score: 65,
        streak: 2
      },
      {
        module_name: "Data Structures",
        status: "Not Started",
        score: 0,
        streak: 0
      }
    ];

    const demoBadges = [
      {
        name: "Cloud Pro",
        description: "Completed Cloud Computing",
        icon: "cloud.png",
        level: 1
      },
      {
        name: "Web Design Rookie",
        description: "Started Web Design with JavaScript",
        icon: "js.png",
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
      <h2>Hello, {user.username}!</h2>

      <section className="progress-section mt-4">
        <h4>Your Learning Progress</h4>
        {progress.map((p, i) => (
          <Card key={i} className="mb-3 shadow-sm">
            <Card.Body>
              <Card.Title>{p.module_name}</Card.Title>
              <Card.Text>Status: <strong>{p.status}</strong></Card.Text>

              {/* VISIBLE, BOLD, CENTERED LABEL */}
              <div className="position-relative">
                <ProgressBar 
                  now={p.score} 
                  label={`${p.score}%`}
                  animated={p.score > 0 && p.score < 100}
                  striped
                  variant={
                    p.score === 100 ? "success" :
                    p.score >= 70 ? "info" :
                    p.score >= 50 ? "warning" :
                    p.score > 0 ? "danger" : "secondary"
                  }
                  style={{ 
                    height: '40px', 
                    fontSize: '1.1rem', 
                    fontWeight: 'bold',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}
                  className="text-dark"
                />
              </div>

              <small className="text-muted">Streak: {p.streak} days</small>
            </Card.Body>
          </Card>
        ))}
      </section>

      <section className="badges-section mt-4">
        <h4>Your Badges</h4>
        <div className="d-flex flex-wrap gap-3">
          {badges.map((b, i) => (
            <Card key={i} className="p-3 text-center shadow-sm" style={{ width: '180px' }}>
              <div 
                className="badge-icon mx-auto mb-2 rounded-circle d-flex align-items-center justify-content-center"
                style={{ width: 50, height: 50, backgroundColor: '#e9ecef' }}
              >
                <span style={{ fontSize: '1.5rem' }}>
                  {b.name === "Cloud Pro" ? "Cloud" : 
                   b.name === "Web Design Rookie" ? "JS" : 
                   "Fire"}
                </span>
              </div>
              <Badge bg="success" className="mb-1">{b.name} (Lv {b.level})</Badge>
              <Card.Text className="small">{b.description}</Card.Text>
            </Card>
          ))}
        </div>
      </section>
    </div>
  );
};

export default Dashboard;