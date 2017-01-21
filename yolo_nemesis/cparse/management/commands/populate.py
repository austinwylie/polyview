import re
import urllib
import urllib2
import itertools
from datetime import datetime
import urlparse

from django.core.management.base import BaseCommand
from bs4 import BeautifulSoup
from django.utils import importlib

from cparse import models
from cparse.models import Prerequisite, Subject, Course, GeArea, Concurrent, \
    Corequisite, Recommended, Crosslisting, Polyrating, Instructor, \
    PolyratingsInstructor, Section, Term, Quarter, Building











# TODO: move regex patterns to top and make them compiled
# TODO: name regex groups
# TODO: figure out unicode to ascii conversion

class Command(BaseCommand):
    import codecs
    import sys

    streamWriter = codecs.lookup('utf-8')[-1]
    sys.stdout = streamWriter(sys.stdout)

    RESET_CATALOG = True  # Flushes database and repopulation.
    SMALL_COURSE_SET = False  # On catalog reset, True value results in
    # abbreviated test set of courses

    I_AM_AUSTIN = False

    log_file = open('population_log.txt', 'a')

    help = 'Site parsing and database population'

    catalog_url = 'http://catalog.calpoly.edu'
    schedules_url = 'http://schedules.calpoly.edu/'

    toc_location = '/coursesaz/'

    relative_terms = ["last", "curr", "next", "2164"]

    def handle(self, *args, **options):
        buildings, instructors, courses, polyratings, schedule, extended = False, False, False, False, False, False

        if not instructors:
            response = raw_input(
                'Do you want to refresh instructor data? The entire database will be refreshed. (y/n): ')
            response = str(response)
            if response.strip() == 'y':
                instructors = True
                buildings = True
                courses = True
                polyratings = True
                schedule = True
                extended = True

        if not courses:
            response = raw_input(
                'Do you want to refresh all course data? Schedules and Polyratings will also be refreshed. (y/n): ')
            if response.strip() == 'y':
                courses = True
                polyratings = True
                schedule = True
                extended = True

        if not extended:
            response = raw_input(
                'Do you want to refresh extended course data? (y/n): ')
            if response.strip() == 'y':
                extended = True

        if not polyratings:
            response = raw_input(
                'Do you want to refresh Polyrating data? (y/n): ')
            if response.strip() == 'y':
                polyratings = True

        if not schedule:
            response = raw_input(
                'Do you want to refresh schedule data? (y/n): ')
            if response.strip() == 'y':
                schedule = True

        if not buildings:
            response = raw_input(
                'Do you want to refresh building data? (y/n): ')
            if response.strip() == 'y':
                buildings = True

        out = "Beginning."
        print out
        self.log_population(out)

        # point of no

        # return

        # for modifying data
        # is here.

        if buildings:
            out = "Refreshing buildings..."
            print out
            self.log_population(out)
            self.refresh_buildings()

        if instructors:
            out = "Refreshing instructors..."
            print out
            self.log_population(out)
            self.refresh_instructor_info()

        if courses:
            out = "Refreshing basic course data..."
            print out
            self.log_population(out)
            self.refresh_initial_data()

        if extended:
            out = "Refreshing extended course data..."
            print out
            self.log_population(out)
            self.refresh_extended_data()

        if schedule:
            out = "Refreshing schedule..."
            print out
            self.log_population(out)
            self.refresh_schedule()

        if polyratings:
            out = "Refreshing instructor reviews..."
            print out
            self.log_population(out)
            self.refresh_polyratings_info()

        out = "Done."
        print out
        self.log_population(out)

    def log_population(self, log_statement):
        import datetime

        ts = datetime.datetime.now()
        ts = str(ts)
        self.log_file.write(ts + ": " + log_statement + '\n')


    def refresh_instructor_info(self):
        Instructor.objects.all().delete()
        out = "Deleted Instructor table."
        print out
        self.log_population(out)
        self.populate_instructor_info()

    def refresh_schedule(self):
        Term.objects.all().delete()
        Section.objects.all().delete()
        out = "Deleted Term and Section tables."
        print out
        self.log_population(out)
        self.populate_schedule()

    def refresh_buildings(self):
        out = "Deleted Building table."
        print out
        self.log_population(out)
        Building.objects.all().delete()
        self.populate_buildings()

    def refresh_polyratings_info(self):
        Polyrating.objects.all().delete()
        PolyratingsInstructor.objects.all().delete()
        out = "Deleted Polyrating and PolyratingInstructor tables."
        print out
        self.log_population(out)
        self.populate_polyratings_info()

    def populate_general_link(self):
        return

    def populate_buildings(self):
        url = 'http://afd.calpoly.edu/facilities/maps_floorplans.asp'

        soup = BeautifulSoup(
            self.get_url_content(url))

        main_left_full = soup.find('div', id='mainLeftFull')

        trs = main_left_full.find_all('tr')
        for tr in trs:
            a_tag = tr.find('a')

            if not a_tag:
                continue

            building = Building()

            floorplan_url = a_tag['href']
            building.floorplan_alias = 'http://afd.calpoly.edu/facilities/' + floorplan_url

            title = a_tag.string

            match = re.search('(\d\w*)\s(.+)', title.strip())
            code = match.group(1)
            name = match.group(2)

            building.code = code
            building.name = name
            if building.name:
                building.name = building.name.strip()

            building.save()


    def populate_schedule(self):


        import codecs
        import sys

        UTF8Writer = codecs.getwriter('utf8')
        sys.stdout = UTF8Writer(sys.stdout)

        for relative_term in self.relative_terms:
            for subject in Subject.objects.all():
                url = self.schedules_url + "subject_" + subject.code.upper() + "_" + relative_term + ".htm"

                soup = BeautifulSoup(
                    self.get_url_content(url))

                term_info = soup.find('div', id='descriptor')

                if not term_info:
                    continue
                else:
                    term_info = term_info.find_all('span')

                if len(term_info) < 3:
                    continue

                quarter = term_info[2].string.strip()
                quarter_enum = None
                if "fall" in quarter.lower():
                    quarter_enum = Quarter.FALL
                elif "winter" in quarter.lower():
                    quarter_enum = Quarter.WINTER
                elif "spring" in quarter.lower():
                    quarter_enum = Quarter.SPRING
                elif "summer" in quarter.lower():
                    quarter_enum = Quarter.SUMMER

                if not quarter_enum:
                    continue

                dates = term_info[3].string
                match = re.search(
                    '(\d{2}/\d{2}/\d{4})\s.+\s(\d{2}/\d{2}/\d{4})',
                    dates.strip())
                if match:
                    start = datetime.strptime(match.group(1), '%m/%d/%Y')
                    end = datetime.strptime(match.group(2), '%m/%d/%Y')
                    year = start.year

                    # get academic term
                    term = self.get_term(quarter_enum, year, start, end)
                else:
                    term = None
                if not soup.find('table'):
                    continue

                rows = soup.find_all('tr', re.compile('entry'))

                for row in rows:
                    course_name = row.find('td', 'courseName')
                    if course_name.a:
                        course_name = course_name.a.string
                    else:
                        course_name = course_name.string

                    if not course_name:
                        continue

                    match = re.search('([A-Z]{2,4})\s+(\d+)',
                                      course_name.strip())
                    if match:
                        section = Section()
                        subject = match.group(1)
                        number = int(match.group(2))
                        course = self.get_course(subject, number)
                        section.course = course

                        section_num = row.find('td', 'courseSection').string
                        section_num = self.to_ascii(section_num)
                        try:
                            section.number = int(section_num.strip())
                        except:
                            continue

                        course_type = row.find('td', 'courseType').string
                        course_type = self.to_ascii(course_type)
                        section.activity_type = course_type.strip()

                        days = row.find('td', 'courseDays').string
                        days = self.to_ascii(days)
                        section.days = days.strip()

                        start_time = row.find('td', 'startTime').string
                        start_time = self.to_ascii(start_time)
                        if len(start_time) > 3:
                            section.start = datetime.strptime(
                                start_time.strip(), "%I:%M %p")

                        end_time = row.find('td', 'endTime').string
                        end_time = self.to_ascii(end_time)
                        if len(end_time) > 3:
                            section.end = datetime.strptime(end_time.strip(),
                                                            "%I:%M %p")

                        location = row.find('td', 'location').string
                        location = self.to_ascii(location)
                        if len(location) > 2:
                            section.location = location.strip()

                        instructor_link = row.find('td', 'personName').find('a')
                        if instructor_link:
                            instructor_link = instructor_link["href"]
                            match = re.search('person_(\w+)_.*',
                                              instructor_link.strip())
                            if match:
                                alias = match.group(1)
                                instructor = self.get_instructor(alias)
                                if instructor:
                                    section.instructor = instructor

                        counts = row.find_all('td', 'count')

                        for i in xrange(len(counts)):
                            count = counts[i].string
                            count = self.to_ascii(count)

                            if i == 0 and len(count) > 1:
                                section.location_capacity = int(count)
                            elif i == 1 and len(count) > 1:
                                section.enrollment_cap = int(count)
                            elif i == 2 and len(count) > 1:
                                section.enrolled = int(count)
                            elif i == 3 and len(count) > 1:
                                section.waitlisted = int(count)
                            elif i == 4 and len(count) > 1:
                                section.dropped = int(count)

                        section.term = term
                        section.save()

        return

    def populate_instructor_info(self):


        to_visit = []

        for relative_term in self.relative_terms:
            schedules_url = 'http://schedules.calpoly.edu/index_'
            schedules_url = schedules_url + relative_term + ".htm"

            soup = BeautifulSoup(
                self.get_url_content(schedules_url))

            for link in soup.find_all(href=re.compile("all_person")):
                to_visit.append(link['href'])

        count = 0
        for link in to_visit:
            out = str(count) + "/" + str(len(to_visit))
            print out
            self.log_population(out)
            count += 1

            soup = BeautifulSoup(
                self.get_url_content(self.schedules_url + '/' + link))
            rows = soup.find('table').find_all('tr')
            for row in rows:
                name = row.find('td', 'personName')
                if name:
                    instructor = Instructor()

                    full_name = name.a.string if name.a else name.string

                    instructor.full_name = self.to_ascii(full_name)
                    alias = row.find('td', 'personAlias')
                    if alias:
                        alias_temp = alias.a.string if alias.a else alias.string
                        instructor.alias = self.to_ascii(alias_temp)
                        other = Instructor.objects.filter(
                            alias__iexact=instructor.alias)
                        if other.count() > 0:
                            continue
                    phone = row.find('td', 'personPhone')
                    if phone:
                        instructor.phone = self.to_ascii(phone.string)

                        if instructor.phone:
                            instructor.phone = instructor.phone.replace('/', '-')

                    location = row.find('td', 'personLocation')
                    if location:
                        instructor.location = self.to_ascii(location.string)

                    name = instructor.full_name
                    first_last_split = name.rfind(',')
                    instructor.last = name[:first_last_split].strip()
                    instructor.first_extended = name[first_last_split:].replace(
                        ', ', '').strip()

                    instructor.first = re.sub(r'\s[A-Z]\.$', '',
                                              instructor.first_extended)
                    if instructor.first == instructor.first_extended:
                        instructor.first = re.sub(r'\s\w+$', '',
                                                  instructor.first_extended)

                    instructor.save()

        return

    def refresh_extended_data(self):
        Prerequisite.objects.all().delete()
        Recommended.objects.all().delete()
        Corequisite.objects.all().delete()
        Concurrent.objects.all().delete()
        Crosslisting.objects.all().delete()
        out = 'Deleted Prerequisites, Recommended, Corequisites, Concurrents, ' \
              '' \
              '' \
              'and Crosslistings...'
        print out
        self.log_population(out)
        self.populate_extended_data()

    def populate_polyratings_info(self):
        soup = BeautifulSoup(
            self.get_url_content("http://polyratings.com/list.phtml"))

        tables = soup.find_all('table')

        print soup.prettify()

        rows = tables[1].find_all('tr')
        to_visit = []
        for row in rows[1:]:
            to_visit.append(row.find('a').get('href'))

        count = 0
        for link in to_visit:
            out = str(count) + "/" + str(len(to_visit))
            print out
            self.log_population(out)
            count += 1
            soup = BeautifulSoup(self.get_url_content(link))

            title = soup.find('font', 'title')
            if not title:
                continue
            full_name = self.to_ascii(title.contents[0]).strip()

            if full_name:
                instructor = PolyratingsInstructor()
                instructor.full_name = full_name

                d = dict(urlparse.parse_qsl(link.split('?')[1]))
                profid = int(d['profid'].strip())
                instructor.prof_id = profid

                first_last_split = full_name.rfind(',')
                instructor.last = full_name[:first_last_split].strip()
                instructor.first = full_name[first_last_split:].replace(', ',
                                                                        '').strip()

                ratings = soup.find_all('font', re.compile("txt$"))

                pattern = 'Cumulative GPA: (\d+\.\d+)/4.00 with (\d+) evaluations?'
                match = re.search(pattern, ratings[0].string)
                if match:
                    instructor.overall = float(match.group(1))
                    instructor.rating_count = int(match.group(2))
                pattern = 'Presents Material Clearly: (\d+\.\d+)'
                match = re.search(pattern, ratings[1].string)
                if match:
                    instructor.presentation = float(match.group(1))
                pattern = 'Recognizes Student Difficulties: (\d+\.\d+)'
                match = re.search(pattern, ratings[2].string)
                if match:
                    instructor.understanding = float(match.group(1))

                real_instructors = Instructor.objects.filter(
                    last__iexact=instructor.last,
                    first__iexact=instructor.first)

                if real_instructors.count() >= 1:
                    instructor.instructor = real_instructors[0]

                if not instructor.instructor:
                    matches = Instructor.objects.filter(
                        last__icontains=instructor.last,
                        first__icontains=instructor.first)
                    if matches.count() >= 1:
                        instructor.instructor = matches[0]
                    else:
                        matches = Instructor.objects.filter(
                            first__icontains=instructor.last,
                            last__icontains=instructor.first)
                        if matches.count() == 1:
                            instructor.instructor = matches[0]

                if not instructor.instructor:
                    real_instructors = Instructor.objects.filter(
                        last__iexact=instructor.last, first__icontains=instructor.first)
                    if real_instructors.count() == 1:
                        instructor.instructor = real_instructors[0]
                    else:
                        # multiple matches on a last name, but no matches on first name
                        pass

                if instructor.instructor:
                    out = "Polyratings instructor " + instructor.instructor.first + " " + instructor.instructor.last + " linked to official instructor" + instructor.first + " " + instructor.last
                    print out
                    self.log_population(out)
                instructor.save()

                # print link.encode('ascii', 'ignore')
                # print soup.encode('ascii', 'ignore')
                soup_table = soup.find('table', 'text')
                if soup_table:
                    rows = soup_table.find_all('tr')

                    for row in rows:
                        if len(row.find_all('td')) < 3:
                            continue

                        rating = Polyrating()

                        tds = row.find_all('td')

                        rating.comments = tds[2].string
                        rating.comments = rating.comments.replace('  ', ' ')

                        info = list(tds[0].strings)
                        info = map(lambda x: x.strip(), info)
                        info = filter(None, info)

                        course_string = info[0].strip().split(' ')
                        standing_string = info[1]
                        grade_string = info[3]
                        timestamp_string = info[5]

                        rating.date = datetime.strptime(timestamp_string,
                                                        "%I:%M %p, %b %d, %Y")

                        if standing_string == 'Freshman':
                            rating.standing = models.Standing.FRESHMAN
                        elif standing_string == 'Sophomore':
                            rating.standing = models.Standing.SOPHOMORE
                        elif standing_string == 'Junior':
                            rating.standing = models.Standing.JUNIOR
                        elif standing_string == 'Senior':
                            rating.standing = models.Standing.SENIOR
                        elif standing_string == '5th Year Senior':
                            rating.standing = models.Standing.FIFTH_YEAR
                        elif standing_string == 'Graduate Student':
                            rating.standing = models.Standing.GRADUATE

                        if grade_string == 'A':
                            rating.grade = models.Grade.A
                        elif grade_string == 'B':
                            rating.grade = models.Grade.B
                        elif grade_string == 'C':
                            rating.grade = models.Grade.C
                        elif grade_string == 'D':
                            rating.grade = models.Grade.D
                        elif grade_string == 'F':
                            rating.grade = models.Grade.F
                        elif grade_string == 'Credit':
                            rating.grade = models.Grade.CREDIT
                        elif grade_string == 'No Credit':
                            rating.grade = models.Grade.NO_CREDIT
                        elif grade_string == 'N/A':
                            rating.grade = models.Grade.NOT_AVAILABLE

                        course = self.get_course(course_string[0].strip(),
                                                 int(course_string[1].strip()))

                        # print course_string[0].strip()
                        # print int(course_string[1].strip())

                        if course:
                            if course.polyratings_count:
                                course.polyratings_count += 1
                            else:
                                course.polyratings_count = 1
                            course.save()
                            rating.course = course
                        else:
                            pass
                            # print str.format(
                            # '{0} {1} not found (listed on PolyRatings)',
                            # str(course_string[0]), str(course_string[1]))

                            # TODO: add timestamp

                        rating.instructor = instructor
                        rating.save()


    def get_subject_urls(self):
        toc_url = self.catalog_url + self.toc_location
        parser = BeautifulSoup(self.get_url_content(toc_url))
        links = parser.body.find('div', id='tbl-coursesaz').find_all('a',
                                                                     'sitemaplink')
        to_visit = []
        for link in links:
            to_visit.append(self.catalog_url + link.get('href'))
        return to_visit

    def match_requisite_line(self, each):
        match = re.search(
            '(Recommended|Prerequisites?|Corequisites?|Concurrent):\s+', each,
            re.IGNORECASE)
        return match

    def populate_terms_offered(self, course, each):
        match = re.match('^Terms?\sTypically\sOffered:\s(.*)$', each,
                         re.IGNORECASE)
        if match:
            terms = match.group(1)
            if 'TBD' in terms:
                course.offered_terms_known = False
            else:
                course.offered_terms_known = True
                course.offered_fall = 'F' in terms
                course.offered_winter = 'W' in terms
                course.offered_spring = 'SP' in terms
                course.offered_summer = 'SU' in terms

    def populate_flags(self, course, each):
        match = re.search('USCP', each)
        if match:
            course.uscp = True

        match = re.search('GWR', each)
        if match:
            course.gwr = True

        match = re.search('^CR/NC$', each)
        if match:
            course.credit_no_credit = True

    def make_unset_flags_false(self, course):
        if course.credit_no_credit != True:
            course.credit_no_credit = False
        if course.gwr != True:
            course.gwr = False
        if course.uscp != True:
            course.uscp = False

    def populate_ges(self, course, each):
        match = re.findall('GE Area (\w)(\d)', each)
        for each in match:
            ge_area = GeArea(letter=each[0], number=each[1])

            try:
                ge_area = GeArea.objects.get(letter=ge_area.letter,
                                             number=ge_area.number)
            except GeArea.DoesNotExist:
                ge_area.save()

            course.ge_areas.add(ge_area)

    def populate_extended_info(self, course, course_block):
        extended_info = course_block.find('div',
                                          'courseextendedwrap')

        extended_info = extended_info.find_all('p')
        extended_infos = []

        for each in extended_info:
            result = ''

            for content in each.contents:
                if content.name == 'a':
                    result += content.string
                else:
                    result += content

            each = re.sub('\s{2,}', ' ', result)
            # print each





            if self.match_requisite_line(each):
                course.requisites = each
            else:
                self.populate_flags(course, each)
                self.populate_ges(course, each)
                self.populate_terms_offered(course, each)
        self.make_unset_flags_false(course)

    def populate_description(self, course, course_block):
        description = \
            course_block.find('div', 'courseblockdesc').p

        result = ''

        for content in description.contents:
            if content.name == 'a':
                result += content.string
            else:
                result += content

        result = re.sub('\s{2,}', ' ', result)

        course.description = result

    def populate_units(self, course, course_block):
        units = course_block.find('span', 'courseblockhours').string.strip()

        match = re.match('^(\d+(?P<decimal>\.\d+)?)(-(\d+))?\sunits?$', units)

        if match and not match.group('decimal'):
            course.min_units = int(match.group(1))
        if match.group(4):
            course.max_units = int(match.group(4))
        else:
            course.max_units = course.min_units

    def populate_title_and_number(self, course, course_block):
        title_info = course_block.select('.courseblocktitle')[0].find_all('strong')[0].contents[0]

        # TODO: figure out why I have to string.replace() the
        # non-breaking
        # space here AND in get_url_content()
        title_info = title_info.replace(u'\u00a0', ' ')
        title_info = title_info.replace(u'\u00a0', ' ')


        match = re.match('^\w{2,4}\s(\d+)\.?\s+(.*)\.$', title_info)
        if match:
            course.number = int(match.group(1))
            course.title = match.group(2)
            return True
        else:
            return False

    def populate_basic_info(self, course, course_block, subject):
        course.subject = subject
        if self.populate_title_and_number(course, course_block) == False:
            return False

        self.populate_units(course, course_block.select('.courseblocktitle')[0])
        self.populate_description(course, course_block)

    def make_subject(self, parser):
        subject_heading = parser.find('h1').string.strip()
        match = re.match('^(.+)\s\((.+)\)$', subject_heading)
        subject = Subject(title=match.group(1), code=match.group(2))
        return subject

    def populate_basic_course_info(self, parser, subject):
        course_blocks = parser.find_all('div', 'courseblock')
        for course_block in course_blocks:
            course = Course()
            if self.populate_basic_info(course, course_block, subject) == False:
                continue
            course.save()
            self.populate_extended_info(course, course_block)
            course.save()

    def populate_initial_data(self, subject_urls):

        i = 0
        for url in subject_urls:
            parser = BeautifulSoup(self.get_url_content(url))

            subject = self.make_subject(parser)
            subject.save()

            self.populate_basic_course_info(parser, subject)

            out = str(subject) + ' completed ' + str(i) + 'out of' + str(
                len(subject_urls))
            print out
            self.log_population(out)
            i += 1

            if self.SMALL_COURSE_SET and i >= 2:
                out = 'Stopping after ' + str(
                    i) + ' subjects for brevity (SMALL_COURSE_SET flag set).'
                print out
                self.log_population(out)
                break

    def populate_requisite_section_courses(self, course, course_tuples,
                                           requisite_model):
        for subject, number in course_tuples:
            other_course = self.get_course(subject, number)
            if other_course:
                req = requisite_model()
                req.containing_course = course
                req.other_course = other_course
                req.save()
            else:
                if not self.SMALL_COURSE_SET:
                    out = str.format('{0} {1} not found ({2} for {3})',
                                     str(subject), str(number),
                                     requisite_model.__name__, str(course))
                    print out
                    self.log_population(out)

    def populate_requisites(self, course, add_relations=True):
        if course.requisites:
            for requisite_section in course.requisites.split('.'):
                requisite_section = requisite_section.strip().replace(unichr(160), " ")

                module = importlib.import_module('cparse.models')
                requisite_model = None

                if requisite_section.startswith('Prerequisite'):
                    course.prerequisites_description = requisite_section.replace(
                        'Prerequisite: ', '')
                    requisite_model = getattr(module, 'Prerequisite')
                elif requisite_section.startswith('Corequisite'):
                    course.corequisites_description = requisite_section.replace(
                        'Corequisite: ', '')
                    requisite_model = getattr(module, 'Corequisite')
                elif requisite_section.startswith('Concurrent'):
                    course.concurrent_description = requisite_section.replace(
                        'Concurrent: ', '')
                    requisite_model = getattr(module, 'Concurrent')
                elif requisite_section.startswith('Recommended'):
                    course.recommended_description = requisite_section.replace(
                        'Recommended: ', '')
                    requisite_model = getattr(module, 'Recommended')

                if not add_relations:
                    continue

                # print requisite_section

                matches = re.finditer(
                    '[A-Z]{2,4}(\s?(and|or|&|/)\s?[A-Z]{2,4})*\s\d{3}(\s?(and|or|&|/)\s?\d{3})*', requisite_section)

                # print matches
                # print course
                # print requisite_model

                if matches:
                    # print matches
                    for match in matches:
                        # print match
                        # print match.group(0)
                        # cross product of subjects and numbers
                        # e.g. [CPE, CSC] x [101, 102] -> [(CPE, 101), (CSC,
                        # 101),
                        # (CPE, 102), (CSC, 102)]
                        subjects = re.findall('[A-Z]{2,4}', match.group(0))
                        numbers = re.findall('\d{3}', match.group(0))
                        course_tuples = list(
                            itertools.product(subjects, numbers))

                        # print 'Tuples: '
                        # for each in course_tuples:
                        # print each

                        # I'm proud of this
                        if requisite_model:
                            self.populate_requisite_section_courses(course,
                                                                    course_tuples,
                                                                    requisite_model)

                            # match = re.search('(
                            # freshman|sophomore|junior|senior|graduate|first
                            # |second|third|fourth|fifth)[\s|-](
                            # standing|year)', course
                            # .requisites, re.IGNORECASE)

                            # match = re.search(
                            # 'FORMERLY',
                            # section)

                            # match = re.search(
                            # '[A-Z]{2,4}\s(students?|majors?)',
                            # course.requisites)

                            # print ''

            course.save()


    def populate_extended_data(self):
        i = 0
        for course in Course.objects.all():
            self.populate_requisites(course)
            self.populate_crosslists(course)
            i += 1
            if i % 10 == 0:
                out = str(i) + ' of ' + str(
                    len(Course.objects.all())) + ' completed...'
                print out
                self.log_population(out)

    def refresh_initial_data(self):
        Subject.objects.all().delete()
        Course.objects.all().delete()
        GeArea.objects.all().delete()
        out = 'Deleted Subjects, Courses, and GeAreas...'
        print out
        self.log_population(out)
        self.populate_initial_data(self.get_subject_urls())

    def get_course(self, subject, number):
        try:
            course = Course.objects.get(subject__code=subject, number=number)
        except Course.DoesNotExist:
            course = None

        return course

    def get_url_content(self, url):
        out = "Retrieved: " + url
        print out
        self.log_population(out)

        hdr = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding': 'none',
            'Accept-Language': 'en-US,en;q=0.8',
            'Connection': 'keep-alive'}

        try:
            req = urllib2.Request(url, headers=hdr)
            value = urllib2.urlopen(req).read()

        except urllib2.HTTPError, e:
            print e.fp.read()
            raise e

        # value = page.read()

        return value

    def to_ascii(self, text):
        import unicodedata

        if not text:
            return None
        # text.replace(u'\xa0', ' ')

        value = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore')
        return value

    def populate_crosslists(self, course):

        course.description = course.description.replace(u'\xa0', u' ')

        match = re.search('Crosslisted as (.*)\.', course.description)

        if not match:
            return

        matches = re.finditer(
            '[A-Z]{2,4}(\s?(and|or|&|/)\s?[A-Z]{2,4})*\s\d{3}('
            '\s?(and|or|&|/)\s?\d{3})*', match.group(1))

        if matches:
            for match in matches:
                # cross product of subjects and numbers
                # e.g. [CPE, CSC] x [101, 102] -> [(CPE, 101), (CSC,
                # 101),
                # (CPE, 102), (CSC, 102)]

                subjects = re.findall('[A-Z]{2,4}', match.group(0))
                numbers = re.findall('\d{3}', match.group(0))

                course_tuples = list(
                    itertools.product(subjects, numbers))

                for course_tuple in course_tuples:
                    result = Course.objects.filter(subject__code=course_tuple[0], number=course_tuple[1])
                    if result.count() == 1:
                        c = result[0]
                    else:
                        continue

                    if c != course:
                        crosslist = Crosslisting()
                        crosslist.containing_course = course
                        crosslist.other_course = c
                        crosslist.save()

        return

    def get_instructor(self, alias):
        result = Instructor.objects.filter(alias__iexact=alias)
        if result:
            return result[0]
        else:
            return None

    def get_term(self, quarter, year, start, end):
        term = Term.objects.filter(quarter=quarter, year=year)

        if term.count() > 0:
            return term[0]
        else:
            term = Term()
            term.quarter = quarter
            term.year = year
            term.start = start
            term.end = end
            term.save()
            return term

    def quarter_string_to_enum(self, quarter):
        if quarter.lower() == "fall":
            return Quarter.FALL
        elif quarter.lower() == "winter":
            return Quarter.WINTER
        elif quarter.lower() == "spring":
            return Quarter.SPRING
        elif quarter.lower() == "summer":
            return Quarter.SUMMER

        return None

    def to_unicode_or_bust(o, encoding='utf-8'):
        if isinstance(o, basestring):
            if not isinstance(o, unicode):
                obj = unicode(o, encoding)

        return obj