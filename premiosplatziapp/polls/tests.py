import datetime

from django.test import TestCase
from django.utils import timezone
from django.urls.base import reverse

from .models import Question


class QuestionModelTest(TestCase):
    
    def test_was_published_recently_with_future_quetions(self):
        """Was_published_recently returns false for questions whose pub_date is in the future"""
        time= timezone.now() + datetime.timedelta(days=30) 
        future_question= Question(question_text="¿Quién es el mejor CD de Platzi", pub_date=time)    
        self.assertIs(future_question.was_published_recently(),False)

    def test_was_published_with_past_questions(self):
        """Was_publised_with_past_questions returns false for questions whose pub_date is the past"""
        time=timezone.now() - datetime.timedelta(days=30)
        future_question= Question(question_text="¿Quién es el mejor CD de Platzi", pub_date=time)
        self.assertIs(future_question.was_published_recently(),False)

    def test_was_published_with_today_questions(self):
        """Was_published_with_today_questions returns true for questions whose pub_date is in the present"""
        time=timezone.now()
        future_question= Question(question_text="¿Quién es el mejor CD de Platzi", pub_date=time)
        self.assertIs(future_question.was_published_recently(),True)

    # def test_create_question_without_choices(self):
    #     """
    #     If the questions hasn't choices it id deleted.
    #     """
    #     question=Question.objects.create(
    #         question_text="¿Quien es el mejor CD de platzi",
    #         pub_date=timezone.now(),
    #         choice=0)
    #     if question.choice <=1:
    #         question.delete()

    #     question_count=len(Question.objects.all())
    #     self.assertEqual(question_count,0)



def create_question(question_text , days):
    """Create a questiom with the given "question_text" and published the given number of days offset to now
    (negative for questions published in the past, positive for questions that have yet to be published)
    """
    time=timezone.now() + datetime.timedelta(days=days) 
    return Question.objects.create(question_text=question_text,pub_date=time)

class QuestionIndexViewTest(TestCase):

    def test_no_question(self):
        """If not question exist an appropieate message is displayed"""
        response=self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code,200)
        self.assertContains(response, "No polls are available")
        self.assertQuerysetEqual(response.context["latest_question_list"],[])

    def test_future_question(self):
        """Questions with a pub_date in the future aren't displayed on the index page.
        """
        create_question("Future question",days=30)
        response=self.client.get(reverse("polls:index"))
        self.assertContains(response,"No polls are available")
        self.assertQuerysetEqual(response.context["latest_question_list"],[])

    def test_past_question(self):
        """Question with a pub_date in the past are displayed on the index page"""
        question=create_question("Past question",days=-10)
        response=self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(response.context["latest_question_list"],[question])


    def test_future_question_and_past_question(self):
        """
        Even if both past and future questiion exist, only past question are displayed
        """
        past_question=create_question(question_text="Past question", days=-30)
        futures_question=create_question(question_text="Future question", days=30)
        response=self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(
            response.context["latest_question_list"],
            [past_question]
        )

    def test_two_past_questions(self):
        """
        The question index page may display multiple questions.
        """
        past_question1=create_question(question_text="Past question", days=-30)
        past_question2=create_question(question_text="Past question", days=-40)
        response =self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(
            response.context["latest_question_list"],
            [past_question1,past_question2]
        )

    def test_two_future_questions(self):
        """
        The question index page may display multiple questions.
        """
        future_question1=create_question(question_text="Future question", days=+30)
        future_question2=create_question(question_text="Future question", days=+40)
        response =self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(
            response.context["latest_question_list"],
            []
        )


class QuestionDetailViewTest(TestCase):
    def test_no_questions(self):
        """
        The result view of a question that doesn't exist
        return a 404 error not found
        """
        url= reverse("polls:results",args=(1,))
        response= self.client.get(url)
        self.assertEqual(response.status_code,404)

    def test_future_questions(self):
        """
        The detail view of a question with a pub_date in the future
        returns a 404 http error not found
        """
        futures_question=create_question(question_text="future question", days=30)
        url=reverse("polls:detail",args=(futures_question.id,))
        response=self.client.get(url)
        self.assertEqual(response.status_code,404)


    def test_past_questions(self):
        """
        the detail view of a question with a pub_date in the 
        past displays the question's text
        """
        past_question=create_question(question_text="Past question", days=-30)
        url=reverse("polls:detail",args=(past_question.id,))
        response=self.client.get(url)
        self.assertContains(response,past_question.question_text)


    
    
