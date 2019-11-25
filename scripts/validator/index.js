const {
    Api,
    JsonRpc,
    RpcError
} = require('eosjs');
const fetch = require('node-fetch');
const fs = require('fs');
const {
    TextEncoder,
    TextDecoder
} = require('util');


/*-------------INITIAL_CONFIG--------------*/
const NODE_VERSION = 'v1.0.0';
const MAX_SUPPLY = "1672708200.0000 BET";
const SUPPLY = "167270820.0000 BET";
const DAO_MAX_RAM_SPENT = '100.0000 BET';
const BRIDGE_ACCOUNT = 'eosio.bridge';
const SYSTEM_ACCOUNTS = [
    'eosio.token',
    'eosio.msig',
    'eosio.vpay',
    'eosio.bpay',
    'eosio.saving',
    'eosio.names',
    'eosio.ram',
    'eosio.ramfee',
    'eosio.stake',
    'eosio.wrap',
    BRIDGE_ACCOUNT
];
const SYSTEM_CONTRACTS = [
    'eosio',
    'eosio.token',
    'eosio.msig',
    'eosio.wrap',
    BRIDGE_ACCOUNT
];
const SYSTEM_CONTRACT_VERSION = 'v1.0.7';
const SHORT_NAMES = [
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
];
const TOKENS = [
    'EOS',
    'DAO',
    'USD',
    'USDT',
    'EUR',
    'ETH',
    'BTC',
];
/*-----------------------------------------*/


const NODE_URL = process.env.NODE_URL || 'http://127.0.0.1:8888';
const JSON_PATH = process.env.JSON_PATH || '../funds.json';

const rpc = new JsonRpc(NODE_URL, {
    fetch
});
const funds = JSON.parse(fs.readFileSync(JSON_PATH));

function asset(str) {
    str = str.toString();
    return parseFloat(str.split(' ')[0]);
}

function total_funds(acc_info) {
    return asset(acc_info.total_resources ? acc_info.total_resources.net_weight : "0") +
        asset(acc_info.total_resources ? acc_info.total_resources.cpu_weight : "0") +
        asset(acc_info.total_resources ? acc_info.total_resources.vote_weight : "0") +
        asset(acc_info.core_liquid_balance ? acc_info.core_liquid_balance : "0");
}

let checks = [];

function throw_error(msg, exp, found) {
    throw `${msg}, expected: ${exp}, found: ${found}`;
}

function new_check(name, check) {
    checks.push({
        name: name,
        check: check,
    });
}


//CHECKS
new_check('Json validate', async () => {
    let accts_set = new Set();
    funds.forEach(acc => accts_set.add(acc.name));

    if (accts_set.size !== funds.length) {
        throw_error("Json should contain only unique accounts");
    }

    let owners = funds.filter(acc => acc.type === "owner");
    if (owners.length !== 1) {
        throw_error("Json should contain 1 owner account", 0, owners.length);
    }

    let systems = funds.filter(acc => SYSTEM_ACCOUNTS.find(sys => sys === acc));
    if (systems.length !== 0) {
        throw_error("Json shouldn't contain system account");
    }
});

new_check('Node version check', async () => {
    let info = await rpc.get_info();

    if (info.server_version_string !== NODE_VERSION) {
        throw_error("Invalid node version", NODE_VERSION, info.server_version_string);
    }
});

new_check('Supply check', async () => {
    let curr_stats = await rpc.get_currency_stats('eosio.token', 'BET');

    if (curr_stats['BET'].supply !== SUPPLY) {
        throw_error("Invalid currency supply", SUPPLY, curr_stats['BET'].supply);
    }
});

new_check('Max supply check', async () => {
    let curr_stats = await rpc.get_currency_stats('eosio.token', 'BET');

    if (curr_stats['BET'].max_supply !== MAX_SUPPLY) {
        throw_error("Invalid currency max supply", MAX_SUPPLY, curr_stats['BET'].max_supply);
    }
});

new_check('System accounts existing check', async () => {
    await Promise.all(SYSTEM_ACCOUNTS.map(async (acc) => {
        try {
            let acc_info = await rpc.get_account(acc);
        } catch (e) {
            throw_error(`Cannot fetch account ${acc}`, acc, 'unknown');
        }
    }));
});

new_check('System contracts existing check', async () => {
    await Promise.all(SYSTEM_CONTRACTS.map(async (acc) => {
        try {
            let contract_info = await rpc.get_raw_code_and_abi(acc);
            if (contract_info.wasm === "") {
                throw_error(`Invalid contract code for ${acc}`);
            }
        } catch (e) {
            throw_error(`Cannot fetch contract code for ${acc}`, acc, 'unknown');
        }
    }));
});

new_check('System contract version check', async () => {
    let rows = await rpc.get_table_rows({
        code: 'eosio',
        scope: 'eosio',
        table: 'version'
    });

    if (rows.rows[0].version !== SYSTEM_CONTRACT_VERSION) {
        throw_error('Invalid eosio contract version', SYSTEM_CONTRACT_VERSION, rows.rows[0].version);
    }
});

