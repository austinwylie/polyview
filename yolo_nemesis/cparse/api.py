__author__ = 'twoods0129'
from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer
from models import Course, Instructor
import jsonpickle
from search import search as s
from django.shortcuts import render

class JSONResponse(HttpResponse):
    """
    An HttpResponse that renders its content into JSON.
    """
    def __init__(self, data, **kwargs):
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(data, **kwargs)

def documentation(request):
    url = 'api/documentation.html'
    context = {}
    return render(request, url, context)

def instructor(request, alias):
    jsonpickle.load_backend('simplejson','dumps','loads',ValueError)
    jsonpickle.set_preferred_backend('simplejson')
    jsonpickle.set_encoder_options('simplejson', ensure_ascii=False)


    include_ratings = request.GET.get('ratings', None)
    try:
        i = Instructor.objects.filter(alias=alias)[0]
    except IndexError:
        i = []

    json = jsonpickle.encode(i, unpicklable=False)
    if include_ratings.lower() == "true":
        try:
            ratings = s.get_polyratings_for_instructor(i)
            json = jsonpickle.encode((i, ratings), unpicklable=False)
        except AttributeError:
            pass

    return JSONResponse(json.replace(u'\xa0', ' '))

def course(request, major=None, number=None):

    jsonpickle.load_backend('simplejson','dumps','loads',ValueError)
    jsonpickle.set_preferred_backend('simplejson')
    jsonpickle.set_encoder_options('simplejson', ensure_ascii=False)

    if number:
        try:
            c = Course.objects.get(subject__code__iexact=major, number=number)
        except Course.DoesNotExist:
            c = []
    else:
        c = list(Course.objects.filter(subject__code__iexact=major))

    json = jsonpickle.encode(c, unpicklable=False)
    return JSONResponse(json.replace(u'\xa0', ' '))

def search(request, query):
    results, flag = s.searchySearch(query)
    jsonpickle.load_backend('simplejson','dumps','loads',ValueError)
    jsonpickle.set_preferred_backend('simplejson')
    jsonpickle.set_encoder_options('simplejson', ensure_ascii=False)

    json = jsonpickle.encode(results, unpicklable=False)
    return JSONResponse(json.replace(u'\xa0', ' '))