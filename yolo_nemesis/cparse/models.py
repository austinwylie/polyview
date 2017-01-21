from django.db import models
from django_enumfield import enum
from django.utils.safestring import mark_safe

# polyrating reviewer grade
class Grade(enum.Enum):
    NOT_AVAILABLE = 0
    NO_CREDIT = 1
    F = 2
    D = 3
    C = 4
    B = 5
    A = 6
    CREDIT = 7


# student standing
class Standing(enum.Enum):
    FRESHMAN = 0
    SOPHOMORE = 1
    JUNIOR = 2
    SENIOR = 3
    FIFTH_YEAR = 4
    GRADUATE = 5


# four quarters/seasons in the academic year
class Quarter(enum.Enum):
    SUMMER = 0
    FALL = 1
    WINTER = 2
    SPRING = 3


# different section types within a course
class SectionType(enum.Enum):
    SEMINAR = 0
    LECTURE = 1
    LAB = 2
    ACTIVITY = 3
    INDEPENDENT = 4


# general link related to the university (usually *.calpoly.edu).
# referenced from other models to be displayed or parsed when appropriate.
# can also exist without an owner
class GeneralLink(models.Model):
    title = models.CharField(max_length=256, null=True)
    url = models.CharField(max_length=2048, null=True)
    description = models.TextField(null=True)


class Subject(models.Model):
    code = models.CharField(max_length=4)  # eg CSC
    title = models.CharField(max_length=512, null=True)  # eg Computer Science
    link = models.ForeignKey(GeneralLink, null=True)

    def __str__(self):
        return self.title + ' (' + self.code + ')'

    def __eq__(self, other):
        return self.code == other.code


# campus building
class Building(models.Model):
    code = models.CharField(max_length=64, null=True)  # eg 06
    name = models.CharField(max_length=256, null=True)  # eg Graphic Arts
    description = models.CharField(max_length=4096, null=True)  # not currently used
    map_alias = models.CharField(max_length=1024, null=True)  # not currently used
    floorplan_alias = models.CharField(max_length=1024, null=True)  # link to floorplan
    link = models.ForeignKey(GeneralLink, null=True)

    result_template = "search/buildingResult_jinja.html"

    def building_code(self):
        b_code = self.code.split("-")[0]
        return ("0" * (3 - len(b_code))) + b_code

    def __str__(self):
        return self.name


class Room(models.Model):
    building = models.ForeignKey(Building)
    code = models.CharField(max_length=64)  # eg 0123


# listing in the course catalog
class Course(models.Model):
    # TODO: make nullable columns more reasonable

    # TODO: add stemmed fields

    subject = models.ForeignKey(Subject, null=True)
    number = models.IntegerField(null=True)  # eg 101
    title = models.CharField(max_length=512, null=True)
    min_units = models.IntegerField(null=True)  # lowest unit count offered for this course
    max_units = models.IntegerField(null=True)  # highest unit count offered for this course
    uscp = models.NullBooleanField(null=True)  # fulfills uscp graduation requirement
    gwr = models.NullBooleanField(null=True)  # fulfills graduation writing requirement
    credit_no_credit = models.NullBooleanField(null=True)  # course offered credit/no credit
    offered_terms_known = models.NullBooleanField(null=True)  # inverse of TBD flag in Cal Poly course catalog
    offered_fall = models.BooleanField(default=False)  # typically offered in fall
    offered_winter = models.BooleanField(default=False)  # typically offered in winter
    offered_spring = models.BooleanField(default=False)  # typically offered in spring
    offered_summer = models.BooleanField(default=False)  # typically offered in summer
    description = models.CharField(max_length=4096, null=True)  # medium-length course description
    ge_areas = models.ManyToManyField('GeArea', null=True)  # ge areas this course appears in
    polyratings_count = models.IntegerField(null=True, default=0)  # total number of polyrating reviews for course
    requisites = models.CharField(max_length=4096, null=True)  # requirements for enrolling in course (deprecated)
    link = models.ForeignKey(GeneralLink, null=True)
    prerequisites_description = models.CharField(max_length=4096, null=True)
    corequisites_description = models.CharField(max_length=4096, null=True)
    recommended_description = models.CharField(max_length=4096, null=True)
    concurrent_description = models.CharField(max_length=4096, null=True)
    prerequisites = models.ManyToManyField('self', through='Prerequisite', related_name='prerequisites_set',
                                           symmetrical=False, null=True)  # list of Prerequisites
    corequisites = models.ManyToManyField('self', through='Corequisite', related_name='corequisites_set',
                                          symmetrical=False, null=True)  # list of Corequisites
    concurrent = models.ManyToManyField('self', through='Concurrent', related_name='concurrent_set', symmetrical=False,
                                        null=True)  # list of Concurrents
    recommended = models.ManyToManyField('self', through='Recommended', related_name='recommended_set',
                                         symmetrical=False, null=True)  # list of Recommendeds
    crosslistings = models.ManyToManyField('self', through='Crosslisting', related_name='+', symmetrical=False,
                                           null=True)  # currently unused

    result_template = "search/courseResult_jinja.html"

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['_state']
        state['crosslistings'] = map(lambda x: str(x), self.crosslistings.all())
        return state

    # TODO: write this method
    # Given a string with string refereneces to courses, replace those with links to actual course pages
    def add_links_to_reqs(self, string):
        return ["Take course <a href='/course/cpe/101'> CPE 101 </a>"]


    def to_str(self):
        return self.subject.code + ' ' + str(self.number)


    class Meta:
        unique_together = ('subject', 'number')

    def __eq__(self, other):
        return self.subject == other.subject and self.number == other.number

    def __str__(self):
        # return pformat(vars(self))
        return self.subject.code + ' ' + str(self.number)


