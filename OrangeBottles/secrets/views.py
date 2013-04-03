from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.core.context_processors import csrf
from secrets.models import Person, Blackmail
import datetime
import secretsforms


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
            
    output = ""
    if isLoggedIn(request):
        output += "Current User: " + str(request.session.get('useremail')) + "</br></br>"
    #display bm objects in displaylist
    output += "all items: </br>"
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
    if request.method == 'POST':
        #get form data
        form = secretsforms.loginForm(request.POST)
        if form.is_valid():
            #form is valid
            user = form.cleaned_data['Email']
            pw = form.cleaned_data['Password']
            if checkCreds(request, user, pw):
                #allow user to continue
                return redirect('/secrets/')
            else:
                #invlaid login credentials
                c = {}
                c.update(csrf(request))
                c['formhaserrors'] = True
                c['form'] = form
                return render_to_response('secrets/signin.html', c)  
        else:
            #form is not valid
            c = {}
            c.update(csrf(request))
            c['form'] = form
            return render_to_response('secrets/signin.html', c)
    else:
        form = secretsforms.loginForm()
        c = {}
        c.update(csrf(request))
        c['form'] = form
        return render_to_response('secrets/signin.html', c)
    
def signup(request):
    return HttpResponse("sign up page")



#Helper Functions
def isLoggedIn(request):
    loggedin = request.session.get('loggedin', False)
    if(loggedin):
        return True
    else:
        return False 
        
#checkCreds - validate credentials and set session variables
#   params:
#       request - current request object
#       user - email address of user
#       pw - password of user
#   returns:
#       True if credetials are valid
#       False if otherwise
def checkCreds(request, user, pw):
    #do checking here
    
    allowContinue = True  #For debugging
    #allowContinue = False #For debugging    
    
    if(allowContinue):
        request.session['loggedin'] = True
        request.session['useremail'] = user
        return True
    else:
        return False
        
        
        
        
        
        
        
        
        
        
    
