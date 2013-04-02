from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.template import RequestContext


# Create your views here.

def index(request):
    r = HttpResponse()
    r.write("index page")
    return r
    
def details(request):
    return HttpResponse("details page")
    
def create(request):
    return HttpResponse("create blackmail page")
    
def login(request):
    return HttpResponse("login page")
    
def signup(request):
    return HttpResponse("sign up page")
