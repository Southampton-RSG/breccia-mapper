
import typing

from django.core.exceptions import ObjectDoesNotExist


def port_question(apps, question_text: str,
                  answers_text: typing.Iterable[str]):
    PersonQuestion = apps.get_model('people', 'PersonQuestion')

    try:
        prev_question = PersonQuestion.objects.filter(
            text=question_text).latest('version')
        question = PersonQuestion.objects.create(
            text=question_text, version=prev_question.version + 1)

    except ObjectDoesNotExist:
        question = PersonQuestion.objects.create(text=question_text)

    for answer_text in answers_text:
        question.answers.get_or_create(text=answer_text)

    return question
