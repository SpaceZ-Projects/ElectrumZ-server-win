# ElectrumZ-Server (Windows)

## Getting Started :

### Requirements :

- Python 3.8 or higher
- Git

Clone the Repository:

```
git clone https://github.com/SpaceZ-Projects/ElectrumZ-server-win.git
cd ElectrumZ-server-win
```

- Setup virtual environment :

Start `setup.bat` file ( as administrator to allow ports 50001 50002 50004 8000)


- Run ElectrumZ :

Start `start-server.bat` file

- example of bitcoinz.conf file :

```
showmetrics=0
rpcthreads=50
maxconnections=50
daemon=1
server=1
whitelist=127.0.0.1
whitelist=172.17.0.2
whitelist=172.17.0.3
txindex=1
addressindex=1
timestampindex=1
spentindex=1
rpcuser=SpaceZProjects
rpcpassword=SpaceZProjects@2042
rpcallowip=127.0.0.1
rpcallowip=172.17.0.2
rpcallowip=172.17.0.3

addnode=explorer.btcz.app:1989
addnode=explorer.btcz.rocks:1989
addnode=74.208.91.217:8233
addnode=37.187.76.80:1989
```