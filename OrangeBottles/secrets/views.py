from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.core.context_processors import csrf
from django.core.mail import EmailMessage
from secrets.models import Person, Blackmail
import datetime
import secretsforms
import hashlib


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
    #gets the current user thats logged in (if user is logged in)
    if isLoggedIn(request):
        output += "Current User: " + str(request.session.get('useremail','')) + "</br></br>"
    #display bm objects in displaylist
    output += "all items: </br>"
    output += '</br>'.join([str(bm) + " : " + str(bm.deadline) for bm in bm_list])
    output += "</br></br>display list: </br>"
    output += '</br>'.join([str(bm) + " : " + str(bm.deadline) for bm in display_list])
    output += '</br></br>dont display list</br>'
    output += '</br>'.join([str(bm) + " : " + str(bm.deadline) for bm in dont_display])
    
    outputDict = {}
    
    if dont_display.count > 0:
        output += '</br></br>next object to be revealed</br>'
        output += str(dont_display[0]) + " : " + str(dont_display[0].deadline)
        nextbm = dont_display[0]
        timetoreveal = nextbm.deadline.replace(tzinfo=None) - now
        output += "</br>in: " + str(timetoreveal)
        days = timetoreveal.days
        secs = timetoreveal.seconds
        hours = int((secs / (3600)))
        secs = secs - (hours * 3600)
        mins = int(secs / 60)
        secs = secs - mins * 60
        
        #used for countdown in template
        outputDict['countdown_days'] = days
        outputDict['countdown_hours'] = hours
        outputDict['countdown_mins'] = mins
        outputDict['countdown_secs'] = secs
        output += "</br>" + str(days) + " : " + str(hours) + " : " + str(mins) + " : " + str(secs)
            
    outputDict['display_list'] = display_list
    return HttpResponse(output)
    
def details(request, bm_id):
    #no post method, everything happens in the response.
    #This will probably just be a templating thing?
    return HttpResponse("details page")
    
def edit(request, bm_id):
    if request.method == 'POST':
        #must create edit form
        if form.is_valid():
            print "edit blackmail"
    return HttpResponse("editing page")
    
def create(request):
    if request.method == 'POST':
        form = secretsforms.createBlackmailForm(request.POST)
        if form.is_valid():
            #If the user is not logged in, need to have them do so.
            if not isLoggedIn(request):
                #CHECK: Should this be a return statement instead?
                redirect('/secrets/signin/')

            #must get target and owner before calling createBlackmail. 
                #Owner should be known if the user creating the blackmail is
                #logged in. If the user is not logged in, they would have been
                #redirected to the signin page.

                #CHECK: Should the target info be a valid user or just an
                #email?
            createBlackmail(request, target, owner, 
                            form.cleaned_data['picture'],
                            form.cleaned_data['deadline'],
                            form.cleaned_data['demands'])
            #if the blackmail was created, should redirect to details page with
            #blackmail
                # TODO ^ : Search database for bm_id; if found, redirect
                    #CHECK: Can an owner have multiple ACTIVE blackmails out on
                    #the same target?
                    # If so,
                        #need to create a method to get the ID of the currently
                        #selected record. (In this case, the current record would
                        #be the newly created record; perhaps the createBlackmail
                        #function should return the new record's ID).
                    # If not,
                        #need to make sure the user knows they are already
                        #blackmailing that target. Redirect to Edit page?
            return redirect('/secrets/create.html/(?P<bm_id>\d+)/')
        else:
            c = {}
            c.update(csrf(request))
            c['formhaserrors'] = True
            c['form'] = form
            return render_to_response('secrets/create.html', c)
    else:
        form = secretsforms.createBlackmailForm()
        c = {}
        c.update(csrf(request))
        c['form'] = form
        return render_to_response('secrets/create.html', c)

    return HttpResponse("create bm page")
    
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
    if request.method == 'POST':
        #get form data
        form = secretsforms.createUserForm(request.POST)
        if form.is_valid():
            #form is valid
            username = form.cleaned_data['Name']
            useremail = form.cleaned_data['Email']
            pw1 = form.cleaned_data['Password']
            pw2 = form.cleaned_data['RePassword']
            result = createUserAccount(request, username, useremail, pw1, pw2)
            if result == 'ok':
                #allow user to continue
                return redirect('/secrets/')
            else:
                #invlaid login credentials
                c = {}
                c.update(csrf(request))
                c['formhaserrors'] = True
                c['strError'] = result
                c['form'] = form
                return render_to_response('secrets/createPersonForm.html', c)  
        else:
            #form is not valid
            c = {}
            c.update(csrf(request))
            c['form'] = form
            return render_to_response('secrets/createPersonForm.html', c)  
    else:
        form = secretsforms.createUserForm()
        c = {}
        c.update(csrf(request))
        c['form'] = form
        return render_to_response('secrets/createPersonForm.html', c)



#Helper Functions ******************************************************


#isLoggedIn - checks to see if there a current user logged in
#   params:
#       request - current request object
#   returns: boolean
#       True if there is a user currently logged in
#       False otherwise
def isLoggedIn(request):
    loggedin = request.session.get('loggedin', False)
    return loggedin
        
#checkCreds - validate credentials and set session variables
#   params:
#       request - current request object
#       user - email address of user
#       pw - password of user
#   returns: boolean
#       True if credetials are valid
#       False if otherwise
def checkCreds(request, useremail, pw):
    
    try:
        p = Person.objects.get(email=useremail)
    except:
        return False
    
    encpw = hashlib.sha512(p.salt + pw).hexdigest()
    if p.password == encpw:
        request.session['loggedin'] = True
        request.session['useremail'] = useremail
        return True
    else:
        return False
        
#checkCreds - validate credentials and set session variables
#   params:
#       request - current request object
#       userename - name of user
#       useremail - email address of user
#       pw1 - first instance of user's password
#       pw2 - second instance of user's password
#   returns: string
#       "ok" if user account created
#       errorMsg otherwise
def createUserAccount(request, username, useremail, pw1, pw2):
    #ensure user typed same pw twice
    if pw1 != pw2:
        return "Passwords must match"
    
    p_list = Person.objects.all()
    for p in p_list:
        #ensure email is unique
        if p.email == useremail:
            return "Account already exists for that email"
    
    #salt and encrypt pw
    pwsalt = str(datetime.datetime.now())
    saltedpw = pwsalt + pw1
    encpw = hashlib.sha512(saltedpw).hexdigest()
    
    #create and store new Person object
    p = Person()
    p.name = username
    p.email = useremail
    p.password = encpw
    p.salt = pwsalt
    p.save()
    
    #send email to the new user
    #sendUserCreatedEmail(useremail)
    
    #set session variables
    request.session['loggedin'] = True
    request.session['useremail'] = useremail
    return "ok"
        
        
        
def sendUserCreatedEmail(useremail):
    body = '''
Congradulations on joining OrangeBottles, The #1 new blackmailing website!
We look forward to seeing what others have in store for them...
    '''
    email = EmailMessage('Welcome to OrangeBottles', 'body', to=[useremail])
    email.send()

def createBlackmail(request, target, owner, picture, deadline, demands):
    b = Blackmail()
    b.target = target
    b.owner = owner
    b.picture = picture
    b.deadline = deadline
    b.timecreated = str(datetime.datetime.now())
    b.demandsmet = False
    
    t = Term()
    t.blackmail = b
    t.demand = demands

    b.save()
    t.save()
