import datetime

from django.shortcuts import render, redirect
from django.http import Http404
from ipware.ip import get_real_ip

from cparse.course.course import grade_to_gpa, gpa_to_grade
from cparse.models import Course, Instructor, PageView, Term, Section, Building, \
    Quarter, Subject, ReportedIssue, GeArea, Grade
from search import search as s


def log(request):
    ip = get_real_ip(request)

    if ip is not None:
        url = request.get_full_path()
        log_view(ip, datetime.datetime.now(), url)


def log_view(ip, timestamp, url):
    view = PageView()
    view.ip = ip
    view.timestamp = timestamp
    view.url = url
    view.save()


def report(request, instructor):
    ip = get_real_ip(request)
    url = request.get_full_path()
    report_log(ip, datetime.datetime.now(), url, instructor)


def report_log(ip, timestamp, url, instructor):
    view = ReportedIssue()
    view.ip = ip
    view.timestamp = timestamp
    view.url = url
    view.instructor = instructor
    view.save()


def index(request, major=None, number=None, alias=None, code=None):
    url = 'homepage/index_jinja.html'
    log(request)

    context = {}
    context['homepage'] = True
    context['week_num'] = week_num()
    # context['rando'] = Course.objects.order_by('?').first()
    return render(request, url, context)


def advancedSearch(request):
    url = 'homepage/advancedSearch.html'
    log(request)

    context = {}


    # BEGIN #
    # why doesn't this...
    instructors = Instructor.objects.all().values_list('full_name', flat=True).order_by('full_name')
    instructor_strings = ['No preference']
    instructor_strings.extend(list(instructors))

    context['instructors'] = instructor_strings
    # END #


    # BEGIN #
    # render the same way as this...?
    subjects = Subject.objects.all().values_list('code', flat=True).order_by('code')
    subjects_strings = ['No preference']
    subjects_strings.extend(list(subjects))

    context['subjects'] = subjects_strings
    # END $


    # context['geareas'] = list(GeArea.objects.all().order_by("letter", "number"))




    ges = GeArea.objects.all().values_list('letter', 'number').order_by('letter', 'number')
    print ges
    ges = map(lambda x: str(x[0]) + str(x[1]), ges)
    print ges
    ge_strings = ['No preference']
    ge_strings.extend(list(ges))

    context['geareas'] = ge_strings

    return render(request, url, context)


def course_browse(request):
    url = 'browse/courses_jinja.html'
    context = {}
    courses = Course.objects.all().order_by("subject__code", "number")
    context['courses1'] = courses[:len(courses) / 6]
    context['courses2'] = courses[len(courses) / 6: 2 * len(courses) / 6]
    context['courses3'] = courses[2 * len(courses) / 6: 3 * len(courses) / 6]
    context['courses4'] = courses[3 * len(courses) / 6: 4 * len(courses) / 6]
    context['courses5'] = courses[4 * len(courses) / 6: 5 * len(courses) / 6]
    context['courses6'] = courses[5 * len(courses) / 6:]

    context['subjects'] = Subject.objects.all().order_by('code')

    return render(request, url, context)


def instructor_browse(request):
    url = 'browse/instructors_jinja.html'
    context = {}
    context['instructors'] = Instructor.objects.all().order_by("last", "first")
    return render(request, url, context)


def building_browse(request):

    url = 'browse/buildings_jinja.html'
    context = {}
    context['buildings'] = Building.objects.all()
    return render(request, url, context)


def course(request, major=None, number=None, course=None):
    url = 'course/course_jinja.html'
    log(request)

    context = {}

    try:
        if not course:
            course = Course.objects.get(subject__code__iexact=major,
                                        number=number)

        context["course"] = course
        context['prereq_links'] = prerequisite_links(course)
        context['stats'] = course_stats(course)
        context['offered'] = get_sections
        context['humanize_prerequisites'] = humanized_course_prerequisites
        context[
            'humanize_corequisites'] = humanized_course_corequisites
        context[
            'humanize_recommended'] = humanized_course_recommended
        context[
            'humanize_list'] = humanize_list
        context['enrolled'] = number_of_students
        context['grade'] = average_grade

        return render(request, url, context)
    except Course.DoesNotExist:
        raise Http404("Course does not exist")


def building(request, code):
    url = "building/building_jinja.html"
    context = {}

    try:
        string = code.lstrip('0').upper()
        building = Building.objects.get(code=string)
        context['building'] = building
        return render(request, url, context)
    except Building.DoesNotExist:
        # Try again removing the last character from code, to catch buildings like 22a
        try:
            string = code.lstrip('0').upper()
            string = string[:len(string) - 1]
            building = Building.objects.get(code=string)
            context['building'] = building
            return render(request, url, context)
        except Building.DoesNotExist:
            raise Http404("Building does not exist")


