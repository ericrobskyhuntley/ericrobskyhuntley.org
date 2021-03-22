from .models import Person, SiteWideSetting

def main_author(request):
    main_person_id = SiteWideSetting.objects.all()[0].main_person.id
    return {'main_author': Person.objects.filter(id=main_person_id)[0]}