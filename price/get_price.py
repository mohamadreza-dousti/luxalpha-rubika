import requests

class tether:
    def get_price(self):
        try:
            url = "https://market.tetherland.com/prices"
            res = requests.get(url)
            data = res.json()
            md = data['data']['markets']['USDTTMN']['asks'][0]
            p = md['price']
            return p
        except Exception as e:
            return False
        