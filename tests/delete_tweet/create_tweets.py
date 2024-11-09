# payload = {"text": "Hello world!"}
from __future__ import annotations


def post_tweet(oauth, payload):
    response = oauth.post(
        "https://api.twitter.com/2/tweets",
        json=payload,
    )

    if response.status_code != 201:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )

    print("Response code: {}".format(response.status_code))

    # Saving the response as JSON
    # print(json.dumps(json_response, indent=4, sort_keys=True))
