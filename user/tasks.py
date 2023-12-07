import base64
import os
import logging
import PIL.Image as Image
import io
from celery import shared_task
from django.core.files import File
from user.utils import generate_image_name

logger = logging.getLogger(__name__)

@shared_task
def upload_image(data):
    logger.info('Uploading image...')

    user = data['user']
    file_name = generate_image_name(user)
    byte_data = data['picture'].encode('utf-8')
    b = base64.b64decode(byte_data)
    img = Image.open(io.BytesIO(b))
    img.save(file_name, format=img.format)

    with open(file_name, 'rb') as file:
        picture = File(file)
        user.picture = picture
        user.save()

    os.remove(file_name)
    logger.info('Uploaded!')
