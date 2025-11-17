import React, { useEffect, useState } from 'react';
import { Card, ProgressBar, Badge as BsBadge, Spinner, Alert } from 'react-bootstrap';
import './Dashboard.css';

const API_BASE = 'http://localhost:5000';

const Dashboard = ({ user, refreshKey = 0 }) => {
  const [progress, setProgress] = useState([]);
  const [badges, setBadges] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!user?.id) return;
    const fetchDashboard = async () => {
      setLoading(true);
      setError('');
      try {
        const res = await fetch(`${API_BASE}/dashboard/${user.id}`);
        const data = await res.json();
        if (res.ok) {
          setProgress(data.progress || []);
          setBadges(data.badges || []);
        } else {
          setError(data.message || 'Unable to load dashboard data.');
        }
      } catch (err) {
        setError('Unable to load dashboard data.');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboard();
  }, [user?.id, refreshKey]);

  const renderProgress = () => {
    if (loading) {
      return (
        <div className="text-center py-4">
          <Spinner animation="border" role="status" />
        </div>
      );
    }

    if (!progress.length) {
      return <p className="text-muted mt-3">No progress yet. Complete a quiz to get started!</p>;
    }

    return progress.map((p, i) => {
      const percent = typeof p.percent_complete === 'number' ? p.percent_complete : Math.min(100, p.score || 0);
      return (
        <Card key={i} className="mb-3 shadow-sm">
          <Card.Body>
            <Card.Title>{p.module_name}</Card.Title>
            <Card.Text>Status: <strong>{p.status}</strong></Card.Text>
            <div className="position-relative">
              <ProgressBar
                now={percent}
                label={`${percent}%`}
                animated={percent > 0 && percent < 100}
                striped
                variant={
                  percent === 100 ? 'success' :
                  percent >= 70 ? 'info' :
                  percent >= 50 ? 'warning' :
                  percent > 0 ? 'danger' : 'secondary'
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
            <small className="text-muted d-block mt-2">
              Score: {p.score || 0} | Streak: {p.streak || 0} days
            </small>
          </Card.Body>
        </Card>
      );
    });
  };

  const renderBadges = () => {
    if (!badges.length) {
      return <p className="text-muted">No badges yet. Keep learning to earn some!</p>;
    }

    return badges.map((b) => (
      <Card key={b.id} className="p-3 text-center shadow-sm" style={{ width: '180px' }}>
        <div
          className="badge-icon mx-auto mb-2 rounded-circle d-flex align-items-center justify-content-center"
          style={{ width: 50, height: 50, backgroundColor: '#e9ecef' }}
        >
          <span style={{ fontSize: '1.2rem' }}>
            {b.name?.[0] || '?'}
          </span>
        </div>
        <BsBadge bg="success" className="mb-1">{b.name} (Lv {b.level || 1})</BsBadge>
        <Card.Text className="small">{b.description}</Card.Text>
      </Card>
    ));
  };

  return (
    <div className="dashboard-container p-3">
      <h2>Hello, {user?.username || 'Learner'}!</h2>
      {error && <Alert variant="danger" className="mt-3">{error}</Alert>}

      <section className="progress-section mt-4">
        <h4>Your Learning Progress</h4>
        {renderProgress()}
      </section>

      <section className="badges-section mt-4">
        <h4>Your Badges</h4>
        <div className="d-flex flex-wrap gap-3">
          {renderBadges()}
        </div>
      </section>
    </div>
  );
};

export default Dashboard;
