import requests


def fetch_image_metadata(graph, base_node):

    """ Query Facebook for information about relevant images to download """

    node = base_node
    id = 0

    while True:
        images = graph.get_object(node, fields='name,webp_images{source}')
        for image in images['data']:
            id += 1
            text = image['name']
            link = image['webp_images'][0]['source']
            yield [id, text, link]
        
        after_id =  images['paging'].get('next')

        if after_id:
            node = f'{base_node}/after={after_id}'

        else:
            break


def stream_image(id, text, link):

    """ Download a given image and return a file blob"""

    r = requests.get(link, stream=True)
    if r.status_code == 200:
        r.raw.decode_content = True
        return r.raw
    else:
        r.raise_for_status()
