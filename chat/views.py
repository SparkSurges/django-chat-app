import json
import logging
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from chat.forms import ChatForm
from user.forms import ContactForm

logger = logging.getLogger(__name__)

INITIAL_PAGE_SIZE = 10

@login_required(login_url='/user/login')
def chat_view(request):
    if request.method == 'GET':
        chat_form = ChatForm()
        queryset = request.user.chats.all()
        paginator = Paginator(queryset, INITIAL_PAGE_SIZE)

        current_page = paginator.page(1)
        serialized_chats = [{'name': chat.name} for chat in current_page]
        serialized_user = {
            'username': request.user.username,
        }
        
        return render(
            request, 
            'chat/index.html', 
            {
                'chats': serialized_chats, 
                'user': serialized_user,
                'chat_form': chat_form
            }
        )

@login_required(login_url='/user/login')
def leave_chat_view(request, id):
    if request.method == 'POST':
        try:
            chat = request.user.chats.get(id=id)
            chat.leave(request.user)
            return redirect('chat-room')
        except Exception as err:
            logger.warning(f'An warning ocurred: {err}')
            messages.error(request, f'Error trying to leave chat: {err}')
            return redirect('chat-room')

@login_required(login_url='/user/login')
def create_chat_view(request):
    if request.method == 'POST':
        chat_form = ChatForm(data=request.POST)

        if chat_form.is_valid():
            chat = chat_form.save(commit=False)
            chat.creator = request.user
            chat.save()
            messages.success(request, 'New chat successfully created.')
            return redirect('chat-room')

@login_required(login_url='/user/login')
def delete_chat_view(request, id):
    if request.method == 'POST':
        try:
            chat = request.user.own_chats.filter(id=id)
        except Exception as err:
            logger.warning(f'An warning ocurred: {err}')
            messages.error(request, f'Error trying to delete chat: {err}')
            return redirect('chat-room')
        
        chat.delete()
        messages.success(request, f'Chat successfully deleted.')
        return redirect('chat-room')

@login_required(login_url='/user/login')
def update_chat_view(request, id):
    if request.method == 'POST':
        try:
            chat = request.user.own_chats.get(id=id)
        except Exception as err:
            logger.warning(f'An warning ocurred: {err}')
            messages.error(request, f'Error trying to update chat: {err}')
            return redirect('chat-room')

        chat_form = ChatForm(data=request.POST or None, instance=chat)

        if chat_form.is_valid():
            chat_form.save()
            messages.success(request, f'Chat updated successfully.')
            return redirect('chat-room')
        
        messages.error(request, f'Invalid chat update request')
        return redirect('chat-room')
            
@login_required(login_url='/user/login')
def create_contact_view(request):
    if request.method == 'POST':
        contact_form = ContactForm(data=request.POST)

        if contact_form.is_valid():
            contact_form.save()
            messages.success(request, f'Contact created successfully.')
            return redirect('chat-room')
    
        messages.error(request, f'Invalid contact post request')
        return redirect('chat-room')

@login_required(login_url='/user/login')
def leave_chat_view(request, id):
    if request.method == 'POST':
        try:
            chat = request.user.chats.get(id=id)

            if request.user == chat.creator:
                chat.delete()
                messages.success(request, f'Chat leaved and deleted by default successfully.')
                return redirect('chat-room')
            
            chat.leave(request.user)
            messages.success(request, f'Chat leaved successfully.')
        except Exception as err:
            logger.warning(f'An warning ocurred: {err}')
            messages.error(request, f'Error trying to leave chat: {err}')
        
        return redirect('chat-room')

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
