from cparse.models import *


def searchySearch(query):
    import re

    query = query.strip()

    DEFAULT_LIMIT = 250
    limit = DEFAULT_LIMIT

    match = re.search('limit\s(\d{,4})', query)
    if match:
        limit = int(match.group(1))
        query = query[:match.start()]

    match = re.search('all\s*$', query, re.IGNORECASE)
    if match:
        limit = 5000
        query = query.replace('all', '').strip()

    query = query.strip()

    match = re.search('^((bu?i?ldi?ngs?|b(ui)?ldg?s?))([\w\s]+)', query,
                      re.IGNORECASE)
    if match:
        number = match.group(4).strip()

        try:
            building = Building.objects.get(code__iexact=number)
            return [building], 'building'
        except Building.DoesNotExist:
            try:
                building = Building.objects.filter(name__icontains=number)

                if building.count() == 0:
                    pass
                elif building.count() == 1:
                    return [building[0]], 'building'
                elif building.count() > 1:
                    return building, 'buildings'

            except Building.DoesNotExist:
                pass

    match = re.search('^([\w\s]+)((bu?i?ldi?ngs?|b(ui)?ldg?s?))', query,
                      re.IGNORECASE)

    if match:
        number = match.group(1).strip()

        try:
            building = Building.objects.get(code__iexact=number)
            return [building], 'building'
        except Building.DoesNotExist:
            try:
                building = Building.objects.filter(name__icontains=number)

                if building.count() == 0:
                    pass
                elif building.count() == 1:
                    return [building[0]], 'building'
                elif building.count() > 1:
                    return building, 'buildings'

            except Building.DoesNotExist:
                pass


    match = re.search('ge(\s+area)?\s*(\w)(\d)?', query, re.IGNORECASE)
    if match:
        area = match.group(2)

        ges = GeArea.objects.filter(letter__iexact=area)

        if match.group(3):
            ges = ges.filter(number=int(match.group(3)))

        results = set()

        for ge in ges.all():
            for c in ge.course_set.all():
                results.add(c)

        results = list(results)[:limit]
        results = sorted(results, key=lambda x: (x.subject.code, x.number))
        return results, 'courses'

    match = re.search('^([a-zA-Z]{2,4})[\-\s]?(\d{3})', query)
    if match:
        subject = match.group(1).strip()
        number = int(match.group(2))
        subjects = Subject.objects.filter(code__iexact=subject)
        try:
            course = Course.objects.get(subject__in=subjects, number=number)
            return [course], 'course'
        except Course.DoesNotExist:
            return [], 'none'

    match = re.search('^(\d{3})$', query.strip())
    if match:
        number = int(match.group(1))
        courses = Course.objects.filter(number=number)
        if courses.count() == 1:
            return courses, 'course'
        elif courses.count() > 1:
            results = list(courses)[:limit]
            results = sorted(results, key=lambda x: (x.subject.code, x.number))
            return results, 'courses'


    if 'random' in query:
        results = Course.objects.order_by('?')[:limit]
        results = list(results)
        results = sorted(results, key=lambda x: (x.subject.code, x.number))
        return results, 'courses'

    match = re.search('^([a-zA-Z]{2,4})', query)
    if match:
        if Subject.objects.filter(code__iexact=match.group(1)).exists():
            results = Course.objects.filter(
                subject__code__iexact=match.group(1)).order_by('number')[
                   :limit]
            results = list(results)
            results = sorted(results, key=lambda x: (x.subject.code, x.number))
            return results, 'courses'

    match = re.search('^(\w+)\s(\w+)$', query)
    if match:

        instructors = Instructor.objects.filter(
            last__icontains=match.group(2).strip(),
            first__icontains=match.group(1).strip())

        if instructors:
            results = instructors
            results = list(results)[:limit]
            results = sorted(results, key=lambda x: (x.last, x.first))

            if len(results) == 1:
                flag = 'instructor'
                return results, flag

        instructors = Instructor.objects.filter(
            last__icontains=match.group(2).strip()) | Instructor.objects.filter(
            first__icontains=match.group(1).strip())

        if instructors:
            results = instructors
            results = list(results)[:limit]
            results = sorted(results, key=lambda x: (x.last, x.first))

            if len(results) == 1:
                flag = 'instructor'
            else:
                flag = 'instructors'

            if len(match.group(2).strip()) >= 3 and len(
                    match.group(1).strip()) >= 3:
                if len(match.group(2).strip()) > 4 or len(
                        match.group(1).strip()) > 4:
                    return results, flag

    match = re.search('^([\w\s]+).*$', query)
    if match:

        instructors_last = Instructor.objects.filter(
            last__iexact=match.group(1).strip())

        instructors_full = Instructor.objects.filter(
            last__icontains=match.group(1).strip()) | Instructor.objects.filter(
            first__icontains=match.group(1).strip())

        if instructors_full.count() > 1:
            results = instructors_full
            results = list(results)[:limit]
            results = sorted(results, key=lambda x: (x.last, x.first))

            return results, 'instructors'

        if instructors_last.count() == 1:
            results = instructors_last
            results = list(results)[:limit]
            results = sorted(results, key=lambda x: (x.last, x.first))

            if len(results) == 1:
                return results, 'instructor'

        import Stemmer

        stemmer = Stemmer.Stemmer('english')

        word = match.group(1)

        if len(word) < 3:
            return [], 'courses'
        elif len(word) < 5:
            word = word
        else:
            word = stemmer.stemWord(word)

        results = (Course.objects.filter(description__icontains=word) | Course.objects.filter(
            title__icontains=word) | Course.objects.filter(
            subject__title__icontains=word)).order_by(
            'subject__code', 'number')[:limit]
        results = list(results)[:limit]
        results = sorted(results, key=lambda x: (x.subject.code, x.number))

        if len(results) > 0:
            print 'here'
            return results, 'courses'
        else:
            print 'there'
            instructors_full = Instructor.objects.filter(
                first__iexact=match.group(1).strip())

            if instructors_full.count() > 1:
                results = instructors_full
                results = list(results)[:limit]
                results = sorted(results, key=lambda x: (x.last, x.first))

                return results, 'instructors'

            elif len(instructors_full) == 1:
                return instructors_full, 'instructor'

        number = word.strip()

        try:
            building = Building.objects.get(code__iexact=number)
            return [building], 'building'
        except Building.DoesNotExist:
            try:
                building = Building.objects.filter(name__icontains=number)

                if building.count() == 0:
                    pass
                elif building.count() == 1:
                    return [building[0]], 'building'
                elif building.count() > 1:
                    return building, 'buildings'

            except Building.DoesNotExist:
                pass



    return [], 'none'


def get_polyratings_for_instructor(instructor):
    ratings = []

    for polyratings_instructor in instructor.polyratingsinstructor_set.all():
        ratings.extend(polyratings_instructor.polyrating_set.all())

    ratings = sorted(ratings, key=lambda rating: rating.date, reverse=True)
    return ratings


def get_score_for_instructor(instructor):
    # total_score = 0.0

    for polyratings_instructor in instructor.polyratingsinstructor_set.all():
        pass
    return 0.0