def incorrect_polyratings(instructor):
    if not instructor:
        return False

    reports = instructor.reportedissue_set

    result = reports.all().values("ip").distinct()

    if result.count() >= 2:
        return True
    else:
        return False

    return False


def instructor(request, alias, instructor=None):
    url = 'instructor/instructor_jinja.html'
    log(request)
    context = {}
    try:
        if not instructor:
            instructor = Instructor.objects.filter(alias=alias)[0]

        if request.GET.get('report-button'):
            print 'BUTTON'
            button = True
            report(request, instructor)
        else:
            print 'NO BUTTON'
            button = False

        if incorrect_polyratings(instructor):
            warning = True
        else:
            warning = False

        context['instructor'] = instructor
        context['offered'] = get_sections
        context['get_grade'] = get_grade_string
        context['get_standing'] = get_standing_string
        ratings = s.get_polyratings_for_instructor(instructor)
        context['ratings'] = ratings
        context['filter_options'] = sorted(name_this_better_ugh(ratings))
        context['p_instructors'] = instructor.polyratingsinstructor_set.all()
        context['button'] = button
        context['warning'] = warning
        context['avg'] = instructor.get_average_grade()
        print 'warning: ', context['warning']

        return render(request, url, context)
    except IndexError:
        raise Http404("Instructor does not exist")


# Um what
def name_this_better_ugh(ratings):
    courses = set()
    for r in ratings:
        if not r.course:
            continue

        course = []

        course.append(r.course)

        if r.course.crosslistings.count() > 0:
            for c in r.course.crosslistings.all():
                course.append(c)

        courses.add(frozenset(course))

    options = []

    for course in courses:
        out = ""
        for cross in course:
            out += str(cross) + " / "

        out = out[:-3]
        options.append(out)

    return options


def get_grade_string(grade):
    grade_strings = ["", "No credit", "F", "D", "C", "B", "A", "Credit"]
    return grade_strings[grade]


def get_standing_string(standing):
    stranding_strings = ["Freshman", "Sophomore", "Junior", "Senior",
                         "5th Year", "Postgrad"]
    return stranding_strings[standing]


def split_requisites(reqs):
    if not reqs:
        return

    for req_section in reqs.split('.'):
        req_section = req_section.strip()

        if len(req_section) == 0:
            continue

        index = req_section.find(':')
        index += 1

        newString = '<strong>' + req_section[
                                 :index] + '</strong>' + req_section[
                                                         index:] + '.'
        yield newString


# TODO: This method will take in a course requisite and split out its prereqs in the format shown
# will also need this for coreqs, either extend this function or add another
# if you want to return just an array of courses, rather than this dictionary we could do that too
def prerequisite_links(course):
    results = []
    for req in course.prerequisites.all():
        results.append({"major": req.subject.code, "number": req.number})
    for req in course.corequisites.all():
        results.append({"major": req.subject.code, "number": req.number})
    for req in course.recommended.all():
        results.append({"major": req.subject.code, "number": req.number})
    for req in course.concurrent.all():
        results.append({"major": req.subject.code, "number": req.number})

    results = sorted(results, key=lambda x: (x['major'], x['number']))

    return results


# TODO: This method will return stats for a given course as a dictionary where key=display string and value=stat value
def course_stats(course):
    return {"Average class size": "TDB", "Average grade": "TBD",
            "Quarters offered": "TBD", "Last Offered": "TBD"}


# connector is 'and' or 'or'
# input is list of strings
def humanize_list(input, connector='and'):
    length = len(input)
    result = ''
    if not input or length == 0:
        return ''
    elif length == 1:
        return str(input[0])
    elif length == 2:
        return str(input[0]) + ' ' + str(connector) + ' ' + str(input[1])
    else:
        for i in xrange(len(input)):
            if i < length - 1:
                result += str(input[i]) + ', '
            else:
                result += connector + ' ' + str(input[i])
        return result


def humanized_course_prerequisites(input_course, connector='and'):
    return humanized_course_links(input_course.prerequisites_set.all(),
                                  connector)


def humanized_course_corequisites(input_course, connector='and'):
    return humanized_course_links(input_course.corequisites_set.all(),
                                  connector)


def humanized_course_recommended(input_course, connector='and'):
    return humanized_course_links(input_course.recommended_set.all(), connector)


def humanized_course_links(input_courses, connector='and'):
    new_list = []

    for each in input_courses:
        new_list.append(get_course_a_tag(each))

    new_list = sorted(new_list)

    return humanize_list(new_list, connector)


