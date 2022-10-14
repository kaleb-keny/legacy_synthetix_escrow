import pandas as pd
import requests
from utils.multicall import Multicall
import asyncio
import nest_asyncio
nest_asyncio.apply()
from utils.utility import get_abi, get_w3

class UpdateData(Multicall):
    
    def __init__(self,conf):
        self.conf = conf
        Multicall.__init__(self,conf=conf)
        self.synthetixAddress = self.get_snx_address('Synthetix')
        
    def run_update_data(self):

        addressList  = self.gather_address_list()
        legacyEscrow = self.gather_legacy_escrow(addressList)
        cRatio       = self.gather_c_ratio(addressList)
        debt         = self.gather_debt(addressList)
        collateral   = self.gather_collateral(addressList)

        df=pd.DataFrame(addressList)
        df.columns=['address']
        df["legacy_escrow"] = df["address"].map(legacyEscrow)/1e18
        df["c_ratio"] = df["address"].map(cRatio)/1e18
        df["c_ratio"] = df["c_ratio"].apply(lambda x: 1/x if x > 0 else 0)
        df["debt"] = df["address"].map(debt)/1e18
        df["collateral"] = df["address"].map(collateral)/1e18
        df = df[["address",'legacy_escrow','c_ratio','collateral','debt']]
        df.to_csv("output/output.csv")        
        
    def gather_address_list(self):
        escrowAddress = self.get_snx_address('SynthetixEscrow')
        abi = get_abi(self.conf,escrowAddress)
        w3 = get_w3(self.conf)
        contract = w3.eth.contract(address=escrowAddress,abi=abi)
        response = requests.get(self.conf["etherscan"]["transfers"].format(escrowAddress))
        data = response.json()
        df = pd.DataFrame(data["result"])
        df = df[df["functionName"]=="addVestingSchedule(address account, uint256[] times, uint256[] quantities)"]
        df["decoded_input"] = df["input"].apply(lambda x: contract.decode_function_input(x))
        data = df["decoded_input"].str[1].to_list()
        data = [dataDict["account"] for dataDict in data]
        return list(set(data))
        
    def gather_legacy_escrow(self,addressList):
        escrowAddress = self.get_snx_address('SynthetixEscrow')
        abi = get_abi(self.conf,escrowAddress)
        w3 = get_w3(self.conf)
        contract = w3.eth.contract(address=escrowAddress,abi=abi)
        task = self.run_multicall(addressList=addressList, functionName='balanceOf', contract=contract)
        output = self.run_async_task([task])
        return output[0]

    def gather_c_ratio(self,addressList):
        abi = get_abi(self.conf,self.synthetixAddress)
        w3 = get_w3(self.conf)
        contract = w3.eth.contract(address=self.synthetixAddress,abi=abi)
        task = self.run_multicall(addressList=addressList, functionName='collateralisationRatio', contract=contract)
        output = self.run_async_task([task])
        return output[0]

    def gather_debt(self,addressList):
        abi = get_abi(self.conf,self.synthetixAddress)
        w3 = get_w3(self.conf)
        contract = w3.eth.contract(address=self.synthetixAddress,abi=abi)
        task= self.run_multicall(addressList, functionName='debtBalanceOf', contract=contract,arg='0x73555344')
        output = self.run_async_task([task])
        return output[0]

    def gather_collateral(self,addressList):
        abi = get_abi(self.conf,self.synthetixAddress)
        w3 = get_w3(self.conf)
        contract = w3.eth.contract(address=self.synthetixAddress,abi=abi)
        task= self.run_multicall(addressList, functionName='collateral', contract=contract)
        output = self.run_async_task([task])
        return output[0]
        
    def run_async_task(self,task):
        loop  = asyncio.get_event_loop()        
        task  = asyncio.gather(*task,return_exceptions=True)
        try:
            return loop.run_until_complete(task)
        except:
            tasks = asyncio.all_tasks(loop=loop)
            for t in tasks:
                t.cancel()
            group = asyncio.gather(*tasks,return_exceptions=True)
            loop.run_until_complete(group)
            
    def get_snx_address(self,contractName):
        url = 'https://raw.githubusercontent.com/Synthetixio/synthetix/develop/publish/deployed/mainnet/deployment.json'
        output = requests.get(url)
        return output.json()["targets"][contractName]["address"]
