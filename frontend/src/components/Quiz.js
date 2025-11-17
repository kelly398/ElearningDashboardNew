import React, { useEffect, useState } from 'react';
import { Card, Button, Form, Alert, Spinner, Badge } from 'react-bootstrap';

const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:5000';
const QUESTIONS_PER_SESSION = 5;
const POINTS_PER_QUESTION = 20;

const gradeFromPercentage = (pct) => {
  if (pct >= 90) return { grade: 'A', comment: 'Outstanding! You mastered this topic.' };
  if (pct >= 80) return { grade: 'B', comment: 'Great job! Keep it up!' };
  if (pct >= 70) return { grade: 'C', comment: 'Good effort! Review and retry.' };
  if (pct >= 60) return { grade: 'D', comment: 'Keep practicing—you are close!' };
  return { grade: 'F', comment: 'Keep studying! You can do it!' };
};

const difficultyVariant = {
  easy: 'success',
  medium: 'warning',
  hard: 'danger',
};

const Quiz = ({ user, onQuizComplete }) => {
  const userId = user?.id;
  const [quizzes, setQuizzes] = useState([]);
  const [quizzesLoading, setQuizzesLoading] = useState(true);
  const [selectedQuiz, setSelectedQuiz] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [currentDifficulty, setCurrentDifficulty] = useState('medium');
  const [questionsAsked, setQuestionsAsked] = useState(0);
  const [questionsAnswered, setQuestionsAnswered] = useState(0);
  const [sessionQuestionTarget, setSessionQuestionTarget] = useState(QUESTIONS_PER_SESSION);
  const [selectedOption, setSelectedOption] = useState('');
  const [feedback, setFeedback] = useState(null);
  const [score, setScore] = useState(0);
  const [showResult, setShowResult] = useState(false);
  const [loadingQuestions, setLoadingQuestions] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [timeLeft, setTimeLeft] = useState(null);
  const [questionStartTime, setQuestionStartTime] = useState(null);
  const [quizError, setQuizError] = useState('');
  const [hasSubmitted, setHasSubmitted] = useState(false);
  const [sessionComplete, setSessionComplete] = useState(false);

  useEffect(() => {
    const fetchQuizzes = async () => {
      setQuizzesLoading(true);
      try {
        const res = await fetch(`${API_BASE}/quizzes`);
        const data = await res.json();
        if (res.ok) {
          setQuizzes(data.quizzes || []);
        } else {
          setQuizError(data.message || 'Unable to load available quizzes.');
        }
      } catch (error) {
        setQuizError('Unable to load available quizzes.');
      } finally {
        setQuizzesLoading(false);
      }
    };

    fetchQuizzes();
  }, []);

  useEffect(() => {
    if (!currentQuestion) return;
    setSelectedOption('');
    setFeedback(null);
    setHasSubmitted(false);
    const limit = currentQuestion.time_limit_seconds || 60;
    setTimeLeft(limit);
    setQuestionStartTime(Date.now());
    setCurrentDifficulty(currentQuestion.difficulty || currentDifficulty);
  }, [currentQuestion]);

  useEffect(() => {
    if (!currentQuestion || timeLeft === null || showResult || hasSubmitted) {
      return;
    }

    if (timeLeft <= 0) {
      handleTimeout();
      return;
    }

    const timerId = setInterval(() => {
      setTimeLeft((prev) => (prev !== null ? prev - 1 : prev));
    }, 1000);

    return () => clearInterval(timerId);
  }, [timeLeft, currentQuestion, showResult, hasSubmitted]);

  const startQuiz = (quiz) => {
    if (!userId) {
      setQuizError('Please log in to start a quiz.');
      return;
    }

    setSelectedQuiz(quiz);
    setScore(0);
    setShowResult(false);
    setFeedback(null);
    setQuizError('');
    setCurrentQuestion(null);
    setQuestionsAsked(0);
    setQuestionsAnswered(0);
    setSessionQuestionTarget(QUESTIONS_PER_SESSION);
    setSessionComplete(false);
    fetchNextQuestion(quiz, true);
  };

  const fetchNextQuestion = async (quiz, resetSession = false) => {
    if (!quiz || !userId) return;
    setLoadingQuestions(true);
    try {
      const params = new URLSearchParams({
        user_id: userId,
      });
      if (resetSession) {
        params.append('reset_session', '1');
      }

      const res = await fetch(`${API_BASE}/quiz/${quiz.id}/next-question?${params.toString()}`);
      const data = await res.json();
      if (!res.ok) {
        setQuizError(data.message || 'Unable to fetch question.');
        return;
      }

      if (data.quiz_complete) {
        setQuestionsAsked(QUESTIONS_PER_SESSION);
        setQuestionsAnswered(QUESTIONS_PER_SESSION);
        finalizeQuiz();
        return;
      }

      setCurrentQuestion(data.question);
      setQuestionsAsked((prev) => Math.min(prev + 1, QUESTIONS_PER_SESSION));
      setSessionQuestionTarget(QUESTIONS_PER_SESSION);
      setCurrentDifficulty(data.question?.difficulty || data.current_difficulty || 'medium');
    } catch (error) {
      setQuizError('Unable to fetch question.');
    } finally {
      setLoadingQuestions(false);
    }
  };

  const handleTimeout = () => {
    if (!currentQuestion || hasSubmitted) {
      return;
    }
    submitAnswer(true);
  };

  const submitAnswer = async (didTimeout = false) => {
    if (!currentQuestion || submitting || hasSubmitted) return;
    if (!didTimeout && !selectedOption.trim()) return;
    if (!userId) {
      setFeedback({ type: 'danger', msg: 'Please log in to submit answers.' });
      return;
    }

    setSubmitting(true);
    setHasSubmitted(true);
    const payload = {
      question_id: currentQuestion.id,
      answer: didTimeout ? null : selectedOption,
      time_taken: questionStartTime ? Math.round((Date.now() - questionStartTime) / 1000) : null,
      time_expired: didTimeout,
      user_id: userId,
    };

    try {
      const res = await fetch(`${API_BASE}/quiz/${selectedQuiz.id}/answer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (!res.ok) {
        setFeedback({ type: 'danger', msg: data.message || 'Unable to submit answer.' });
        setHasSubmitted(false);
        return;
      }

      if (data.score_delta) {
        setScore((prev) => prev + data.score_delta);
      }

      setFeedback({
        type: data.correct ? 'success' : 'danger',
        msg: data.message,
        correctAnswer: !data.correct ? data.correct_answer : undefined,
      });

      const updatedAnswered = Math.min(questionsAnswered + 1, QUESTIONS_PER_SESSION);
      const shouldComplete = Boolean(data.session_complete) || updatedAnswered >= QUESTIONS_PER_SESSION;

      setQuestionsAnswered(updatedAnswered);
      setCurrentDifficulty(data.current_difficulty || currentDifficulty);
      setSessionQuestionTarget(QUESTIONS_PER_SESSION);
      setSessionComplete(shouldComplete);

      setTimeout(() => handlePostAnswer(shouldComplete), 1200);
    } catch (error) {
      setFeedback({ type: 'danger', msg: 'Unable to submit answer.' });
      setHasSubmitted(false);
    } finally {
      setSubmitting(false);
    }
  };

  const handlePostAnswer = (shouldComplete) => {
    if (shouldComplete) {
      finalizeQuiz();
    } else {
      fetchNextQuestion(selectedQuiz);
    }
  };

  const finalizeQuiz = () => {
    setShowResult(true);
    setTimeLeft(null);
    setSessionComplete(true);
    if (typeof onQuizComplete === 'function') {
      onQuizComplete();
    }
  };

  const resetQuiz = () => {
    setSelectedQuiz(null);
    setCurrentQuestion(null);
    setShowResult(false);
    setFeedback(null);
    setScore(0);
    setTimeLeft(null);
    setQuestionStartTime(null);
    setSelectedOption('');
    setHasSubmitted(false);
    setQuizError('');
    setQuestionsAsked(0);
    setQuestionsAnswered(0);
    setSessionComplete(false);
  };

  const restartCurrentQuiz = () => {
    if (!selectedQuiz) return;
    setShowResult(false);
    setFeedback(null);
    setScore(0);
    setTimeLeft(null);
    setQuestionStartTime(null);
    setSelectedOption('');
    setHasSubmitted(false);
    setQuizError('');
    setQuestionsAsked(0);
    setQuestionsAnswered(0);
    setSessionComplete(false);
    fetchNextQuestion(selectedQuiz, true);
  };

  const renderQuizSelection = () => (
    <div className="p-4 text-center">
      <h3>Select Quiz Subject</h3>
      <p className="text-muted">Adaptive sessions ramp difficulty based on your performance.</p>
      {quizzesLoading ? (
        <div className="mt-4">
          <Spinner animation="border" role="status" />
          <p className="mt-2">Loading quizzes...</p>
        </div>
      ) : (
        <div className="d-flex flex-wrap justify-content-center gap-3 mt-4">
          {quizzes.map((quiz) => (
            <Card key={quiz.id} className="p-3 shadow-sm" style={{ width: '280px' }}>
              <Card.Title>{quiz.title}</Card.Title>
              <Card.Text className="text-muted small">{quiz.description}</Card.Text>
              <Card.Text className="fw-semibold">{quiz.question_count} questions available</Card.Text>
              <Button variant="primary" onClick={() => startQuiz(quiz)}>
                Start Adaptive Quiz
              </Button>
            </Card>
          ))}
          {!quizzes.length && (
            <Card className="p-4 shadow-sm">
              <Card.Text>No quizzes found. Seed the database to continue.</Card.Text>
            </Card>
          )}
        </div>
      )}
      {quizError && <Alert variant="danger" className="mt-3">{quizError}</Alert>}
    </div>
  );

  if (!selectedQuiz) {
    return renderQuizSelection();
  }

  if (loadingQuestions && !currentQuestion && !showResult) {
    return (
      <div className="p-4 text-center">
        <Spinner animation="border" role="status" />
        <p className="mt-2">Preparing adaptive question...</p>
      </div>
    );
  }

  if (showResult) {
    const totalPossible = sessionQuestionTarget * POINTS_PER_QUESTION || POINTS_PER_QUESTION;
    const percentage = Math.round((score / (totalPossible || POINTS_PER_QUESTION)) * 100);
    const { grade, comment } = gradeFromPercentage(percentage);
    return (
      <div className="p-4 text-center">
        <Card className="p-5 shadow-lg">
          <h2>{selectedQuiz.title} Quiz Complete!</h2>
          <h1 className="display-4 text-primary">{grade}</h1>
          <p className="lead">{comment}</p>
          <p><strong>Final Score: {score}/{totalPossible} ({percentage}%)</strong></p>
          <div className="d-flex flex-column flex-md-row gap-2 justify-content-center mt-3">
            <Button variant="primary" onClick={restartCurrentQuiz}>
              Try Again
            </Button>
            <Button variant="success" onClick={resetQuiz}>
              Choose Another Subject
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  if (!currentQuestion) {
    return (
      <div className="p-4 text-center">
        <Alert variant="warning">
          Unable to load questions for this quiz. Please try another subject.
        </Alert>
        <Button variant="outline-primary" onClick={resetQuiz}>Back to subjects</Button>
      </div>
    );
  }

  return (
    <div className="p-4 animate-fadeIn">
      <div className="d-flex justify-content-between align-items-center mb-3 flex-wrap gap-2">
        <div>
          <h4 className="mb-0">{selectedQuiz.title}</h4>
          <small className="text-muted">
            Question {Math.min(questionsAsked, sessionQuestionTarget)}/{sessionQuestionTarget}
          </small>
        </div>
        <div className="text-end">
          <Badge bg={difficultyVariant[currentDifficulty] || 'secondary'} className="me-2">
            Difficulty: {currentDifficulty || 'medium'}
          </Badge>
          <Badge bg={timeLeft !== null && timeLeft <= 5 ? 'danger' : 'secondary'}>
            Time Left: {timeLeft !== null ? `${timeLeft}s` : '--'}
          </Badge>
          <div className="small mt-1">
            Score: {score}/{sessionQuestionTarget * POINTS_PER_QUESTION}
          </div>
        </div>
      </div>

      {quizError && (
        <Alert variant="danger">
          {quizError}
        </Alert>
      )}

      <Card className="p-4 shadow-sm">
        <Card.Title className="quiz-question">{currentQuestion.question}</Card.Title>

        <Form.Group className="mt-3">
          {currentQuestion.options?.map((opt, i) => (
            <Form.Check
              key={i}
              type="radio"
              label={opt}
              name="answer"
              value={opt}
              onChange={() => setSelectedOption(opt)}
              checked={selectedOption === opt}
              disabled={hasSubmitted}
              className="mb-2"
            />
          ))}
        </Form.Group>

        <div className="d-flex gap-2 mt-3">
          <Button
            onClick={() => submitAnswer(false)}
            disabled={!selectedOption || submitting || hasSubmitted}
          >
            Submit
          </Button>
          <Button variant="outline-secondary" onClick={resetQuiz}>
            Change Subject
          </Button>
        </div>

        {feedback && (
          <Alert variant={feedback.type} className="mt-3">
            <div>{feedback.msg}</div>
            {feedback.correctAnswer && (
              <div className="small mt-1">Correct answer: {feedback.correctAnswer}</div>
            )}
          </Alert>
        )}
      </Card>
    </div>
  );
};

export default Quiz;
