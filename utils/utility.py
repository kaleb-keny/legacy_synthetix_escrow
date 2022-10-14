import yaml
import requests
import time
import web3 as w3

def parse_config(path):
    with open(path, 'r') as stream:
        return  yaml.load(stream, Loader=yaml.FullLoader)

def get_w3(conf):
    return w3.Web3(w3.HTTPProvider(conf["rpc"]))

async def run_post_request(session,url,payload):
    async with session.post(url=url,data=payload) as response:
        return await response.json(content_type=None)
    
def get_abi(conf,address):
    headers      = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    url = conf["etherscan"]["abi"].format(address)
    while True:
        try:
            result = requests.get(url,headers=headers).json()
            if result["status"] != '0':
                return result["result"]
            else:
                print("error seen with abi fetch, trying again")
                time.spleep(3)
                continue
        except:
            print("error seen with abi fetch, trying again")
            time.sleep(3)