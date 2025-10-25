import React, { useState, useEffect } from 'react';
import { Card, Button, Form } from 'react-bootstrap';

const Quiz = () => {
  const [quiz, setQuiz] = useState(null);
  const [answer, setAnswer] = useState('');
  const [response, setResponse] = useState(null);

  useEffect(() => {
    fetch('http://localhost:5000/quiz/1')
      .then(res => res.json())
      .then(data => setQuiz(data))
      .catch(() => setQuiz(null));
  }, []);

  const submitAnswer = () => {
    fetch('http://localhost:5000/quiz/1', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ answer })
    })
      .then(res => res.json())
      .then(data => setResponse(data));
  };

  return (
    <div className="p-4">
      {quiz && (
        <Card className="p-4">
          <h5 className="quiz-question">{quiz.question}</h5>
          <Form.Control type="text" value={answer} onChange={e => setAnswer(e.target.value)} />
          <Button className="mt-3" onClick={submitAnswer}>Submit</Button>
        </Card>
      )}
      {response && <p className="mt-3">{response.message}</p>}
    </div>
  );
};

export default Quiz;
