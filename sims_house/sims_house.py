import os
from multiprocessing.pool import Pool

import facebook
from googleapiclient.discovery import build

from sims_house.fb_api import fetch_image_metadata, stream_image
from sims_house.gdrive import get_creds, get_parent_folder_id, upload_image
from sims_house.images import prepare_image


def upload_images(drive, folder_id, image_id, text, link):
    img = stream_image(image_id, text, link)
    img = prepare_image(img, image_id, text)
    upload_image(drive, image_id, img, folder_id)

def _combine(drive, folder_id, images):
    for img in images:
        yield [drive, folder_id]+img

if __name__ == "__main__":
    graph = facebook.GraphAPI(access_token=os.getenv('FB_ACCESS_TOKEN'), version="3.1")
    images = fetch_image_metadata(graph, '1847648795309980/photos')

    creds = get_creds()
    drive_service = build('drive', 'v3', credentials=creds)
    folder_id = get_parent_folder_id(drive_service)

    images = _combine(drive_service, folder_id, images)

    with Pool() as pool:
        pool.starmap(upload_images, images)
