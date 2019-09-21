from .models import Author

def main_author(request):
    return {'main_author': Author.objects.filter(id=1)[0]}
