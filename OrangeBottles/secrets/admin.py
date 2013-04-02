from secrets.models import Person, Blackmail, Term
from django.contrib import admin

admin.site.register(Person)
admin.site.register(Term)
#admin.site.register(Blackmail)

class TermInline(admin.StackedInline):
    model = Term
    extra = 3

class BlackmailAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Related People',          {'fields': ['target','owner']}),
        ('Evidence',                {'fields': ['picture']}),
        (None,                      {'fields': ['demands']}),
        ('date time info',          {'fields': ['deadline', 'timecreated']}),
    ]
    inlines = [TermInline]
    
admin.site.register(Blackmail, BlackmailAdmin)
    