def get_course_a_tag(in_course):
    subj = str(in_course.subject.code)
    num = str(in_course.number)
    result = '<a href="/course/' + subj + '/' + num + '">' + subj + ' ' + num + '</a>'
    return result


# Given a quarter as a string eg "Spring 2015" and optionally a course and/or instructor, return the offered courses
# matching that criteria
def get_sections(course=None, quarter=None, instructor=None):
    courses = []
    if not quarter:
        return courses

    quarterInt = 0
    quarter_string = quarter.split(" ")[0]
    if quarter_string == "Fall":
        quarterInt = Quarter.FALL
    elif quarter_string == "Winter":
        quarterInt = Quarter.WINTER
    elif quarter_string == "Spring":
        quarterInt = Quarter.SPRING
    elif quarter_string == "Summer":
        quarterInt = Quarter.SUMMER

    try:
        term = Term.objects.get(quarter=quarterInt, year=quarter.split(" ")[1])
        if instructor is not None:
            courses = Section.objects.filter(instructor=instructor, term=term)
        else:

            from django.db.models import Q

            filter = Q(course=course, term=term)

            for c in course.crosslistings.all():
                filter = filter | Q(course=c, term=term)

            courses = Section.objects.filter(filter)
    except Term.DoesNotExist:
        return []

    if course:
        courses = courses.order_by('number', 'days', 'start', 'end')
    elif instructor:
        courses = courses.order_by('course', 'number', 'days', 'start', 'end')

    return courses


def search(request):
    url = 'search/search.html'
    log(request)
    query = request.GET.get('query', '')
    results, flag = s.searchySearch(query)

    # one course
    if flag == 'course':
        return redirect(
            '/course/' + results[0].subject.code + "/" + str(results[0].number),
            course=results[0])
    # one instructor
    elif flag == 'instructor':
        return redirect('/instructor/' + results[0].alias,
                        instructor=results[0])
    elif flag == 'building':
        return redirect('/building/' + results[0].code,
                        building=results[0])
    elif flag == 'courses':
        # zero, one, or more courses
        pass
    elif flag == 'instructors':
        # zero, one, or more instructors
        pass
    else:
        # default
        # mixed results not implemented yet
        pass

    context = {}
    context['query'] = query
    context['results'] = results
    context['count'] = len(results)
    context['split_reqs'] = split_requisites

    context['FLAGS_IN_HEADER'] = False

    return render(request, url, context)


