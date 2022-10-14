# synthetix_legacy_escrow

`conf.yaml` file should be incorporated into config folder with the following:

```
rpc: "https://eth-mainnet.g.alchemy.com/v2/XXXXXXXXXXXXXXXXXXXXXX"
                
etherscan:  
    abi: 'https://api.etherscan.io/api?module=contract&action=getabi&address={}&apikey=XXXXXXXXXXXXXXXXXX'
    transfers: 'https://api.etherscan.io/api?module=account&action=txlist&address={}&startblock=0&endblock=latest&sort=asc&apikey=XXXXXXXXXXXXXXXXXX'

multicaller: '0xeefBa1e63905eF1D7ACbA5a8513c70307C1cE441'

mysql:
    user:  "root"
    password:  "XXXXXXXXXXXXXXXXXXXXXXX"
    host:  "localhost"
    database:  "legacy_synthetix_escrow"
    raise_on_warnings:  True
    port: 3315
```
 
