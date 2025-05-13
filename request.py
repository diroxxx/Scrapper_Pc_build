import requests

ACCESS_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzY29wZSI6WyJhbGxlZ3JvOmFwaTpzYWxlOm9mZmVyczpyZWFkIl0sImFsbGVncm9fYXBpIjp0cnVlLCJpc3MiOiJodHRwczovL2FsbGVncm8ucGwiLCJleHAiOjE3NDcyMDYzMDksImp0aSI6IjYwNjM5NzI0LTE5YjUtNGIyYS1hN2RkLWU2NGMyOGFkZTQ4ZSIsImNsaWVudF9pZCI6ImM1YzU1NzJjNDg4NjRlMmE4MWM3YjY3OTdkYjJhOGUzIn0.hjGbPhYyGjEmwQK0pjJR4vtCY7ViMVJJi13CApxZsqJ8icW0z3kIfkuYBipRN2_b5Nx_paHNv7IcfXCj65OErkKW2LfIi1xKgVOFQmJc06T-kFrFQQiki1FlyUOuQawQvRf30VnEEt2dCE7_d1Zlrv3l2aPr6z026cEtgi_2blzdWBVz35AXZL1NMPxumqGLZ25iJzY1RYyhwV7cU6WIuRpP7W7PtCZzEXIyZjXV0iCsae-S1tjhWo6vBgfX9IFTxp7ijwMW3PssQByNdKukYGac_IEzSyQghqb0pN6k7fy3cuo1IbQUx81K9MoeuxJDm6U1JLzBlVpdOGrkxtJXMg"

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Accept": "application/vnd.allegro.public.v1+json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# url = "https://api.allegro.pl.allegrosandbox.pl/sale/categories"
url = "https://allegro.pl/sale/categories"

response = requests.get(url, headers=headers)

print(response.status_code)
print(response.text)
