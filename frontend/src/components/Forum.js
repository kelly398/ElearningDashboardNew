import React, { useEffect, useState } from 'react';
import { Card, Button, Form } from 'react-bootstrap';

const Forum = () => {
  const [posts, setPosts] = useState([]);
  const [content, setContent] = useState('');

  const loadPosts = () => {
    fetch('http://localhost:5000/forum')
      .then(res => res.json())
      .then(data => setPosts(data.posts || []));
  };

  const submitPost = () => {
    fetch('http://localhost:5000/forum', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content })
    })
      .then(res => res.json())
      .then(() => {
        setContent('');
        loadPosts();
      });
  };

  useEffect(() => {
    loadPosts();
  }, []);

  return (
    <div className="p-4">
      <h4>Forum</h4>
      <Form.Control
        as="textarea"
        rows={3}
        placeholder="Share your thoughts..."
        value={content}
        onChange={e => setContent(e.target.value)}
      />
      <Button className="mt-2" onClick={submitPost}>Post</Button>
      <div className="mt-4">
        {posts.map((p, i) => (
          <Card key={i} className="forum-post">
            <Card.Text>{p.content}</Card.Text>
            <small>{new Date(p.date).toLocaleString()}</small>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default Forum;
