# AUTOGENERATED! DO NOT EDIT! File to edit: 00_parser.ipynb (unless otherwise specified).

__all__ = ['format_date', 'parse_query']

# Cell

from urllib.parse import urlparse, parse_qsl, parse_qs
import requests
import arrow

def format_date(date, start=False):
    '''
    The web interface uses YYYY-MM-DD dates, but the API expects YYYY-MM-DDT00:00:00Z. Reformat dates accordingly.

    Also the start date in an API query needs to be set to the day before you want. So if this is a start date, take it back in time by a day.
    '''
    if date != '*':
        date_obj = arrow.get(date)
        if start:
            date_obj = date_obj.shift(days=-1)
        date = '{}Z'.format(date_obj.format('YYYY-MM-DDT00:00:00'))
    return date

def parse_query(query):
    '''
    Converts the parameters of a search using the Trove web interface into a form the API will understand.

    Parameters:
    * `query` – the url of a search in the Trove newspapers & gazettes category

    Returns:
    * a dict containing the parameters (multiple values will be in a list)
    '''
    parsed_url = urlparse(query)
    if 'api.trove.nla.gov.au' in query:
        # If it's an API url, no further processing of parameters needed
        new_params = parse_qs(parsed_url.query)
    else:
        # These params can be accepted as is.
        safe = ['l-category', 'l-title', 'l-decade', 'l-year', 'l-month', 'l-state', 'l-word', 'include']
        new_params = {}
        dates = {}
        keywords = []
        params = parse_qsl(parsed_url.query)
        # Loop through all the parameters
        for key, value in params:
            if key in safe:
                try:
                    new_params[key].append(value)
                except KeyError:
                    new_params[key] = [value]
            elif key == 'l-advWord':
                new_params['l-word'] = value
            elif key == 'l-advstate':
                try:
                    new_params['l-state'].append(value)
                except KeyError:
                    new_params['l-state'] = [value]
            elif key == 'l-advcategory':
                try:
                    new_params['l-category'].append(value)
                except KeyError:
                    new_params['l-category'] = [value]
            elif key == 'l-advtitle':
                try:
                    new_params['l-title'].append(value)
                except KeyError:
                    new_params['l-title'] = [value]
            elif key in ['l-illustrationType', 'l-advIllustrationType']:
                new_params['l-illustrated'] = 'true'
                try:
                    new_params['l-illtype'].append(value)
                except KeyError:
                    new_params['l-illtype'] = [value]
            elif key == 'date.from':
                dates['from'] = value
            elif key == 'date.to':
                dates['to'] = value
            elif key == 'keyword':
                new_params['q'] = value
            elif key == 'keyword.phrase':
                keywords.append('"{}"'.format(value))
            elif key == 'keyword.not':
                keywords.append('NOT ({})'.format(' OR '.join(value.split())))
            elif key == 'keyword.any':
                keywords.append('({})'.format(' OR '.join(value.split())))
            elif key in ['l-ArtType', 'l-advArtType', 'l-artType']:
                if value == 'newspapers':
                    new_params['zone'] = 'newspaper'
                elif value == 'gazette':
                    new_params['zone'] = 'gazette'
        if keywords:
            if 'q' in new_params:
                new_params['q'] += ' AND {}'.format(' AND '.join(keywords))
            else:
                new_params['q'] = ' AND '.join(keywords)
        if dates:
            if 'from' not in dates:
                dates['from'] = '*'
            if 'to' not in dates:
                dates['to'] = '*'
            date_query = 'date:[{} TO {}]'.format(format_date(dates['from'], True), format_date(dates['to']))
            if 'q' in new_params:
                new_params['q'] += ' {}'.format(date_query)
            else:
                new_params['q'] = date_query
        if 'q' not in new_params:
            new_params['q'] = ' '
        if 'zone' not in new_params:
            new_params['zone'] = 'newspaper,gazette'
    # return '{}?{}'.format('https://api.trove.nla.gov.au/v2/result', urlencode(new_params, doseq=True))
    return new_params