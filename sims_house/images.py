import io
import string

from PIL import Image, ImageDraw, ImageFont, ImageOps


def _centered_text_position(img, num_lines, line_height):

    """ Center text in the middle of the image depending on how many lines the text is """

    x_position =  15

    textbox_center = num_lines*line_height/2
    image_center = img.height/2 
    y_position = image_center - textbox_center

    return (x_position, y_position)

def _hacky_word_wrap(font, text):

    """ because textwrap.wrap did a good job except when it didn't """

    charmap = {letter: font.getsize(letter)[0] for letter in string.printable}
    text = text.replace('\n', ' \n ').split(' ')

    lines = []
    current_line = []
    current_line_size = 0

    for word in text:
        if word == '\n':
            lines.append('\n')

        else:
            word_size = sum(charmap[letter] for letter in word)
            potential_line_size = current_line_size + word_size

            if potential_line_size <= 200:
                current_line_size = potential_line_size
                current_line.append(word)

            else:
                lines.append(' '.join(current_line))
                current_line = [word]
                current_line_size = word_size
        
    lines.append(' '.join(current_line))

    return lines


def _write_lines(panel, text):

    """ Write centered lines of text onto image """

    line_height = 20

    draw = ImageDraw.Draw(panel)
    font = ImageFont.truetype("/Library/Fonts/Futura.ttc", 15)
    lines = _hacky_word_wrap(font, text)

    x_text, y_text = _centered_text_position(panel, len(lines), line_height)
    for line in lines:
        draw.text((x_text, y_text), line, font=font, fill=(0,0,0))
        y_text += line_height

    return panel

def _combine_images(img, panel):

    """ Combine original image with text panel side-by-side for larger image """ 

    new_im = Image.new('RGB', (img.width + panel.width, img.height))
    x_offset = 0
    for im in (img, panel):
        new_im.paste(im, (x_offset,0))
        x_offset += im.width

    return new_im

def _save_image(new_im):

    temp = io.BytesIO()
    new_im.save(temp, format="JPEG")

    return temp

def prepare_image(obj, id, text):

    """ Adds a text panel next to original photo and returns a file blob"""

    img = Image.open(obj)

    panel = Image.new('RGB', (250, img.height), color='white')
    panel = _write_lines(panel, text)

    new_im = _combine_images(img, panel)
    new_im = _save_image(new_im)

    return new_im
