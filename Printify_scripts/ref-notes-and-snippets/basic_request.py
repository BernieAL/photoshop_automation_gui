import requests
import json
import os

token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIzN2Q0YmQzMDM1ZmUxMWU5YTgwM2FiN2VlYjNjY2M5NyIsImp0aSI6IjlhMDVjZWNiYjc4MzcyYzIxMDk2N2UzNWM2MDNkYTMyNzE5YWZjYzc0NTQxOGM0NzRhNWIzNzA2MDFlNjBmZDk0ZTRmN2NjODEwZDZlMTMzIiwiaWF0IjoxNjg0OTQ0OTYzLjMwMTY0MywibmJmIjoxNjg0OTQ0OTYzLjMwMTY0OCwiZXhwIjoxNzE2NTY3MzYzLjI5Mjc1Nywic3ViIjoiMTI3NDY2NjAiLCJzY29wZXMiOlsic2hvcHMubWFuYWdlIiwic2hvcHMucmVhZCIsImNhdGFsb2cucmVhZCIsIm9yZGVycy5yZWFkIiwib3JkZXJzLndyaXRlIiwicHJvZHVjdHMucmVhZCIsInByb2R1Y3RzLndyaXRlIiwid2ViaG9va3MucmVhZCIsIndlYmhvb2tzLndyaXRlIiwidXBsb2Fkcy5yZWFkIiwidXBsb2Fkcy53cml0ZSIsInByaW50X3Byb3ZpZGVycy5yZWFkIl19.Aexvip9HWZgRfm-UCLBWFOw0R1_eF3aU8QMjkK9LaHymKuwosMCfrIwp4YyVqNNXggLZSbbEt2yjl-qarew'


# ===== BASIC REQUEST TO ACCESS LIST OF SHOPS ===== #
# /shops.json gets list of shops and there ID's
url = "https://api.printify.com/v1/shops.json"

#required headers for printify reqeust
headers = {
    'Authorization': f'Bearer {token}',
    'User-Agent': 'PYTHON'
}
response = requests.get(url,headers=headers)
#  used to access response payload data
print(response.json())