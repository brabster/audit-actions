import argparse
import json
import os
import urllib.parse
import urllib.request


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--org', help='GitHub org to query')
    parser.add_argument('-t', '--trusted', action='append', help='trusted actions provider, may be used more than once')
    return parser.parse_args()


def get_results_page(org: str, page: int) -> tuple[dict, dict]:
    auth_token = os.environ['GITHUB_TOKEN']
    headers = {
        'Authorization': f'Bearer: {auth_token}',
        'Accept': 'application/vnd.github.text-match+json'
    }
    query = f'org:{org} path:.github NOT is_fork uses:'
    url = f'https://api.github.com/search/code?per_page=10&q={urllib.parse.quote(query)}' + (f'&page={page}' if page > 1 else '')
    request = urllib.request.Request(url)
    request.add_header('Authorization',f'Bearer {auth_token}')
    request.add_header('Accept','application/vnd.github.text-match+json')
    with urllib.request.urlopen(request) as response:
        return (response.headers, json.load(response))


def uses_non_local_action(line: str) -> bool:
    '''
    >>> uses_non_local_action('  foobar:  ')
    False
    >>> uses_non_local_action(' uses: actions/foobar')
    True
    >>> uses_non_local_action(' uses: ./foobar')
    False
    '''
    return 'uses:' in line and './' not in line


def get_action_parts(line: str) -> tuple[str, str]:
    '''
    >>> get_action_parts(' uses: actions/foobar')
    ('actions', 'foobar')
    >>> get_action_parts(' uses: fooble-bar-actions/foobar')
    ('fooble-bar-actions', 'foobar')
    '''
    return tuple(line.replace('"', '').replace('\'', '').split('uses:')[1].strip().split('/'))


if __name__ == '__main__':
    args = parse_args()
    
    # naive pagination to keep it simple and easy to understand
    items = []
    page = 1
    while True:
        headers, body = get_results_page(org=args.org, page=page)
        new_items = body['items']

        # no items indicates paged past end of results
        if len(new_items) == 0:
            break

        items = items + new_items
        page = page + 1
    
    for item in items:
        path = item['path']
        repo = item['repository']['full_name']
        matches = item['text_matches']
        for match in matches:
            fragment = match['fragment']
            lines = fragment.split('\n')
            for line in lines:
                if uses_non_local_action(line):
                    namespace, action = get_action_parts(line)
                    if namespace not in (args.trusted or []):
                        print(f'{repo}: {namespace}/{action} "{path}"')


