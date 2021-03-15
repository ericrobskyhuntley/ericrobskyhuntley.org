from .models import Person

def main_author(request):
    return {'main_author': Person.objects.filter(id=1)[0]}