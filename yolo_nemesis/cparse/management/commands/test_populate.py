from django.test import TestCase

from cparse.management.commands.populate import Command
from cparse.models import *


class PopulateTestCase(TestCase):
    def setUp(self):
        cmd = Command()
        # cmd.populate_initial_data(['http://catalog.calpoly.edu/coursesaz/csc/'])
        # cmd.populate_polyratings_info()
        cmd.populate_instructor_info();

    def test_description(self):

        test = 'Basic principles of algorithmic problem solving and programming using methods of top-down design, stepwise refinement and procedural abstraction. Basic control structures, data types, and input/output. Introduction to the software development process: design, implementation, testing and documentation. The syntax and semantics of a modern programming language. Credit not available for students who have taken CSC/CPE 108. 3 lectures, 1 laboratory. Crosslisted as CPE/CSC 101.'

        c = Course.objects.get(subject__code__iexact='CSC', number=101)

        if not c:
            self.fail(
                'CSC 101 not found. Has the Course database been populated?')

        desc = c.description

        desc = desc.replace(u'\xa0', ' ')
        test = test.replace(u'\xa0', ' ')

        self.assertEqual(desc, test, 'Description not populated correctly')