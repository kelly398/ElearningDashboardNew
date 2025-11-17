import React, { useEffect, useState } from 'react';
import { Card, Button, Form, Badge } from 'react-bootstrap';

const API_BASE = 'http://localhost:5000';
const DEFAULT_TOPICS = ['General', 'Cloud Computing', 'Web Design with JavaScript', 'Data Structures', 'Deep Learning'];

const Forum = ({ user }) => {
  const [posts, setPosts] = useState([]);
  const [topics, setTopics] = useState(DEFAULT_TOPICS);
  const [selectedTopic, setSelectedTopic] = useState(DEFAULT_TOPICS[0]);
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(false);
  const [replyText, setReplyText] = useState({});
  const [openReplyId, setOpenReplyId] = useState(null);

  const loadPosts = async () => {
    try {
      const res = await fetch(`${API_BASE}/forum`);
      const data = await res.json();
      setPosts(data.posts || []);
      const apiTopics = data.topics && data.topics.length ? data.topics : DEFAULT_TOPICS;
      setTopics(apiTopics);
      if (!apiTopics.includes(selectedTopic)) {
        setSelectedTopic(apiTopics[0]);
      }
    } catch (error) {
      console.error('Unable to load forum data', error);
    }
  };

  const submitPost = async () => {
    if (!content.trim() || !user?.id) return;
    setLoading(true);
    try {
      await fetch(`${API_BASE}/forum`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content, topic: selectedTopic, user_id: user.id }),
      });
      setContent('');
      await loadPosts();
    } catch (error) {
      console.error('Unable to submit post', error);
    } finally {
      setLoading(false);
    }
  };

  const submitReply = async (postId, topic) => {
    const message = (replyText[postId] || '').trim();
    if (!message || !user?.id) return;
    try {
      await fetch(`${API_BASE}/forum`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content: message, thread_id: postId, topic, user_id: user.id }),
      });
      setReplyText((prev) => ({ ...prev, [postId]: '' }));
      setOpenReplyId(null);
      await loadPosts();
    } catch (error) {
      console.error('Unable to submit reply', error);
    }
  };

  useEffect(() => {
    loadPosts();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const renderReplies = (replies = []) => {
    if (!replies.length) return null;
    return (
      <div className="mt-3 ms-4 border-start ps-3">
        {replies.map((reply) => (
          <Card key={reply.id} className="mb-2 shadow-sm border-light">
            <Card.Body>
              <div className="d-flex justify-content-between align-items-center mb-2">
                <Badge bg="light" text="dark">
                  Reply
                </Badge>
                <small className="text-muted">
                  {reply.author ? `by ${reply.author}` : ''}{' '}
                  {new Date(reply.date).toLocaleString()}
                </small>
              </div>
              <Card.Text className="mb-0">{reply.content}</Card.Text>
            </Card.Body>
            {renderReplies(reply.replies)}
          </Card>
        ))}
      </div>
    );
  };

  if (!user) {
    return <div className="p-4">Please log in to join the forum.</div>;
  }

  return (
    <div className="p-4">
      <h4>Course Discussion Forum</h4>

      <Form.Group className="mb-3">
        <Form.Label>Choose Topic</Form.Label>
        <Form.Select
          value={selectedTopic}
          onChange={(e) => setSelectedTopic(e.target.value)}
        >
          {topics.map((topic) => (
            <option key={topic} value={topic}>
              {topic}
            </option>
          ))}
        </Form.Select>
      </Form.Group>

      <Form.Control
        as="textarea"
        rows={3}
        placeholder={`Share something about ${selectedTopic}...`}
        value={content}
        onChange={(e) => setContent(e.target.value)}
      />
      <Button
        className="mt-2"
        onClick={submitPost}
        disabled={loading || !content.trim()}
      >
        {loading ? 'Posting...' : 'Post'}
      </Button>

      <div className="mt-4">
        {!posts.length && (
          <p className="text-muted">No conversations yet. Start one!</p>
        )}
        {posts.map((post) => (
          <Card key={post.id} className="mb-3 shadow-sm">
            <Card.Body>
              <div className="d-flex justify-content-between align-items-center mb-2">
                <Badge bg="secondary">{post.topic || 'General'}</Badge>
                <small className="text-muted">
                  {new Date(post.date).toLocaleString()}
                </small>
              </div>
              <div className="d-flex justify-content-between text-muted mb-2 small">
                <span>Posted by {post.author || 'User'}</span>
              </div>
              <Card.Text>{post.content}</Card.Text>
              <div className="d-flex gap-2 mt-3">
                <Button
                  size="sm"
                  variant="outline-primary"
                  onClick={() =>
                    setOpenReplyId((prev) => (prev === post.id ? null : post.id))
                  }
                >
                  {openReplyId === post.id ? 'Cancel' : 'Reply'}
                </Button>
              </div>
              {openReplyId === post.id && (
                <div className="mt-3">
                  <Form.Control
                    as="textarea"
                    rows={2}
                    placeholder="Write your reply..."
                    value={replyText[post.id] || ''}
                    onChange={(e) =>
                      setReplyText((prev) => ({ ...prev, [post.id]: e.target.value }))
                    }
                  />
                  <Button
                    size="sm"
                    className="mt-2"
                    onClick={() => submitReply(post.id, post.topic || 'General')}
                    disabled={!replyText[post.id]?.trim()}
                  >
                    Submit Reply
                  </Button>
                </div>
              )}
            </Card.Body>
            {renderReplies(post.replies)}
          </Card>
        ))}
      </div>
    </div>
  );
};

export default Forum;
