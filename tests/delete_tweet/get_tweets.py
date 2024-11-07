from __future__ import annotations

from auth import connect_to_endpoint
from auth import get_user_id


def get_tweets(oauth, number):
    """
    Method to acquire a specified number of tweets from the user.
    """
    id = get_user_id(oauth)
    url = "https://api.x.com/2/users/" + str(id) + "/tweets"
    params = {"tweet.fields": "id,text", "max_results": number}
    json_response = connect_to_endpoint(url, params)
    # print(json.dumps(json_response, indent=4, sort_keys=True))
    return json_response
