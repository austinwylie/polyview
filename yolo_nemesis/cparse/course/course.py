from cparse.models import *


def course_average_grade(course):
    ratings = course.polyrating_set
    return overall_gpa(list(map(grade_to_gpa, ratings)))


def grade_to_gpa(grade):
    if grade == Grade.A:
        gpa = 4.0
    elif grade == Grade.B:
        gpa = 3.0
    elif grade == Grade.C:
        gpa = 2.0
    elif grade == Grade.D:
        gpa = 1.0
    elif grade == Grade.F:
        gpa = 0.0
    else:
        gpa = None

    return gpa


def gpa_to_grade(grade):
    if grade >= 3.7:
        letter = 'A'
    elif grade >= 2.7:
        letter = 'B'
    elif grade >= 1.7:
        letter = 'C'
    elif grade >= 0.7:
        letter = 'D'
    elif grade >= 0.0:
        letter = 'F'
    else:
        return 'N/A'

    rounded = round(grade)

    remainder = grade - rounded
    if remainder >= 0.3:
        letter += '+'
    elif remainder <= -0.3:
        letter += '-'

    return letter


def overall_gpa(gpas):
    sum = 0.0
    count = 0
    for gpa in gpas:
        if gpa:
            sum += gpa
            count += 1

    if count > 0:
        return sum / count
    else:
        return None


def get_course(subject, number):
    try:
        course = Course.objects.get(subject=subject, number=number)
    except Course.DoesNotExist:
        course = None

    return course