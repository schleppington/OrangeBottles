from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.core.context_processors import csrf
from django.core.mail import EmailMessage
from secrets.models import Person, Blackmail, Term
import datetime
import secretsforms
import hashlib
import os


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
    #If the user is not logged in, need to have them do so.
    if not isLoggedIn(request):
        return redirect('/secrets/signin/')
    
    c = {}
    bm = get_object_or_404(Blackmail, pk=bm_id)
    
    
    
    
    lstTerms = Term.objects.filter(blackmail=bm)
    
    basepath, filename = os.path.split(str(bm.picture))
    
    c['bm'] = bm
    c['terms'] = list(lstTerms)
    c['imgpath'] = filename
    return render_to_response('secrets/details.html', c)
    

def edit(request, bm_id):
    #If the user is not logged in, need to have them do so.
    if not isLoggedIn(request):
        return redirect('/secrets/signin/')

    b = Blackmail.objects.get(pk=bm_id)
    p = Person.objects.get(email=request.session['useremail'])

    #Make sure user has the proper credentials to edit, before letting
    #them see the options/data.
    if (b.owner.pk != p.pk):
        return redirect('/secrets/details/%s/' %b.pk)
    if request.method == 'POST':
        #must create edit form
        form = secretsforms.createEditForm(request.POST)
        if form.is_valid():
            print "edit blackmail"
    
    else:
        form = secretsforms.createEditForm()
        c = {}
        c.update(csrf(request))
        c['form'] = form
        return render_to_response('secrets/edit/%s/' %bm_id, c)

    return HttpResponse("editing page")
    

def create(request):
    #If the user is not logged in, need to have them do so.
    if not isLoggedIn(request):
        return redirect('/secrets/signin/')

    if request.method == 'POST':
        form = secretsforms.createBlackmailForm(request.POST, request.FILES)
        if form.is_valid():
            #must get target and owner objects before calling createBlackmail.
            o = Person.objects.get(email=request.session['useremail'])
            tEMail = form.cleaned_data['target']
            #See if the current target is found in the database.
            try:
                t = Person.objects.get(email=tEMail)
            except Person.DoesNotExist:
                createUserAccount(request, 'TARGET', tEMail, 'CHANGEME', 'CHANGEME', True)
                t = Person.objects.get(email=tEMail)

            #An owner cannot have multiple ACTIVE blackmails out on the same
            #target. If attempted, notify user they are already blackmailing that
            #target, then redirect to Edit page.
            try:
                blackmail = Blackmail.objects.get(target__id=t.pk, owner__id=o.pk)
                if blackmail:
                     return redirect('/secrets/edit/%s/' %blackmail.pk)
            except Blackmail.DoesNotExist:
                createBlackmail(request, t, o, 
                                                 request.FILES['picture'],
                                                 form.cleaned_data['deadline'])
                #Get the newly created blackmail object's ID, then redirect to the
                #details page.
                blackmail = Blackmail.objects.get(target__id=t.pk, owner__id=o.pk)
                
                #get demands to go with the blackmail
                t = Term()
                t.blackmail = blackmail
                t.demand = form.cleaned_data['term1']
                t.save()
                
                strterm2 = form.cleaned_data['term2']
                if strterm2:
                    t2 = Term()
                    t.blackmail = blackmail
                    t.demand = strterm2
                    t.save()
                strterm3 = form.cleaned_data['term3']
                if strterm3:
                    t3 = Term()
                    t.blackmail = blackmail
                    t.demand = strterm3
                    t.save()                

            return redirect('/secrets/details/%s/' %blackmail.pk)

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


#createUserAccount - validate credentials and set session variables
#   params:
#       request - current request object
#       userename - name of user
#       useremail - email address of user
#       pw1 - first instance of user's password
#       pw2 - second instance of user's password
#       target - determines whether this is an account being created for
#                a target rather than a user.
#   returns: string
#       "ok" if user account created
#       errorMsg otherwise
def createUserAccount(request, username, useremail, pw1, pw2, target=False):
    #ensure user typed same pw twice
    if pw1 != pw2:
        return "Passwords must match"
    
    #Assume we will be adding a new account to the database.
    newPerson = True
    
    #salt and encrypt pw
    pwsalt = str(datetime.datetime.now())
    saltedpw = pwsalt + pw1
    encpw = hashlib.sha512(saltedpw).hexdigest()

    p_list = Person.objects.all()
    for p in p_list:
        #ensure email is unique
        if p.email == useremail:
            #Account found, make sure it wasn't created as a target account.
            if p.name != 'TARGET':
                return "Account already exists for that email"
            else:
                newPerson = False
                addUser(p, useremail, username, encpw, pwsalt)
                break

    #create and store new Person object
    if newPerson:
        p = Person()
        addUser(p, useremail, username, encpw, pwsalt)
    
    #set session variables and send email to the new user
    if not target:
        request.session['loggedin'] = True
        request.session['useremail'] = useremail
        #sendUserCreatedEmail(useremail)

    return "ok"


def addUser(p, useremail, username, encpw, pwsalt):
    p.email = useremail
    p.name = username
    p.password = encpw
    p.salt = pwsalt
    p.save()


def sendUserCreatedEmail(useremail):
    body = '''
Congradulations on joining OrangeBottles, The #1 new blackmailing website!
We look forward to seeing what others have in store for them...
    '''
    email = EmailMessage('Welcome to OrangeBottles', 'body', to=[useremail])
    email.send()


def sendTargetEmail(useremail):
    body = '''
You are the target of a blackmail! Please visit localhost:8000\sessions\
for more information.
    '''
    email = EmailMessage('Blackmail Target Alert!!!', 'body', to=[useremail])
    email.send()


def createBlackmail(request, target, owner, picture, deadline):
    b = Blackmail()
    b.target = target
    b.owner = owner
    b.picture = picture
    b.deadline = deadline
    b.timecreated = str(datetime.datetime.now())
    b.demandsmet = False
    b.save()
    return b
