import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        db_host = os.getenv('DB_HOST', '127.0.0.1:5432')
        db_user = os.getenv('DB_USER', 'postgres')
        db_pass = os.getenv('DB_PASSWORD', 'postgres')
        db_name = os.getenv('DB_NAME', 'trivia_test')
        database_path = f"postgres://{db_user}:{db_pass}@{db_host}/{db_name}"
        setup_db(self.app, database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    def test_get_categories(self):
        resp = self.client().get('/categories')
        data = json.loads(resp.data)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['categories']))

    def test_get_paginated_questions(self):
        resp = self.client().get('/questions')
        data = json.loads(resp.data)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(len(data['categories']))
        self.assertTrue(data['total_questions'])

    def test_404_questions_page_too_big(self):
        resp = self.client().get('/questions?page=1000')
        data = json.loads(resp.data)

        self.assertEqual(resp.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], 'Not Found')

    def test_delete_qestion(self):
        question = Question(question='test delete question',
                            answer='test delete answer',
                            category=1, difficulty=1)
        question.insert()

        resp = self.client().delete(f'/questions/{question.id}')
        data = json.loads(resp.data)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], str(question.id))

    def test_400_delete_question(self):
        resp = self.client().delete('/questions/a')
        data = json.loads(resp.data)

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 400)
        self.assertEqual(data['message'], 'Bad Request')

    def test_404_delete_question(self):
        resp = self.client().delete('/questions/1000')
        data = json.loads(resp.data)

        self.assertEqual(resp.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 404)
        self.assertEqual(data['message'], 'Not Found')

    def test_create_question(self):
        question = Question(question='test delete question',
                            answer='test delete answer',
                            category=1, difficulty=1)

        prev_total = Question.query.count()
        resp = self.client().post('/questions', json=question.format())
        data = json.loads(resp.data)
        curr_total = Question.query.count()

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])
        self.assertEqual(curr_total, prev_total+1)

        created_question = Question.query.get(data['created'])
        created_question.delete()

    def test_400_create_question_with_bad_json(self):
        body = {
            'question': 'test delete question',
            'answer': 'test delete answer'
        }

        prev_total = Question.query.count()
        resp = self.client().post('/questions', json=body)
        data = json.loads(resp.data)
        curr_total = Question.query.count()

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 400)
        self.assertEqual(data['message'], 'Bad Request')
        self.assertEqual(prev_total, curr_total)

    def test_search_question(self):
        body = {
            'query': 'title',
        }

        resp = self.client().post('/questions/search', json=body)
        data = json.loads(resp.data)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])

        questions = data['questions']

        for question in questions:
            self.assertIn(body['query'], question['question'])

    def test_400_search_question_with_bad_json(self):
        body = {
            'no_query': 'wow',
        }

        resp = self.client().post('/questions/search', json=body)
        data = json.loads(resp.data)

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 400)
        self.assertEqual(data['message'], 'Bad Request')

    def test_get_questions_by_category(self):
        resp = self.client().get('/categories/1/questions')
        data = json.loads(resp.data)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])

    def test_400_get_questions_by_category(self):
        resp = self.client().get('/categories/one/questions')
        data = json.loads(resp.data)

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 400)
        self.assertEqual(data['message'], 'Bad Request')

    def test_play_quiz(self):
        body = {
            'previous_questions': [],
            'quiz_category': {'type': 'Science', 'id': 1}
        }

        resp = self.client().post('/quizzes', json=body)
        data = json.loads(resp.data)

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])

    def test_400_play_quiz(self):
        body = {
            'previous_questions': [],
        }

        resp = self.client().post('/quizzes', json=body)
        data = json.loads(resp.data)

        self.assertEqual(resp.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['error'], 400)
        self.assertEqual(data['message'], 'Bad Request')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