new_check('Claimed keys check', async () => {
    await Promise.all(funds.map(async (acc) => {
        let acc_info = await rpc.get_account(acc.name);
        let owner = acc_info.permissions.filter((perm) => perm.perm_name === 'owner')[0];
        let active = acc_info.permissions.filter((perm) => perm.perm_name === 'active')[0];

        if (owner.required_auth.keys.length !== 1) {
            throw_error(`Owner keys should contain only 1 key for ${acc.name}`, 1, owner.required_auth.keys);
        }
        if (owner.required_auth.waits.length !== 0) {
            throw_error(`Owner waits should be empty for ${acc.name}`, 'empty', owner.required_auth.waits);
        }
        if (active.required_auth.keys.length !== 1) {
            throw_error(`Active keys should contain only 1 key for ${acc.name}`, 1, owner.required_auth.keys);
        }
        if (active.required_auth.waits.length !== 0) {
            throw_error(`Active waits should be empty for ${acc.name}`, 'empty', owner.required_auth.waits);
        }
        if (owner.required_auth.accounts.length !== 0) {
            throw_error(`Owner accounts should be empty for ${acc.name}`, 'empty', owner.required_auth.accounts);
        }
        if (active.required_auth.accounts.length !== 0) {
            throw_error(`Owner accounts should be empty for ${acc.name}`, 'empty', owner.required_auth.accounts);
        }

        if (owner.required_auth.keys[0].weight !== 1) {
            throw_error(`Owner key invalid weight for ${acc.name}`, 1, owner.required_auth.keys[0].weight);
        }
        if (owner.required_auth.keys[0].key !== acc.pub_key) {
            throw_error(`Owner key invalid for ${acc.name}`, acc.pub_key, owner.required_auth.keys[0].key);
        }

        if (active.required_auth.keys[0].weight !== 1) {
            throw_error(`Active key invalid weight for ${acc.name}`, 1, active.required_auth.keys[0].weight);
        }
        if (active.required_auth.keys[0].key !== acc.pub_key) {
            throw_error(`Active key invalid for ${acc.name}`, acc.pub_key, active.required_auth.keys[0].key);
        }
    }));
});

new_check('Claimed balances check', async () => {
    await Promise.all(funds.map(async (acc) => {
        let acc_info;
        try {
            acc_info = await rpc.get_account(acc.name);
        } catch (e) {
            throw_error(`Cannot fetch account ${acc.name}`, acc.name, e.message);
        }

        let acc_balance = total_funds(acc_info);

        if (acc.type != "owner" && asset(acc.bet_liquid) !== acc_balance) {
            throw_error(`Invalid balance for ${acc.name}`, acc.bet_liquid, acc_balance);
        }
    }));
});

new_check('Bridge balance check', async () => {
    let sum = funds.reduce((accum, item) => accum + asset(item.bet_liquid));
    let to_bridge = asset(SUPPLY) - sum;

    let bridge_info;
    try {
        bridge_info = await rpc.get_account(BRIDGE_ACCOUNT);
    } catch (e) {
        throw_error(`Cannot fetch account ${BRIDGE_ACCOUNT}`, BRIDGE_ACCOUNT, 'unknown');
    }

    if (asset(bridge_info.core_liquid_balance) === to_bridge) {
        throw_error('Invalid bridge balance', to_bridge, asset(bridge_info.core_liquid_balance));
    }
});

new_check('Short names existing check', async () => {
    await Promise.all(SHORT_NAMES.map(async (acc) => {
        try {
            let acc_info = await rpc.get_account(acc);
        } catch (e) {
            throw_error(`Cannot fetch account ${acc}`, acc, 'unknown');
        }
    }));
});

new_check('Predefined tokens check', async () => {
    await Promise.all(TOKENS.map(async (tiker) => {
        try {
            let curr_stats = await rpc.get_currency_stats('eosio.token', tiker);
            if (curr_stats[tiker] === undefined) {
                throw_error("Cannot fetch token", tiker, 'undefined');
            }
        } catch (e) {
            throw_error(`Cannot fetch token ${tiker}`, tiker, e.message);
        }
    }));
});

new_check('Msig priveleged check', async () => {
    let msig_info = await rpc.get_account('eosio.msig');

    if (msig_info.privileged !== true) {
        throw_error('Msig not priveleged', true, false);
    }
});

new_check('Eosio priveleged check', async () => {
    let eosio_info = await rpc.get_account('eosio');

    if (eosio_info.privileged !== true) {
        throw_error('Eosio not priveleged', true, false);
    }
});

