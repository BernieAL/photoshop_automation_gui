#==========  ACCESS ALL SHOP PRODUCTS ========== #



product_test = {}
outputfile = './product.json'


shop_id = 9157753
url = f"https://api.printify.com/v1/shops/{shop_id}/products.json"

#required headers for printify reqeust
headers = {
    'Authorization': f'Bearer {token}',
    'User-Agent': 'PYTHON'
}

json_response = requests.get(url,headers=headers)
formatted_json = json.dumps(json_response.json(),indent=4)
print(formatted_json)
