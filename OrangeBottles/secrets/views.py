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
import random

# Views ****************************************************************

def index(request):
    
    outputDict = {}
    
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
            
    #gets the current user thats logged in (if user is logged in)
    if isLoggedIn(request):
        curUser = str(request.session.get('username',''))
        outputDict['curuser'] = curUser    
    
    if dont_display.count > 0:
        nextbm = dont_display[0]
        timetoreveal = nextbm.deadline.replace(tzinfo=None) - now
        outputDict['totalseconds'] = int(timetoreveal.total_seconds())
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
            
    outputDict['display_list'] = display_list      
    return render_to_response('secrets/index.html', outputDict)
    

def details(request, bm_id):
    #outputDict contains everything that will be passed to the template
    outputDict = {}
    
    #If the user is not logged in, need to have them do so.
    if not isLoggedIn(request):
        return redirect('/secrets/signin/')
    else:
        curUser = request.session.get('useremail','')
        outputDict['curuser'] = request.session.get('username','')

    bm = get_object_or_404(Blackmail, pk=bm_id)
    
    #ensure that the current user is allowed to view this bm
    now = datetime.datetime.now()
    if bm.target.email != curUser and bm.owner.email != curUser and bm.deadline.replace(tzinfo=None) > now:
        #access denied
        return HttpResponse('Access to this page is denied!',status=401)
    if bm.owner.email == curUser:
        outputDict['allowedit'] = True

    lstTerms = Term.objects.filter(blackmail=bm)
    
    basepath, filename = os.path.split(str(bm.picture))
    
    outputDict['bm'] = bm
    outputDict['terms'] = list(lstTerms)
    outputDict['imgpath'] = filename
    return render_to_response('secrets/details.html', outputDict)
    

def edit(request, bm_id):
    #outputDict contains everything that will be passed to the template
    outputDict = {}
    
    #If the user is not logged in, need to have them do so.
    if not isLoggedIn(request):
        return redirect('/secrets/signin/')
    else:
        curUser = request.session.get('username','')
        outputDict['curuser'] = curUser
        
    b = get_object_or_404(Blackmail, pk=bm_id)
    p = Person.objects.get(email=request.session['useremail'])

    #Get Filename & Path
    basepath, filename = os.path.split(str(b.picture))

    #Get terms stored in database:
    terms = Term.objects.filter(blackmail=b)
    term1 = None    #term1 - term3 are variables to store blackmail
    term2 = None    #        terms already in the database.
    term3 = None

    i = 0           #i is used to keep track of how many terms were
                    #  stored in the database.
    for t in terms:     # this loop is used to retrieve all terms
        if i == 0:      # stored in the queryset "terms"
            term1 = t
        elif i == 1:
            term2 = t
        elif i == 2:
            term3 = t
        i += 1

    #Make sure user has the proper credentials to edit, before letting
    #them see the options/data.
    if (b.owner.pk != p.pk):
        return redirect('/secrets/details/%s/' %b.pk)
    if request.method == 'POST':
        form = secretsforms.createEditForm(request.POST, request.FILES)
        if form.is_valid():
            #Make sure the deadline hasn't already passed before any
            #any info is modified.
            now = datetime.datetime.now()
            if b.deadline.replace(tzinfo=None) > now:
                deadline = form.cleaned_data['deadline']
                
                #Did the user change the deadline?
                if b.deadline != deadline:
                    b.deadline = deadline
                
                #Did the user change the image?
                try:
                    img2 = request.FILES['picture']
                except:
                    img2 = None

                if img2:
                    if filename != img2:
                        b.picture = request.FILES['picture']
                
                #Save changes
                b.save()
                
                #Get the terms from the form.
                t1 = form.cleaned_data['term1']     #t1 - t3 are variables to
                t2 = form.cleaned_data['term2']     #     store new blackmail
                t3 = form.cleaned_data['term3']     #     terms in.

                # the following if conditions are used to determine which terms,
                # if any, were changed.
                if term1.demand != t1:
                    if t1:
                        term1.demand = t1
                        term1.save()
                if term2:       # Was there previously a 2nd term?
                    if term2.demand != t2:
                        if t2:  # Is there a 2nd term in the updated list?
                            term2.demand = t2
                            term2.save()
                        else:   # No 2nd term in updated list, delete original one.
                            term2.delete()
                elif t2:        # There wasn't a 2nd term previously, is there a
                                # 2nd term now?
                    createNewTerm(b, t2)
                if term3:       # Was there previously a 3rd term?
                    if term3.demand != t3:
                        if t3:  # Is there a 3rd term in the updated list?
                            term3.demand = t3
                            term3.save()
                        else:   # No 3rd term in updated list, delete original one.
                            term3.delete()
                elif t3:        # There wasn't a 3rd term previously, is there a
                                # 3rd term now?
                    createNewTerm(b, t3)

        return redirect('/secrets/details/%s/' %b.pk)
    
    else:
        form = secretsforms.createEditForm(initial={'deadline':b.deadline, 'term1':term1.demand, 'term2':term2, 'term3':term3})
        outputDict.update(csrf(request))
        outputDict['bm'] = b        
        outputDict['form'] = form
        outputDict['imgpath'] = filename
        return render_to_response('secrets/edit.html', outputDict)

    return HttpResponse("editing page")
    