new_check('Permissions check', async () => {
    let accounts = SYSTEM_ACCOUNTS.concat(SHORT_NAMES);

    await Promise.all(accounts.map(async (acc) => {
        let acc_info = await rpc.get_account(acc);
        let owner = acc_info.permissions.filter((perm) => perm.perm_name === 'owner')[0];
        let active = acc_info.permissions.filter((perm) => perm.perm_name === 'active')[0];

        if (owner.required_auth.keys.length !== 0) {
            throw_error(`Owner keys should be empty for ${acc}`, 'empty', owner.required_auth.keys);
        }
        if (owner.required_auth.waits.length !== 0) {
            throw_error(`Owner waits should be empty for ${acc}`, 'empty', owner.required_auth.waits);
        }
        if (active.required_auth.keys.length !== 0) {
            throw_error(`Active keys should be empty for ${acc}`, 'empty', owner.required_auth.keys);
        }
        if (active.required_auth.waits.length !== 0) {
            throw_error(`Active waits should be empty for ${acc}`, 'empty', owner.required_auth.waits);
        }

        if (owner.parent !== "") {
            throw_error(`Invalid owner parent for ${acc}`, '', owner.parent);
        }
        if (active.parent !== "owner") {
            throw_error(`Invalid active parent for ${acc}`, 'owner', active.parent);
        }

        if (owner.required_auth.accounts.length !== 1) {
            throw_error(`Owner accounts should contain only 1 account for ${acc}`, 1, owner.required_auth.accounts);
        }
        if (owner.required_auth.accounts[0].weight !== 1) {
            throw_error(`Invalid owner weight for ${acc}`, 1, owner.required_auth.accounts[0].weight);
        }
        if (owner.required_auth.accounts[0].permission.actor !== 'eosio.prods') {
            throw_error(`Invalid owner permission for ${acc}`, 'eosio.prods', owner.required_auth.accounts[0].permission.actor);
        }
        if (owner.required_auth.accounts[0].permission.permission !== 'active') {
            throw_error(`Invalid owner permission for ${acc}`, 'active', owner.required_auth.accounts[0].permission.permission);
        }

        if (acc !== BRIDGE_ACCOUNT) {
            if (active.required_auth.accounts.length !== 1) {
                throw_error(`Active accounts should contain only 1 account for ${acc}`, 1, active.required_auth.accounts);
            }
            if (active.required_auth.accounts[0].weight !== 1) {
                throw_error(`Invalid active weight for ${acc}`, 1, active.required_auth.accounts[0].weight);
            }
            if (active.required_auth.accounts[0].permission.actor !== 'eosio.prods') {
                throw_error(`Invalid active permission for ${acc}`, 'eosio.prods', active.required_auth.accounts[0].permission.actor);
            }
            if (active.required_auth.accounts[0].permission.permission !== 'active') {
                throw_error(`Invalid active permission for ${acc}`, 'active', active.required_auth.accounts[0].permission.permission);
            }
        } else {
            if (active.required_auth.accounts.length !== 2) {
                throw_error(`Active accounts should contain only 2 account for ${acc}`, 2, active.required_auth.accounts);
            }
            let prods_perm = active.required_auth.accounts.filter(acc => acc.permission.actor === "eosio.prods")[0];
            let code_perm = active.required_auth.accounts.filter(acc => acc.permission.permission === "eosio.code")[0];

            if (!prods_perm) {
                throw_error(`Not found eosio.prods permission for ${acc}`);
            }
            if (!code_perm) {
                throw_error(`Not found eosio.code permission for ${acc}`);
            }
            if (prods_perm.weight !== 1) {
                throw_error(`Invalid active weight for ${acc}`, 1, prods_perm.weight);
            }
            if (prods_perm.permission.permission !== 'active') {
                throw_error(`Invalid active permission for ${acc}`, 'active', prods_perm.permission.permission);
            }
            if (code_perm.weight !== 1) {
                throw_error(`Invalid active weight for ${acc}`, 1, code_perm.weight);
            }
            if (code_perm.permission.actor !== acc) {
                throw_error(`Invalid active permission for ${acc}`, 'active', code_perm.permission.actor);
            }
        }
    }));
});

new_check('DAOBet owner balance check', async () => {
    let owner = funds.filter(acc => acc.type === "owner")[0];
    let owner_info = await rpc.get_account(owner.name);

    if (asset(owner.bet_liquid) - total_funds(owner_info) <= 0) {
        throw_error(`DAOBet owner(${owner.name}) have invalid balance`, `more than ${owner.bet_liquid}`, total_funds(owner_info))
    }
    if (asset(owner.bet_liquid) - total_funds(owner_info) > asset(DAO_MAX_RAM_SPENT)) {
        throw_error(`DAOBet owner(${owner.name}) have invalid balance`, `less than ${owner.bet_liquid - asset(DAO_MAX_RAM_SPENT)}`, total_funds(owner_info))
    }
});


(async () => {
    let fails = 0;
    for (let i = 0; i < checks.length; ++i) {
        let error = false;
        let error_text = '';
        try {
            process.stdout.write(`Running: '${checks[i].name}' ...`);
            await checks[i].check();
        } catch (e) {
            error = true;
            error_text = e.toString();
            fails++;
        }
        if (error) {
            console.log(`\x1b[31m FAILED\x1b[0m, details: '${error_text}'`);
        } else {
            console.log(`\x1b[32m OK\x1b[0m`);
        }
        if (process.env.STOP && error) {
            break;
        }
    }

    console.log('===============DONE================');
    console.log(`${checks.length - fails} checks passed`);
    console.log(`${fails} checks failed`);
    console.log('===================================');

    if (fails) {
        process.exit(1);
    }
})();