from secrets.models import Person, Blackmail, Term
from django.contrib import admin

admin.site.register(Person)
admin.site.register(Term)

class TermInline(admin.StackedInline):
    model = Term
    extra = 3

class BlackmailAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Related People',          {'fields': ['target','owner']}),
        ('Evidence',                {'fields': ['picture']}),
        ('date time info',          {'fields': ['deadline', 'timecreated']}),
    ]
    inlines = [TermInline]
    
admin.site.register(Blackmail, BlackmailAdmin)
    
