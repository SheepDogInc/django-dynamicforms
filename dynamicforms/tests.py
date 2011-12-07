from django.contrib.auth.models import User
from django.test.client import RequestFactory
from django.test import TestCase
from models import *
from forms import *


class BaseTestCase(TestCase):

    def assertStringIn(self, needle, haystack, count=1):
        """
        Assert that haystack contains needle.
        By default, we make sure that it's contained at least once. If you want
        to make sure that it occurs a certain number of times, pass that number
        as count.
        """
        assert count == haystack.count(needle)

class ModelTests(BaseTestCase):

    def setUp(self):
        self.user = User.objects.create_user('test', 'test@test.com', 'test')
        self.factory = RequestFactory()

    def test_inheritance_resolving(self):
        self.assertEqual(0, DynamicFormQuestion.objects.count())
        df = DynamicForm.objects.create(name='Interview')

        q1 = DynamicTextQuestion.objects.create(
            question_text='What time is it?', parent_object=df, order=2)

        q2 = DynamicTextQuestion.objects.create(
            question_text='How are you?', parent_object=df, order=1)

        df = DynamicForm.objects.get(id=df.id)
        self.assertEqual(2, df.questions.count())

        questions = df.questions.all()
        q = questions[0]
        q = q.resolve()
        self.assertTrue(isinstance(q, DynamicTextQuestion))

        self.assertEqual(q1.id, questions[1].id)
        self.assertEqual(q2.id, questions[0].id)

    def test_form_creation(self):
        self.assertEqual(0, DynamicFormQuestion.objects.count())
        df = DynamicForm.objects.create(name='Interview')

        q1 = DynamicTextQuestion.objects.create(
            question_text='What time is it?', parent_object=df)

        q2 = DynamicYesNoQuestion.objects.create(
            question_text='Are you crazy?', parent_object=df)

        request = self.factory.get('/')
        f = DynamicFormCreator(request, df.id, user=self.user)
        form = str(f.get())

        self.assertStringIn('input', form, 3)
        self.assertStringIn('What time is it?', form)
        self.assertStringIn('Are you crazy?', form)
