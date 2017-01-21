from django.core.management.base import BaseCommand

from cparse import views
from cparse.management.commands import populate
from cparse.models import Course, ReportedIssue, Instructor


class Command(BaseCommand):
    def handle(self, *args, **options):

        print views.number_of_students(Course.objects.get(subject__code='CPE', number=101))
        return

        for each in Course.objects.get(subject__code='CPE', number=344).section_set.all():
            print each.days

        return
        ReportedIssue.objects.all().delete()
        return

        print views.week_num()
        return

        z = Instructor.objects.get(alias="zwood")
        print views.incorrect_polyratings(z)
        return



        for each in ReportedIssue.objects.all():
            print each.url

        return

        courses = Course.objects.all().order_by('?')[:10]

        cmd = populate.Command()

        for c in courses:
            cmd.populate_crosslists(c)
            print c

            for l in c.crosslistings.all():
                print '   ', l


