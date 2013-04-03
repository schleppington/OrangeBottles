from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.template import RequestContext
from secrets.models import Person, Blackmail
import datetime


def index(request):
    #get all blackmail objects
    bm_list = Blackmail.objects.all().order_by('-deadline')
    now = datetime.datetime.now()
    display_list = []
    dont_display = []
    #get blackmail objects that have an expired deadline
    for bm in bm_list:
        if bm.deadline.replace(tzinfo=None) < now:
            display_list.append(bm)
        else:
            #objects that are still hidden, used to get the next exipration time
            dont_display.insert(0,bm)
    #display bm objects in displaylist
    output = "all items: </br>"
    output += '</br>'.join([str(bm) + " : " + str(bm.deadline) for bm in bm_list])
    output += "</br></br>display list: </br>"
    output += '</br>'.join([str(bm) + " : " + str(bm.deadline) for bm in display_list])
    output += '</br></br>dont display list</br>'
    output += '</br>'.join([str(bm) + " : " + str(bm.deadline) for bm in dont_display])
    output += '</br></br>next object to be revealed</br>'
    output += str(dont_display[0]) + " : " + str(dont_display[0].deadline)

    return HttpResponse(output)
    
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
        
        
        
        
        
        
        
        
        
        
    