def create(request):
    #outputDict contains everything that will be passed to the template
    outputDict = {}
    
    #If the user is not logged in, need to have them do so.
    if not isLoggedIn(request):
        return redirect('/secrets/signin/')
    else:
        curUser = request.session.get('useremail','')
        outputDict['curuser'] = request.session.get('username','')
        
    if request.method == 'POST':
        randpw = ''
        form = secretsforms.createBlackmailForm(request.POST, request.FILES)
        if form.is_valid():
            #Get target and owner objects before calling createBlackmail.
            o = Person.objects.get(email=request.session['useremail'])
            tEMail = form.cleaned_data['target']
            #See if the current target is found in the database.
            try:
                t = Person.objects.get(email=tEMail)
                randpw = 'your current password'
            except Person.DoesNotExist:
                randpw = str(random.randint(100000, 1000000))
                try:
                    tname = form.cleaned_data['tname']
                    if len(tname) is 0:
                        tname = 'TARGET'
                except:
                    tname = 'TARGET'
                createUserAccount(request, tname, tEMail, randpw, randpw, True)
                t = Person.objects.get(email=tEMail)

            #An owner cannot have multiple ACTIVE blackmails out on the same
            #target. If attempted, redirect to Edit page.
            try:
                blackmail = Blackmail.objects.get(target__id=t.pk, owner__id=o.pk)
                if blackmail:
                     return redirect('/secrets/edit/%s/' %blackmail.pk)
            except Blackmail.DoesNotExist:
                createBlackmail(request, t, o, 
                                                 request.FILES['picture'],
                                                 form.cleaned_data['deadline'])
                
                #Get the newly created blackmail object
                blackmail = Blackmail.objects.get(target__id=t.pk, owner__id=o.pk)
                
                #get demands to go with the blackmail
                createNewTerm(blackmail, form.cleaned_data['term1'])
                
                strterm2 = form.cleaned_data['term2']
                if strterm2:
                    createNewTerm(blackmail, strterm2)
                strterm3 = form.cleaned_data['term3']
                if strterm3:
                    createNewTerm(blackmail, strterm3)

            #send target an email
            sendTargetEmail(tEMail, blackmail.pk, randpw)

            #Redirect to details page so user can see newly created blackmail data.
            return redirect('/secrets/details/%s/' %blackmail.pk)

        else:
            outputDict.update(csrf(request))
            outputDict['formhaserrors'] = True
            outputDict['form'] = form
            return render_to_response('secrets/create.html', outputDict)

    else:
        form = secretsforms.createBlackmailForm()
        outputDict.update(csrf(request))
        outputDict['form'] = form
        return render_to_response('secrets/create.html', outputDict)

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


