import React, { useEffect, useState } from 'react';
import { Card, Spinner, Alert, Form, Row, Col } from 'react-bootstrap';

const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:5000';

const Modules = () => {
  const [modules, setModules] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [filter, setFilter] = useState('');

  useEffect(() => {
    const fetchModules = async () => {
      setLoading(true);
      setError('');
      try {
        const res = await fetch(`${API_BASE}/modules`);
        const data = await res.json();
        if (res.ok) {
          setModules(data.modules || []);
        } else {
          setError(data.message || 'Unable to load modules.');
        }
      } catch (err) {
        setError('Unable to load modules.');
      } finally {
        setLoading(false);
      }
    };

    fetchModules();
  }, []);

  const filteredModules = modules.filter((module) => {
    if (!filter.trim()) return true;
    const term = filter.toLowerCase();
    return (
      module.title.toLowerCase().includes(term) ||
      module.category.toLowerCase().includes(term)
    );
  });

  return (
    <div className="p-3">
      <div className="d-flex flex-column flex-md-row align-items-md-center justify-content-between mb-3">
        <div>
          <h4 className="mb-1">Learning Modules</h4>
          <p className="text-muted mb-0">Browse curated topics and skills.</p>
        </div>
        <Form.Control
          type="text"
          placeholder="Search by title or category..."
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="mt-2 mt-md-0"
          style={{ maxWidth: 320 }}
        />
      </div>

      {loading && (
        <div className="text-center py-5">
          <Spinner animation="border" role="status" />
        </div>
      )}

      {error && <Alert variant="danger">{error}</Alert>}

      {!loading && !error && (
        <Row xs={1} md={2} lg={3} className="g-3">
          {filteredModules.map((module) => (
            <Col key={module.id}>
              <Card className="shadow-sm h-100 module-card">
                <Card.Body>
                  <div className="d-flex justify-content-between align-items-center mb-2">
                    <Card.Title className="mb-0">{module.title}</Card.Title>
                    <span className="badge bg-secondary">{module.category}</span>
                  </div>
                  <Card.Text className="text-muted">{module.description}</Card.Text>
                </Card.Body>
                <Card.Footer className="d-flex justify-content-between text-muted">
                  <small>Duration: {module.duration || 0} min</small>
                  <small>Order: {module.order}</small>
                </Card.Footer>
              </Card>
            </Col>
          ))}
          {!filteredModules.length && (
            <Col>
              <Card className="p-4 text-center">
                <Card.Text className="text-muted mb-0">
                  No modules match that query.
                </Card.Text>
              </Card>
            </Col>
          )}
        </Row>
      )}
    </div>
  );
};

export default Modules;
