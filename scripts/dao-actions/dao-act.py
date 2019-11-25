#!/usr/bin/env python3.6

import json
import subprocess

system_pub_key=""
file_funds = "../funds.json"
wallet_url = "http://localhost:6666"
node_url = "http://localhost:8888"
cmd = [
        "/usr/bin/daobet-cli",
        "--wallet-url=" + wallet_url,
        "--url=" + node_url
        ]
MTA = float(1672708200.0000)
TSE = float(167270820.0000)

SYMBOL = " BET"
STAKED_CPU = "1.0000"
STAKED_NET = "1.0000"
STAKED_RAM = "8"
STAKED_VOTE = "0.0000"

# For predefined accounts
PA_STAKED_CPU = "1.0000"
PA_STAKED_NET = "1.0000"
PA_STAKED_RAM = "8"
PA_STAKED_VOTE = "0.0000"
PA_NAMES = [
        "daobet",
        "dao",
        "bet",
        "casino",
        "play",
        "gambling",
        "fair",
        "trust",
        "vegas",
        "poker",
        "dice",
        "game",
        "blackjack",
        "lottery",
        "games",
        "slots",
        "gaming",
        "igaming",
        "cards",
        "live",
        "win",
        "jackpot",
        "bingo",
        "sports",
        "roulette",
        "luck",
        "lucky",
        "moneywheel",
        "racing",
        "betting",
        "macau",
        "fortune",
        "spin"
        ]


BRIDGE_ACCOUNT = "eosio.bridge"

TOKENS = [
        'EOS',
        'DAO',
        'USD',
        'USDT',
        'EUR',
        'ETH',
        'BTC'
        ]

