import random, string, json
from flask import make_response

class WebHelper:
    def generateRandomClientId(self, rndNumb):
         # Generate random chain of strings and digits with length of 64 signs which will be our antiforgery state
        state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(rndNumb))
        return state

    def generateJsonDump(self, description, error_code):
        # Generic generation of json messages
        response = make_response(json.dumps(description), error_code)
        response.headers['Content-Type'] = 'application/json'
        return response
