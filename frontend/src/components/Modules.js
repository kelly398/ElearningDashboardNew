import React, { useEffect, useState } from 'react';
import { Card, Spinner, Alert, Form, Row, Col, Button } from 'react-bootstrap';

const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:5000';

const Modules = ({ user }) => {
  const userId = user?.id;
  const [modules, setModules] = useState([]);
  const [selectedIds, setSelectedIds] = useState(new Set());
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [saving, setSaving] = useState(false);
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

    const fetchSelections = async () => {
      if (!userId) return;
      try {
        const res = await fetch(`${API_BASE}/users/${userId}/modules`);
        const data = await res.json();
        if (res.ok) {
          setSelectedIds(new Set((data.modules || []).map((m) => m.module_id)));
        }
      } catch (err) {
        // ignore selection fetch errors; they'll be handled during save
      }
    };

    fetchModules();
    fetchSelections();
  }, [userId]);

  const filteredModules = modules.filter((module) => {
    if (!filter.trim()) return true;
    const term = filter.toLowerCase();
    return (
      module.title.toLowerCase().includes(term) ||
      module.category.toLowerCase().includes(term)
    );
  });

  const toggleSelection = (moduleId) => {
    setSuccess('');
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(moduleId)) {
        next.delete(moduleId);
      } else {
        next.add(moduleId);
      }
      return next;
    });
  };

  const saveSelection = async () => {
    if (!userId) {
      setError('Please log in to save module selections.');
      return;
    }
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      const res = await fetch(`${API_BASE}/users/${userId}/modules`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ module_ids: Array.from(selectedIds) }),
      });
      const data = await res.json();
      if (res.ok) {
        setSuccess('Modules saved successfully!');
      } else {
        setError(data.message || 'Unable to save modules.');
      }
    } catch (err) {
      setError('Unable to save modules.');
    } finally {
      setSaving(false);
    }
  };

  if (!userId) {
    return (
      <div className="p-3">
        <Alert variant="warning">Please log in to choose modules.</Alert>
      </div>
    );
  }

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
      {success && <Alert variant="success">{success}</Alert>}

      {loading && (
        <div className="text-center py-5">
          <Spinner animation="border" role="status" />
        </div>
      )}

      {error && <Alert variant="danger">{error}</Alert>}

      {!loading && !error && (
        <>
          <Row xs={1} md={2} lg={3} className="g-3">
            {filteredModules.map((module) => {
              const isSelected = selectedIds.has(module.id);
              return (
                <Col key={module.id}>
                  <Card
                    className={`shadow-sm h-100 module-card ${isSelected ? 'border border-success' : ''}`}
                    onClick={() => toggleSelection(module.id)}
                    role="button"
                  >
                    <Card.Body>
                      <div className="d-flex justify-content-between align-items-center mb-2">
                        <Card.Title className="mb-0">{module.title}</Card.Title>
                        <span className="badge bg-secondary">{module.category}</span>
                      </div>
                      <Card.Text className="text-muted">{module.description}</Card.Text>
                    </Card.Body>
                    <Card.Footer className="d-flex justify-content-between align-items-center text-muted">
                      <small>Duration: {module.duration || 0} min</small>
                      <Form.Check
                        type="checkbox"
                        checked={isSelected}
                        onChange={() => toggleSelection(module.id)}
                        label="Select"
                        onClick={(e) => e.stopPropagation()}
                      />
                    </Card.Footer>
                  </Card>
                </Col>
              );
            })}
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
          <div className="text-end mt-3">
            <Button onClick={saveSelection} disabled={saving}>
              {saving ? 'Saving...' : 'Save Selection'}
            </Button>
          </div>
        </>
      )}
    </div>
  );
};

export default Modules;