def adv_search(request):
    url = 'search/search.html'
    log(request)
    # The keys for all possible parameters
    available_params = ["keywords", "instructor", "subject", "geArea", "crnc", "minUnits",
                        "maxUnits", "uscp", "futureQuarter", "nextQuarter", "gwr"]

    # The parameters that actually matter for filtering for this request
    filter_params = {}

    for param in available_params:
        val = request.GET.get(param, '')

        # Don't bother with filters which are Any or blank
        if val != '' and val != 'No preference':
            filter_params[param] = val

    # TODO: find results using filter_params

    courses = Course.objects.all()

    if 'subject' in filter_params:
        courses = courses.filter(subject__code__iexact=filter_params['subject'])

    if 'minUnits' in filter_params:
        courses = courses.filter(max_units__gte=int(filter_params['minUnits']))
        courses = courses.filter(credit_no_credit=False)

    if 'maxUnits' in filter_params:
        courses = courses.filter(min_units__lte=int(filter_params['maxUnits']))
        courses = courses.filter(credit_no_credit=False)

    if 'gwr' in filter_params:
        courses = courses.filter(gwr=True if filter_params['gwr'] else False)

    if 'uscp' in filter_params:
        courses = courses.filter(uscp=True if filter_params['uscp'] else False)

    if 'crnc' in filter_params:
        courses = courses.filter(credit_no_credit=True if filter_params['crnc'] else False)

    if 'instructor' in filter_params:
        sections = Section.objects.filter(instructor__full_name__iexact=filter_params['instructor'])
        temp_courses = courses.filter(id__in=sections.values_list('course__id'))
        courses = courses & temp_courses

    if 'nextQuarter' in filter_params:
        sections = Section.objects.filter(term__quarter=Quarter.FALL, term__year=2015).values_list('course__id',
                                                                                                     flat=True)

        if filter_params['nextQuarter'] == 'Yes':
            temp_courses = courses.filter(id__in=sections)
            courses = courses & temp_courses

            crosslists = []
            for course in courses:
                crosslists.extend(course.crosslistings.all())

            crosslists = map(lambda x: x.id, crosslists)
            temp_courses = courses.filter(id__in=crosslists)
            courses = courses | temp_courses



        else:
            courses = courses.exclude(id__in=sections)
            crosslists = []
            for course in courses:
                crosslists.extend(course.crosslistings.all())

            crosslists = map(lambda x: x.id, crosslists)
            courses = courses.exclude(id__in=crosslists)

    if 'futureQuarter' in filter_params:
        sections = Section.objects.filter(term__quarter=Quarter.WINTER, term__year=2016).values_list(
            'course__id',
            flat=True)

        if filter_params['futureQuarter'] == 'Yes':
            temp_courses = courses.filter(id__in=sections)
            courses = courses & temp_courses

            crosslists = []
            for course in courses:
                crosslists.extend(course.crosslistings.all())

            crosslists = map(lambda x: x.id, crosslists)
            temp_courses = courses.filter(id__in=crosslists)
            courses = courses | temp_courses

        else:
            courses = courses.exclude(id__in=sections)
            crosslists = []
            for course in courses:
                crosslists.extend(course.crosslistings.all())

            crosslists = map(lambda x: x.id, crosslists)
            courses = courses.exclude(id__in=crosslists)

    if 'geArea' in filter_params:
        ge = GeArea.objects.get(letter=filter_params['geArea'][0], number=int(filter_params['geArea'][1]))
        courses_temp = Course.objects.filter(ge_areas__id=ge.id)
        courses = courses & courses_temp

    if 'keywords' in filter_params:
        import Stemmer

        stemmer = Stemmer.Stemmer('english')
        # stemmer.stemWord()

        words_and = filter_params['keywords'].split(',')
        words_amp = filter_params['keywords'].split('&')
        words_or = filter_params['keywords'].split('|')

        or_flag = False

        if (len(words_or) > len(words_and)) and (len(words_or) > len(words_amp)):
            or_flag = True
            words = words_or
        else:
            if '&' in filter_params['keywords']:
                words = words_amp
            else:
                words = words_and

        new_courses = None

        for word in words:
            word = word.strip()
            word = stemmer.stemWord(word)

            course_title_set = Course.objects.filter(title__icontains=word)
            course_description_set = Course.objects.filter(description__icontains=word)

            if len(words) == 1 and len(words[0]) < 4:
                pass
            elif len(word) < 4:
                if or_flag:
                    new_courses = new_courses | (course_title_set)
                else:
                    new_courses = new_courses & (course_title_set)
            else:

                if not new_courses:
                    new_courses = course_title_set | course_description_set
                else:
                    if or_flag:
                        new_courses = new_courses | (course_title_set | course_description_set)
                    else:
                        new_courses = new_courses & (course_title_set | course_description_set)

        if new_courses:
            courses = courses & new_courses

    courses = courses.order_by()

    if courses.count() == Course.objects.all().count():
        results = []
    else:
        results = list(courses)

    context = {}
    context['query'] = request.GET.get("keywords", "")
    results = sorted(results, key=lambda x: str(x))
    context['results'] = results
    context['count'] = len(results)
    context['split_reqs'] = split_requisites
    return render(request, url, context)


def faq(request):
    url = 'faq.html'
    log(request)
    context = {}
    return render(request, url, context)


def week_num():
    from datetime import datetime, timedelta

    d1 = datetime(2015, 1, 5)
    d2 = datetime.now()

    monday1 = (d1 - timedelta(days=d1.weekday()))
    monday2 = (d2 - timedelta(days=d2.weekday()))

    return (monday2 - monday1).days / 7


def number_of_students(course):
    enrolled = 0
    capacity = 0

    courses = [course]
    for crosslist in course.crosslistings.all():
        courses.append(crosslist)

    for c in courses:
        for section in c.section_set.all():
            if section.enrolled and section.enrollment_cap and section.term.quarter == Quarter.SPRING and section.term.year == 2015:
                enrolled += section.enrolled
                capacity += section.enrollment_cap

    if capacity == 0:
        return -1
    return enrolled / float(capacity) * 100


def average_grade(course):
    count = 0
    gpa = 0.0

    courses = [course]
    for crosslist in course.crosslistings.all():
        courses.append(crosslist)

    for c in courses:
        for rating in c.polyrating_set.all():
            if rating.grade < Grade.F or rating.grade > Grade.A:
                continue
            else:
                gpa += grade_to_gpa(rating.grade)
                count += 1

    if count < 10:
        return 'N/A'

    mean = float(gpa) / float(count)

    return gpa_to_grade(mean)




def since_quarter_start(date):
    pass
    # bad logic below
    from datetime import datetime, timedelta

    d1 = datetime(2015, 1, 5)
    d2 = since_quarter_start

    monday1 = (d1 - timedelta(days=d1.weekday()))
    monday2 = (d2 - timedelta(days=d2.weekday()))

    return (monday2 - monday1).days / 7