def signout(request):
    if isLoggedIn(request):
        request.session.clear()
        
    return redirect("/secrets/signin")
  

def myaccount(request):
    #outputDict contains everything that will be passed to the template
    outputDict = {}
    
    #If the user is not logged in, need to have them do so.
    if not isLoggedIn(request):
        return redirect('/secrets/signin/')
    else:
        curUser = request.session.get('username','')
        outputDict['curuser'] = curUser
        curEmail = request.session.get('useremail','')
        outputDict['useremail'] = curEmail
        
    p = get_object_or_404(Person, email=curEmail)
    
    bms = Blackmail.objects.filter(owner=p)
    
    outputDict['p'] = p
    outputDict['bm_list'] = bms
    return render_to_response('secrets/myaccount.html', outputDict)
    
    
def editaccount(request):
    #outputDict contains everything that will be passed to the template
    outputDict = {}
    
    #If the user is not logged in, need to have them do so.
    if not isLoggedIn(request):
        return redirect('/secrets/signin/')
    else:
        curUser = request.session.get('username','')
        outputDict['curuser'] = curUser
        curEmail = request.session.get('useremail','')
        outputDict['useremail'] = curEmail
        
    if request.method == 'POST':
        #get form data
        form = secretsforms.editUserForm(request.POST)
        if form.is_valid():
            #form is valid
            username = form.cleaned_data['Name']
            useremail = form.cleaned_data['Email']
            oldpw = form.cleaned_data['oldPassword']
            pw1 = form.cleaned_data['Password']
            pw2 = form.cleaned_data['RePassword']
            
            p = Person.objects.get(email=curEmail)
            p.name = username
            p.email = useremail
            
            if checkCreds(request, curEmail, oldpw):
                if pw1 and pw2:
                    if pw1 == pw2:
                        pwsalt = str(datetime.datetime.now())
                        saltedpw = pwsalt + pw1
                        encpw = hashlib.sha512(saltedpw).hexdigest()
                        p.password = encpw
                        p.salt = pwsalt
                else:
                    outputDict['strError'] = "new passwords must match"
                p.save()
                request.session['useremail'] = p.email
                request.session['username'] = p.name
                outputDict['strError'] = "account updated"
            else:                
                outputDict['strError'] = "invalid old password"  
                
            #display form with msg
            formdata = {'Name': request.session['username'], 'Email':request.session['useremail'] }
            form = secretsforms.editUserForm(initial=formdata)
            outputDict.update(csrf(request))
            outputDict['formhaserrors'] = True      
            outputDict['form'] = form
            return render_to_response('secrets/editaccount.html', outputDict)
            
    else:
        #display form
        formdata = {'Name': curUser, 'Email':outputDict['useremail'] }
        form = secretsforms.editUserForm(initial=formdata)
        outputDict.update(csrf(request))
        
        outputDict['form'] = form
        return render_to_response('secrets/editaccount.html', outputDict)

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
        request.session['username'] = p.name
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
            return "Account already exists for that email"

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


def sendTargetEmail(useremail, bm_pk, userpw):
    body = ''
    body += 'You are the target of a blackmail! Please visit http://localhost:8000/secrets/details/{0}/ '.format(bm_pk)
    body += 'for more information.\n'
    body += 'You may log in using the following info:\n'
    body += 'user name: {0}\n'.format(useremail)
    body += 'password: {0}\n'.format(userpw)
     
    email = EmailMessage('Blackmail Target Alert!!!', body, to=[useremail])
    email.send()

def createNewTerm(bm, demand):
    t = Term()
    t.blackmail = bm
    t.demand = demand
    t.save()

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