def get_system_pub_key():
    _cmd = []
    _cmd.extend(cmd)
    _args_create = [
        "get", "account", "eosio", "-j"
    ]
    _cmd.extend(_args_create)
    _ts = subprocess.Popen(_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    _tso = _ts.communicate()[0]
    _acc_info = json.loads(_tso)
    _pub_key = _acc_info['permissions'][0]['required_auth']['keys'][0]['key']
    return _pub_key

def create_system_accounts(accounts=[]):
    count_success = 0
    count_error = 0
    with open('dao-actions.out','w+') as fout:
        with open('dao-actions.err','w+') as ferr:
            for _account in accounts:
                _cmd = []
                _res_out = ""
                _res_err = ""
                _cmd.extend(cmd)
                _args_create_1 = [
                    'create', 'account',
                    '-x', '45', 'eosio', _account, system_pub_key, system_pub_key
                ]
                _cmd.extend(_args_create_1)
                try:
                    _res = subprocess.run(_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, universal_newlines=True)
                    print(_res.stdout, _res.stderr)
                    count_success += 1
                    print("{} created".format(_account))
                except:
                    count_error += 1
    print("{} created account".format(count_success))
    print("{} errors".format(count_error))

def make_privileged(accounts=[]):
    count_success = 0
    count_error = 0
    with open('dao-actions.out','w+') as fout:
        with open('dao-actions.err','w+') as ferr:
            for _account in accounts:
                _cmd = []
                _res_out = ""
                _res_err = ""
                _cmd.extend(cmd)
                _args_create_1 = [
                    'push', 'action', 'eosio', 'setpriv',
                    "[\"" + _account + "\", 1]", "-p", "eosio@active"
                ]
                _cmd.extend(_args_create_1)
                try:
                    _res = subprocess.run(_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, universal_newlines=True)
                    print(_res.stdout, _res.stderr)
                    count_success += 1
                    print("{} created".format(_account))
                except:
                    count_error += 1
    print("{} created account".format(count_success))
    print("{} errors".format(count_error))

def reg_acc(
        name='',
        pub_key='',
        stake_net=STAKED_NET,
        stake_cpu=STAKED_CPU,
        stake_ram=STAKED_RAM,
        stake_vote=STAKED_VOTE,
        symbol=SYMBOL
        ):
    '''
    Registration genesis accounts (bridge)
    '''
    # create producers account
    _cmd = []
    _cmd.extend(cmd)
    _args_create = [
        "system", "newaccount", "-x", "45", "eosio", "--transfer", name,
        pub_key, "--stake-net", stake_net + symbol,
        "--stake-cpu", stake_cpu + symbol,
        "--stake-vote", stake_vote + symbol,
        "--buy-ram-kbytes", stake_ram
    ]
    _cmd.extend(_args_create)
    subprocess.run(_cmd)


def create_predefined_accounts(names=[]):
    '''
    Registration predefined accounts (bridge)
    '''
    _stake_net = PA_STAKED_NET
    _stake_cpu = PA_STAKED_CPU
    _stake_ram = PA_STAKED_RAM
    _stake_vote = PA_STAKED_VOTE
    symbol=" " + SYMBOL
    for name in names:
        # TODO: create temporary public key
        # create producers account
        _cmd = []
        _cmd.extend(cmd)
        print("NET : ", _stake_net, "", symbol)
        _args_create = [
            "system", "newaccount", "-x", "45", "eosio", name,
            system_pub_key, "--stake-net", _stake_net + symbol,
            "--stake-cpu", _stake_cpu + symbol,
            "--stake-vote", _stake_vote + symbol,
            "--buy-ram-kbytes", _stake_ram
        ]
        _cmd.extend(_args_create)
        subprocess.run(_cmd)


def send_funds(
        name,
        bet_liquid,
        symbol
        ):
    '''
    Send token - resources to all genesis accounts
    '''
    _cmd = []
    _cmd.extend(cmd)
    _args_create = [
        "transfer", "eosio", name,
        bet_liquid + symbol
    ]
    _cmd.extend(_args_create)
    subprocess.run(_cmd)


def create_token(_token_symbol=''):
    '''
    Create token
    '''
    _cmd3 = []
    _cmd3.extend(cmd)
    _args_create_3 = [
        "push", "action", "eosio.token", "create", "[\"eosio\", \"" + str("%.4f" % MTA) + " " + _token_symbol + "\"]", "-p", "eosio.token" 
    ]
    _cmd3.extend(_args_create_3)
    try:
        print("Creating token {}".format(_token_symbol))
        _res3 = subprocess.run(_cmd3, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, universal_newlines=True)
        print(_res3.stdout, _res3.stderr)
        print("OK")
    except:
        print("Token was NOT created")
    pass

def setcode_for():
    '''
    register and set code
    '''
    names=[
        'eosio.system',
        'eosio.token',
        'eosio.msig',
        'eosio.wrap'
            ]
    count_success = 0
    count_error = 0
    with open('dao-actions.out','w+') as fout:
        with open('dao-actions.err','w+') as ferr:
            for _name in names:
                if _name == "eosio.system":
                    _account = "eosio"
                else:
                    _account = _name

                _cmd1, _cmd2 = [], []
                # set abi
                _args_create_1 = [
                    "set", "abi", _account, "/host/opt/daobet/contracts/"+_name+"/"+_name+".abi"
                ]
                # set code
                _args_create_2 = [
                    "set", "code", _account, "/host/opt/daobet/contracts/"+_name+"/"+_name+".wasm"
                ]
                _cmd1.extend(cmd)
                _cmd1.extend(_args_create_1)
                _cmd2.extend(cmd)
                _cmd2.extend(_args_create_2)
                try:
                    print("=======  Contract {}  ========".format(_name))
                    _res1 = subprocess.run(_cmd1, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, universal_newlines=True)
                    print(_res1.stdout, _res1.stderr)
                    print("ABI activated".format(_account), end=' ')
                    _res2 = subprocess.run(_cmd2, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, universal_newlines=True)
                    print(_res2.stdout, _res2.stderr)
                    print("CODE activated".format(_account), end='\n\n')
                    count_success += 1
                except:
                    count_error += 1
            _cmd3, _cmd4, _cmd5 = [], [], []
            _cmd3.extend(cmd)
            _cmd4.extend(cmd)
            _cmd5.extend(cmd)
            _args_create_3 = [
                "push", "action", "eosio.token", "create", "[\"eosio\", \"" + str("%.4f" % MTA) + " BET\"]", "-p", "eosio.token" 
            ]
            _args_create_4 = [
                "push", "action", "eosio.token", "issue", "[\"eosio\", \"" + str("%.4f" % TSE) + " BET\", \"memo\"]", "-p", "eosio" 
            ]
            _args_create_5 = [
                "push", "action", "eosio", "init", "[0, \"4,BET\"]", "-p", "eosio" 
            ]
            _cmd3.extend(_args_create_3)
            _cmd4.extend(_args_create_4)
            _cmd5.extend(_args_create_5)
            try:
                print("Creating token")
                _res3 = subprocess.run(_cmd3, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, universal_newlines=True)
                print(_res3.stdout, _res3.stderr)
                print("OK")
                print("Allocating tokens", end=': ')
                _res4 = subprocess.run(_cmd4, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, universal_newlines=True)
                print(_res4.stdout, _res4.stderr)
                print("OK")
                print("Token created")
                print("Init system contracts", end=': ')
                _res5 = subprocess.run(_cmd5, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, universal_newlines=True)
                print(_res5.stdout, _res5.stderr)
                print("OK")
            except:
                print("Token was NOT created")
    print("{} created account".format(count_success))
    print("{} errors".format(count_error))


def setcode_bridge():
    '''
    register and set code bridge
    '''
    # TODO: need wasm for bridge
    # TODO: need name for bridge
    _cmd_1, _cmd_2 = [], []

    _cmd_1.extend(cmd)
    _args_create_1 = [
        "set", "abi",
        BRIDGE_ACCOUNT,
        "/host/opt/daobet/contracts/tokenbridge/tokenbridge.abi"
    ]
    _cmd_1.extend(_args_create_1)

    _cmd_2.extend(cmd)
    _args_create_2 = [
        "set", "code",
        BRIDGE_ACCOUNT,
        "/host/opt/daobet/contracts/tokenbridge/tokenbridge.wasm"
    ]
    _cmd_2.extend(_args_create_2)

    print("Init tokenbridge contract", end=': ')
    _res_1 = subprocess.run(_cmd_1, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, universal_newlines=True)
    print(_res_1.stdout, _res_1.stderr)
    _res_2 = subprocess.run(_cmd_2, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, universal_newlines=True)
    print(_res_2.stdout, _res_2.stderr)
    print("OK")


def get_total_supply():
    '''
    Get total supply
    '''
    _cmd = []
    _cmd.extend(cmd)
    _args_create = [
        "get", "account", "eosio", "-j"
    ]
    _cmd.extend(_args_create)
    _ts = subprocess.Popen(_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    _tso = _ts.communicate()[0]
    print(json.loads(_tso))
    _core_liquid_balance = json.loads(_tso)['core_liquid_balance'].split(" ")[0]
    _total_supply = \
        float(_core_liquid_balance)
    return _total_supply


def set_as_owner(accounts=[]):
    '''
    set eosio.prods as an owner for eosio?
    '''
    for _account in accounts:
        _cmd = []
        _cmd.extend(cmd)
        _args_create_1 = [
            "push", "action", "eosio", "updateauth",
            "{\"account\": \"" + _account + "\", \"permission\": \"owner\", \"parent\": \"\", \"auth\": {\"threshold\": 1, \"keys\": [], \"waits\": [], \"accounts\": [{\"weight\": 1, \"permission\": {\"actor\": \"eosio.prods\", \"permission\": \"active\"}}]}}",
            "-p", _account+"@owner"
        ]
        _args_create_2 = [
            "push", "action", "eosio", "updateauth",
            "{\"account\": \"" + _account + "\", \"permission\": \"active\", \"parent\": \"owner\", \"auth\": {\"threshold\": 1, \"keys\": [], \"waits\": [], \"accounts\": [{\"weight\": 1, \"permission\": {\"actor\": \"eosio.prods\", \"permission\": \"active\"}}]}}",
            "-p", _account+"@active"
        ]
        if _account == BRIDGE_ACCOUNT:
            _args_create_2 = [
                "push", "action", "eosio", "updateauth",
                "{\"account\": \"" + _account + "\", \"permission\": \"active\", \"parent\": \"owner\", \"auth\": {\"threshold\": 1, \"keys\": [], \"waits\": [], \"accounts\": [{\"weight\": 1, \"permission\": {\"actor\": \"" + BRIDGE_ACCOUNT + "\", \"permission\": \"eosio.code\"}}, {\"weight\": 1, \"permission\": {\"actor\": \"eosio.prods\", \"permission\": \"active\"}}]}}",
                "-p", _account+"@active"
            ]

        _cmd.extend(_args_create_1)
        subprocess.run(_cmd)
        _cmd = []
        _cmd.extend(cmd)
        _cmd.extend(_args_create_2)
        subprocess.run(_cmd)


with open(file_funds) as file:
    funds_data = json.load(file)
    '''
    ========                    =========
    ========    BASIC actions   =========
    ========                    =========
    '''

    #   IN PROGRESS
    '''
    1. Launch boot-node (healthcheck)
    '''

    # DONE
    '''
    1.1. Get system pub key
    '''
    system_pub_key = get_system_pub_key()

    #   DONE
    '''
    2. Registration system accounts (permissions: eosio)
        eosio.token
        eosio.msig
        eosio.vpay
        eosio.bpay
        eosio.saving
        eosio.names
        eosio.ram
        eosio.ramfee
        eosio.stake
        eosio.wrap
    '''
    
    print("Creating system accounts")
    create_system_accounts([
        "eosio.bpay",
        "eosio.msig",
        "eosio.names",
        "eosio.ram",
        "eosio.ramfee",
        "eosio.saving",
        "eosio.stake",
        "eosio.token",
        "eosio.vpay",
        "eosio.wrap",
        BRIDGE_ACCOUNT
        ])
    

    #   DONE
    '''
    3. Set code for:
        eosio.system
        eosio.token
        eosio.msig
        eosio.wrap
    '''
    
    setcode_for()
    setcode_bridge()

    # DONE
    '''
    4. Make eosio.msig privileged account
    '''
    make_privileged(["eosio.msig"])

    # DONE (in setcode_for)
    '''
    5. Issue token: 167,270,820 BET (with a max supply 1,672,708,200)
    '''

    # DONE ( in setcode_for ) 
    '''
    6. Push action eosio init '["0", "4, BET"]'
    '''

    '''

    ======                      =======
    ======    MAINNET actions   =======
    ======                      =======

    2.1 register genesis accounts and distribute tokens (also stake min resources)
    '''
    
    print("======  Registering accounts and sending funds...")
    print("=================================================")
    for item in funds_data:
        item_type = item.get('type', 'simple')
        if item_type == "simple":
            reg_acc(item['name'], item['pub_key'])
            send_funds(item['name'], str("%.4f" % (float(item['bet_liquid'].split(" ")[0]) - float(STAKED_CPU) - float(STAKED_NET))), " " + item['bet_liquid'].split(" ")[1])
        if item_type == "owner":
            OWNER_name = item['name']
            OWNER_bet_liquid = item['bet_liquid'].split(" ")[0]
            OWNER_bet_symbol = item['bet_liquid'].split(" ")[1]

    
    '''
    2.2 register bridge contract and set code bridge
    '''

    # DONE
    '''
    2.3 sent tokens to bridge
    '''
    print("TSE - Total Supply from Ethereum: {tse:.4f}".format(tse=TSE))
    _C = []
    for item in funds_data:
        item_type = item.get('type', 'simple')
        if item_type == "simple":
            sum_for_item = float(item['bet_liquid'].split(" ")[0])
            _C.append(sum_for_item)
    C = sum(_C)
    print("C - Sent to Claims except DAO: {c:.4f}".format(c=C))

    B = TSE - C - (float(OWNER_bet_liquid)) # TODO get dao funds from json (owner's account)
    print("B - Not Claimed ( for bridge ): {b:.4f}".format(b=B))
    print("Sending tokens to bridge")
    send_funds(
            BRIDGE_ACCOUNT, str("%.4f" % B), " " + SYMBOL
            )


    '''
    2.4 register short names((permissions: eosio):
        daobet
        dao
        bet
        eos
    '''
    create_predefined_accounts(PA_NAMES)

    '''
    2.5 create tokens in eosio.token: EOS, DAO
    '''
    for item in TOKENS:
        create_token(item)

    '''
    2.5.2 Send tokent to owner account
    '''
    
    for item in funds_data:
        item_type = item.get('type', 'simple')
        if item_type == "owner":
            reg_acc(item['name'], item['pub_key'])
            send_funds(item['name'], str("%.4f" % get_total_supply()), " " + item['bet_liquid'].split(" ")[1])

    '''
    2.6 set permission eosio@active and eosio@owner as eosio.prods@active
    '''
    print("======  Setting up eosio.prods owner for all contracts...")
    print("=================================================")
    set_as_owner([
        "eosio.bpay",
        "eosio.msig",
        "eosio.names",
        "eosio.ram",
        "eosio.ramfee",
        "eosio.saving",
        "eosio.stake",
        "eosio.token",
        "eosio.vpay",
        "eosio.wrap",
        BRIDGE_ACCOUNT
        ])
    set_as_owner(PA_NAMES)
