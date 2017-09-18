import requests
import re
import json
from lxml import html, etree
from lxml.cssselect import CSSSelector


verbose = True


SITE_URL = 'http://www.filmweb.pl'
select_topics_links = CSSSelector('.topics-list h3 a')
select_first_post = CSSSelector('.firstPost')
select_post_author = CSSSelector('.userName')
select_date_time = CSSSelector('.cap')
select_points = CSSSelector('.plusCount')
select_post_info = CSSSelector('.postInfo')
select_post_text = CSSSelector('.text')
select_title = CSSSelector('h1 a')


def get_opinion(opinion_url):
    response = requests.get(opinion_url)
    tree = html.fromstring(response.content)
    first_post = select_first_post(tree)[0]
    rating_match = re.search(rb'(\d+) <i', etree.tostring(select_post_info(first_post)[0]))
    post_text_el = select_post_text(first_post)[0]
    etree.strip_elements(post_text_el, "*", with_tail=False)
    opinion = {
        'author': select_post_author(first_post)[0].text.strip(),
        'date': select_date_time(first_post)[0].get('title'),
        'rating': int(rating_match.group(1)) if rating_match else None,
        'points': int(select_points(first_post)[0].text or 0),
        'title': select_title(tree)[0].text,
        'text': post_text_el.text
    }
    return opinion


def get_opinions(discussion_url, page):
    if verbose:
        print('Page #%d' % page)
    response = requests.get('{}?page={}'.format(discussion_url, page))
    tree = html.fromstring(response.content)
    opinions = []
    topics_links = select_topics_links(tree)
    opinions_len = len(topics_links)
    for i, opinion_link in enumerate(topics_links):
        if verbose: print('    Parsing opinion {} of {}'.format(i + 1, opinions_len), end='\r')
        opinions.append(get_opinion(SITE_URL + opinion_link.get('href')))
    if verbose: print()
    return opinions


def get_all_opinions(discussion_url):
    all_opinions = []
    page = 1
    while True:
        opinions = get_opinions(discussion_url, page)
        if len(opinions) == 0:
            break
        all_opinions += opinions
        page += 1
    return all_opinions


opinions = get_all_opinions(SITE_URL + '/' +
                            'serial/Westworld-2016-232988' +
                            '/discussion')

selected_opinions = list(filter(lambda op: op['rating'] is not None, opinions))

with open('out.js', 'w') as f:
    json.dump(selected_opinions, f)