class Instructor(models.Model):
    full_name = models.CharField(max_length=256)  # Turing, Alan M. / Turing, Alan M.
    first = models.CharField(max_length=128, null=True)  # Alan
    first_extended = models.CharField(max_length=128, null=True)  # Alan M. / Alan Mathison
    middle = models.CharField(max_length=128, null=True)  # M. / Mathison
    last = models.CharField(max_length=128, null=True)  # Turing
    phone = models.CharField(max_length=64, null=True)  # 707-123-1234
    alias = models.CharField(max_length=128, null=True)  # same as email address when appended with @calpoly.edu
    location = models.CharField(max_length=256, null=True)  # 14-123
    rating_count = models.IntegerField(null=True)  # number of polyrating reviews
    overall = models.FloatField(null=True)  # overall polyrating score
    presentation = models.FloatField(null=True)  # polyratings presentation score
    understanding = models.FloatField(null=True)  # polyratings student understanding score
    result_template = "search/instructorResult_jinja.html"
    link = models.ForeignKey(GeneralLink, null=True)

    def __str__(self):
        return self.first + ' ' + self.last

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['_state']
        return state

    def get_score(self):
        count = 0.0
        average = 0.0
        for each in self.polyratingsinstructor_set.all():
            count += each.polyrating_set.all().count()

        for each in self.polyratingsinstructor_set.all():
            average += (
                each.overall * (each.polyrating_set.all().count() / count))

        if count < 5:
            return 'N/A (not enough data)'
        else:
            return str(average) + "/4.00"

    def get_polyrating_count(self):
        count = 0
        for each in self.polyratingsinstructor_set.all():
            count += each.polyrating_set.all().count()
        return count

    def get_average_grade(self):
        count = 0
        number = 0
        for each in self.polyratingsinstructor_set.all():
            for rating in each.polyrating_set.all():
                grade = rating.grade
                if grade < Grade.F or grade > Grade.A:
                    continue
                else:
                    number += grade
                    count += 1

        if count < 10:
            return 'N/A (not enough data)'
        mean = float(number) / float(count)

        rounded = round(mean)

        if rounded == Grade.A:
            letter = 'A'
        elif rounded == Grade.B:
            letter = 'B'
        elif rounded == Grade.C:
            letter = 'C'
        elif rounded == Grade.D:
            letter = 'D'
        elif rounded == Grade.F:
            letter = 'F'
        else:
            return 'N/A'

        remainder = mean - rounded
        if remainder >= 0.3:
            letter += '+'
        elif remainder <= -0.3:
            letter += '-'

        return letter








