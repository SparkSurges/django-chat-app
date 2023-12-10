from chat.models import Chat
from user.models import Contact, CustomUser

def serialize_chat_public_private(user, chats):
    serialized_chats = []
    for chat in chats:
        if chat.is_private:
            serialized_chats.append(serialize_private_chat(user, chat))
        else:
            serialized_chats.append(serialize_chat(user, chat))

    return serialized_chats

def serialize_chat(user, chat):
    admins_data = [
        {
            'id': admin.id,
            'username': admin.username,
            'email': admin.email,
            'last_seen': admin.last_seen,
        }
        for admin in chat.admins.all()
    ]

    users_data = [
        {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'last_seen': user.last_seen
        }
        for user in chat.users.all()
    ]

    return {
        'id': str(chat.id),
        'name': chat.name,
        'description': chat.description,
        'picture': str(chat.picture.url) if chat.picture else None,
        'is_private': chat.is_private,
        'admins': admins_data,
        'users': users_data,
        'link': chat.link,
        'group_name': chat.group_name,
        'created_at': chat.created_at.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
    }

def serialize_private_chat(user, private_chat):
    user_contact = get_user_contact_from_private_chat(user, private_chat)
    contact = Contact.objects.filter(
        user=user,
        email=user_contact.email
    ).first()

    return {
        'id': str(user_contact.id),
        'username': contact.username,
        'email': contact.email,
        'picture': str(user_contact.picture.url) if user_contact.picture else None,
        'connected': user_contact.connected,
        'last_seen': user_contact.last_seen,
        'group_name': private_chat.group_name,
        'is_private': private_chat.is_private,
    }

def get_user_contact_from_private_chat(user, private_chat):
    admins = private_chat.admins.all()
    return admins.exclude(user=user).first()
