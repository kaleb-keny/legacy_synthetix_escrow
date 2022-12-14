from web3._utils.abi import get_abi_output_types
from utils.utility import run_post_request, get_w3, get_abi
from funcy import chunks
from web3.providers.base import JSONBaseProvider
import aiohttp
import asyncio

class Multicall():

    def __init__(self,conf):

        self.conf = conf
        w3 = get_w3(conf)
        multicallABI = get_abi(self.conf,address=self.conf["multicaller"])

        #get the multicall contract        
        self.multicallContract = w3.eth.contract(address=self.conf["multicaller"],abi=multicallABI)

        #get the aggregate decoding data types
        decoder           = self.multicallContract.get_function_by_name(fn_name='aggregate')
        self.decoder      = get_abi_output_types(decoder.abi)

    async def run_multicall(self, addressList,functionName,contract,arg=None):
        
        responsesList     = list()
        payloadChunks     = list()
        outputList        = list()
        w3                = get_w3(self.conf)
                
        #Aggergate addresses into chunks of 1,000
        for addressChunk in chunks(1000,addressList):
            payloads = list()
            #for each chunk prepare the payload to be sent in async manner (since 1 payload per chunk, so 1 chunk = 1k addresses)
            for address in addressChunk:
                if arg is None:
                    callData = contract.encodeABI(fn_name=functionName,args=[address])
                else:
                    callData = contract.encodeABI(fn_name=functionName,args=[address,arg])
                payloads.append((contract.address,callData))
            payloadChunks.append(self.multicallContract.encodeABI(fn_name='aggregate',args=[payloads]))
                    
        for payloadChunk in chunks(5,payloadChunks):
            tries = 0
            while tries < 4:
                try:
                    baseProvider    = JSONBaseProvider()
                    tasks = list()
                    async with aiohttp.ClientSession() as session:
                        for payload in payloadChunk:
                                params=[{'from':'0x0000000000000000000000000000000000000000',
                                         'to':self.multicallContract.address,
                                         'data':payload},
                                        'latest']
                                payload = baseProvider.encode_rpc_request('eth_call',params)
                                task = run_post_request(session=session,
                                                        url=self.conf['rpc'],
                                                        payload=payload)
                                tasks.append(task)
                        responsesList.extend(await asyncio.gather(*tasks))
                        break
            
                except KeyboardInterrupt:
                    return None

                except Exception as e:
                    print(e)
                    tries+=1
                    await asyncio.sleep(2)

        #decode the responses  ['uint256',[bytes[]]] < [blockNumber,[ETH_VALUES]]
        for response in responsesList:
            outputList.extend(w3.codec.decode_abi(self.decoder, w3.toBytes(hexstr=response["result"]))[1])
        return {address:w3.toInt(output) for address, output in zip(addressList,outputList)}