class PolyratingsInstructor(models.Model):
    instructor = models.ForeignKey(Instructor, null=True)  # best guess as to who official, real-world instructor is
    full_name = models.CharField(max_length=256)  # Turing, Alan
    first = models.CharField(max_length=256)  # Alan
    last = models.CharField(max_length=256)  # Turing
    rating_count = models.IntegerField(null=True)  # number of polyrating reviews
    overall = models.FloatField(null=True)  # overall score
    presentation = models.FloatField(null=True)  # presentation score
    understanding = models.FloatField(null=True)  # student understanding score
    prof_id = models.IntegerField(null=True)  # instructor's polyratings ID (for creating links to polyratings)
    link = models.ForeignKey(GeneralLink, null=True)


# individual polyrating review
class Polyrating(models.Model):
    date = models.DateField(null=True)
    standing = enum.EnumField(Standing, null=True)  # student standing
    grade = enum.EnumField(Grade, null=True)  # reported grade received
    course = models.ForeignKey(Course, null=True)  # course taken
    comments = models.TextField(null=True)  # long-form student comments
    instructor = models.ForeignKey(PolyratingsInstructor, null=True)  # polyratings instructor who this review is for

    def __str__(self):
        return str(self.course) + ": " + str(self.comments)

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['_state']
        del state['_instructor_cache'] #I dont think we need to return the instructor data along with each rating
        return state


# academic term
class Term(models.Model):
    quarter = enum.EnumField(Quarter)
    year = models.IntegerField()
    start = models.DateField(null=True)
    end = models.DateField(null=True)

    def __str__(self):
        return str(str(self.quarter)) + " " + str(self.year) + ", " + str(
            self.start) + "-" + str(self.end)


class PageView(models.Model):
    ip = models.CharField(max_length=64, null=True)
    url = models.CharField(max_length=1024, null=True)
    timestamp = models.TimeField(null=True)


# specific section in one term for a course
class Section(models.Model):
    course = models.ForeignKey(Course, null=True)
    number = models.IntegerField(null=True)  # section number
    term = models.ForeignKey(Term, null=True)
    activity_type = models.CharField(max_length=64, null=True)  # TODO: switch to enum
    instructor = models.ForeignKey(Instructor, null=True)
    location = models.CharField(max_length=256, null=True)  # building number with room number. eg 14-123
    days = models.CharField(max_length=32, null=True)  # MWF, etc.
    start = models.TimeField(null=True)
    end = models.TimeField(null=True)
    location_capacity = models.IntegerField(null=True)  # location capacity
    enrollment_cap = models.IntegerField(null=True)  # enrollment/administrative capacity
    enrolled = models.IntegerField(null=True)
    waitlisted = models.IntegerField(null=True)
    dropped = models.IntegerField(null=True)

    def time_string(self):
        if self.start and self.end:
            return self.start.strftime("%I:%M").lstrip(
                '0') + "-" + self.end.strftime("%I:%M %p").lstrip('0')
        else:
            return ""

    def rating(self):
        if self.instructor:
            return self.instructor.overall
        else:
            return ""

    def location_link(self):
        if self.location and len(self.location.split("-")) >= 2:
            return mark_safe(
                "<a href='/building/" + self.location.split("-")[0].lstrip(
                    '0') + "'>" + self.location.split("-")[0].lstrip(
                    '0') + "-" + self.location.split("-")[1].lstrip(
                    '0') + "</a>")
        else:
            return self.location


class GeArea(models.Model):
    letter = models.CharField(max_length=1)
    number = models.IntegerField()

    class Meta:
        unique_together = ('letter', 'number')

    def __str__(self):
        return self.letter + str(self.number)


class Crosslisting(models.Model):
    containing_course = models.ForeignKey(Course, related_name='+')
    other_course = models.ForeignKey(Course, related_name='+')


class Prerequisite(models.Model):
    containing_course = models.ForeignKey(Course, related_name='+')
    other_course = models.ForeignKey(Course, related_name='+')


class Corequisite(models.Model):
    containing_course = models.ForeignKey(Course, related_name='+')
    other_course = models.ForeignKey(Course, related_name='+')


class Concurrent(models.Model):
    containing_course = models.ForeignKey(Course, related_name='+')
    other_course = models.ForeignKey(Course, related_name='+')


class Recommended(models.Model):
    containing_course = models.ForeignKey(Course, related_name='+')
    other_course = models.ForeignKey(Course, related_name='+')


class ReportedIssue(models.Model):
    ip = models.CharField(max_length=64, null=True)
    url = models.CharField(max_length=1024, null=True)
    instructor = models.ForeignKey(Instructor, null=True)
    timestamp = models.TimeField(null=True)
