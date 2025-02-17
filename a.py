
def sabe(**kwargs):
    print("https://{region}.api.riotgames.com/riot/account/v1/accounts/by-puuid/{puuid}?api_key={api_key}".format(server="aaa", region="euw1",  **kwargs))




sabe(puuid ="aaa", api_key = "ss" )