from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.template import RequestContext
from secrets.models import Person, Blackmail

# Create your views here.

def index(request):
    r = HttpResponse()
    loggedin = request.session.get('loggedin', False)
    if(loggedin):
        r.write("logged in, yay!")
    else:
        r.write("NOT logged in, boo...")        
    r.write("index page")
    return r
    
def details(request):
    return HttpResponse("details page")
    
def edit(request):
    return HttpResponse("editing page")
    
def create(request):
    return HttpResponse("create blackmail page")
    
def signin(request):
    #set session to expire in 15 mins
    request.session.set_expiry(900)
    request.session['loggedin'] = True
    return HttpResponse("login page")
    
def signup(request):
    return HttpResponse("sign up page")



#Helper Functions
def isLoggedIn(request):
    loggedin = request.session.get('loggedin', False)
    if(loggedin):
        return True
    else:
        return False 
        
        
        
        
        
        
        
        
        
        
    
