import json
import logging
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import get_user_model
from chat.models import Chat

logger = logging.getLogger(__name__)

INITIAL_PAGE_SIZE = 10

@login_required(login_url='/user/login')
def chat_view(request):
    if request.method == 'GET':
        queryset = request.user.chats.all()
        paginator = Paginator(queryset, INITIAL_PAGE_SIZE)

        current_page = paginator.page(1)
        serialized_chats = [{'name': chat.name} for chat in current_page]
        serialized_user = {
            'username': request.user.username,
        }
        
        return render(request, 'chat/index.html', {'chats': serialized_chats, 'user': serialized_user})

@login_required(login_url='/user/login')
def leave_chat_view(request, id):
    if request.method == 'POST':
        try:
            queryset = request.user.chats.get(id=id)
        except:
            logger.warning()

@login_required(login_url='/user/login')
def create_chat_view(request):
    if request.method == 'POST':
        pass


@login_required(login_url='/user/login')
def delete_chat_view(request):
    if request.method == 'POST':
        pass


@login_required(login_url='/user/login')
def update_chat_view(request):
    if request.method == 'POST':
        pass

@login_required(login_url='/user/login')
def create_contact_view(request):
    if request.method == 'POST':
        pass

@login_required(login_url='/user/login')
def leave_chat_view(request, id):
    if request.method == 'POST':
        try:
            queryset = request.user.chats.get(id=id)
        except:
            logger.warning()

@login_required(login_url='/user/login')
def load_chat_view(request):
    if request.method == 'GET':
        try:
            body = json.loads(request.body.decode('utf-8'))

            if 'page' not in body or 'page_size' not in body:
                return JsonResponse(
                    {
                        'type': 'bad_request', 
                        'message': 'Expected page or page_size in body',
                    },
                    status=400,
                )

            queryset = request.user.chats.all()
            paginator = Paginator(queryset, body['page_size'])

            try:
                current_page = paginator.page(body['page'])
                serialized_chats = [{'name': chat.name} for chat in current_page]

                return JsonResponse(
                    {
                        'type': 'ok',
                        'content': serialized_chats
                    }
                )
            except (EmptyPage, PageNotAnInteger) as err:
                logger.warning(f'An warning ocurred: {err}')
                return JsonResponse(
                    {
                        'type': 'bad_request',
                        'message': f'Invalid body request: {err}'
                    }
                )

        except json.JSONDecodeError as err:
            logger.warning(f'An warning ocurred: {err}')
            return JsonResponse(
                {
                    'type': 'bad_request',
                    'message': f'Invalid JSON in request body: {err}'
                },
                status=400
            )
