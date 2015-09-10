from django.conf.urls import patterns, url
from django.shortcuts import render
from django.http import Http404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.sites.shortcuts import get_current_site

import requests

from .forms import UploadImageForm
from .models import Picture


# Create your views here.
@csrf_exempt
def image_handler(request):

    possibe_food = set([
        'apple',
        'banana',
        'carrot',
        'broccoli',
        'pear',
        'watermelon'
    ])

    if request.method != 'POST':
        raise Http404('wrong method')
    else:
        form = UploadImageForm(request.POST, request.FILES)
        current_site = get_current_site(request)
        print current_site
        if form.is_valid():
            newpic = Picture(image=request.FILES['image'])
            newpic.save()

            auth = ('some_account', 'some_key')
            image_path = \
                'http://' + str(current_site) + '/media/' + str(newpic.image.name)
            r_url = 'https://api.imagga.com/v1/tagging?url=' + image_path

            r = requests.get(r_url, auth=auth)
            if r.status_code < 400:
                data = r.json()
                print data
                foods = data['results'][0]['tags']
                for food in foods:
                    if food['tag'] in possibe_food:
                        return JsonResponse({'food': food['tag']})

                return JsonResponse({'food': foods[0]['tag']})
            else:
                raise Http404('Imagga error occured')

    raise Http404('Unknown error occured')


def recipe_handler(request):
    if request.method != 'GET':
        return Http404('wrong method')
    query = request.GET['id']

    if query:
        r_url = 'http://api.bigoven.com/recipe/%s?api_key=some_api_key' % str(query)
        r = requests.get(r_url, headers={"Accept": "application/json"})

        if r.status_code < 400:
            recipe = r.json()

            processed_results = {}

            if 'Instructions' not in recipe:
                return JsonResponse({'error': 'Instructions not found'})
            else:
                instruction = recipe['Instructions'].replace('\n', ' ').replace('\r', '')
                instructions = instruction.split('.')
                instructions = map(
                    lambda sentence: sentence.strip(),
                    instructions
                )
                instructions = filter(
                    lambda s: not s.isspace() and s,
                    instructions
                )
                processed_results['Instructions'] = instructions
                processed_results['Ingredient'] = map(
                    lambda ingredient: ingredient['Name'],
                    recipe['Ingredients']
                )
                return JsonResponse(processed_results)
    raise Http404('Unknown error occured')


def list_handler(request):
    if request.method != 'GET':
        return Http404('Wrong method')
    query = request.GET['name']

    if query:
        r_url = 'http://api.bigoven.com/recipes?title_kw=%s&api_key=some_api_key&pg=1&rpp=3' % query
        r = requests.get(r_url, headers={"Accept": "application/json"})

        if r.status_code < 400:
            results = r.json()['Results']

            processed_results = map(
                lambda recipe: {'title': recipe['Title'], 'id': recipe['RecipeID']},
                results
            )

            return JsonResponse({'result': processed_results})

    return Http404('Unknown error occured')

