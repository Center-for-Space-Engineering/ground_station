import requests

class peripheral_hand_shake():
    def __init__(self, list_of_peripheral:list[str]) -> None:

        # Get pi url from the list of peripherals
        pi_url = list_of_peripheral[0]

        #create dictionary containing /Command and /receive_url, not sure what the key values should be
        data = {
            'command' : '/Command',
            'receive_url' : '/receive_url'
        }

        #post the command dictionary to the pi_url
        response = requests.post(pi_url, data=data)

        #Return the response, I wasn't sure what I am supposed to do with the response
        return response