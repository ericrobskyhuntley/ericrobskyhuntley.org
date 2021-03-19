from .models import Person

def main_author(request):
    return {'main_author': Person.objects.filter(affiliation__primary=True)[0]}