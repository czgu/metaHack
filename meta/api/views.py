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
        'pear'
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

            auth = ('acc_2569f28daa2ca36', '5f3d54692a4dcdeda460024d50505ecd')
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
    if request.method != 'POST':
        return Http404('wrong method')


