#!/usr/bin/env python3

import sys, os, pprint, json
import base64, io
from PIL import Image, ImageOps
from argparse import ArgumentParser
from bs4 import BeautifulSoup, Tag

def is_a_student_entry(tag):
    return (isinstance(tag,Tag) and tag.name == 'img' and 
            isinstance(tag.parent, Tag) and tag.parent.name == 'div')

def read_roster(path):
    with open(path) as f:
        data = json.load(f)
        print(data['name'])
        for x in data['contacts']:
            print(x.keys())
            start = x['photoData'].find('/9')
            jpg = x['photoData'][start:]
            Image.open(io.BytesIO(base64.b64decode(jpg))).save('result.jpg')
            # e.g., 640 x 640 JPG image
            

def generate_contact(first, last, img_path):
    prefix = 'data:image/jpeg;base64,'

    image = Image.open(img_path)
    size = (image.size[0],image.size[0])
    image.thumbnail(size, Image.ANTIALIAS)
    background = Image.new('RGB', size, (0, 0, 0))
    background.paste(
        image, (int((size[0] - image.size[0]) / 2), int((size[1] - image.size[1]) / 2))
    )

    buffered = io.BytesIO()
    background.save(buffered, format='JPEG')
    img_str = base64.b64encode(buffered.getvalue())

    photoData = prefix + img_str.decode()
    contact = {'first':first, 'last':last, 'details':'', 'photoData':photoData}
    return contact


if __name__ == '__main__':
    SCRIPTPATH = os.path.dirname(os.path.abspath(__file__))

    parser = ArgumentParser(description='Create Name Shark roster from Picture Roster')
    parser.add_argument("files", type=str, nargs='+',
        help="Path to saved website index")
    OPT = vars(parser.parse_args())

    contacts = []
    roster_title = None

    # open picture roster and process it
    for idx in OPT['files']:
        idx = os.path.abspath(idx)

        with open(idx, 'r') as fp:
            soup = BeautifulSoup(fp, 'html.parser')

            roster_title = soup.find('h3').text
            for s in soup.find_all(is_a_student_entry):
                img_path = os.path.join(os.path.dirname(idx), s['src'])
                last_first = s.parent.next_sibling.next_sibling.text[2:].split(', ')
                first = last_first[1]
                last = last_first[0]

                x = generate_contact(first, last, img_path)
                contacts.append(x)

    # assemble roster
    roster = {'name': roster_title, 
              'contacts':contacts}

    # write the roster
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(roster, f)
