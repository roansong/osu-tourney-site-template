import requests
from django.conf import settings

STANDARD = 0
TAIKO = 1


def api_request(endpoint: str, params: dict):
    request_params = {
        'k': settings.API_KEY,
        'm': STANDARD
    }
    request_params.update(params)
    result = requests.get(url=f"{settings.API_HOST}/{endpoint}", params=request_params)
    j = result.json()
    if not j or isinstance(result.json(), dict):
        return j
    if isinstance(result.json(), dict):
        return j
    return j[0]


if __name__ == "__main__":
    import pprint
    pprint.pprint(api_request('get_match', {'mp': 63175703}))