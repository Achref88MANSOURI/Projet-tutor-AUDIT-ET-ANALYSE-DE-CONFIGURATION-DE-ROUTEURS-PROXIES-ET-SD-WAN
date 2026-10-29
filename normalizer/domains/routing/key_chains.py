"""Routing key-chain identities and non-secret key metadata only."""
from normalizer.common.collections import collection
from schemas import router_contract_v1 as s


def handle(state, record):
    root = record if record['rule'] == 'auth_key_chain' else state.root(record)
    if not root or root['rule'] != 'auth_key_chain':
        return
    chains = collection(state.c.routing, 'key_chains')
    chain = next((c for c in chains if c.name == root['values']['name']), None)
    if chain is None:
        chain = s.KeyChain(name=root['values']['name'])
        chains.append(chain)
    path = f'routing/key_chains/{chains.index(chain)}'
    state.bind(path + '/name', root['source_line'])
    if record['rule'] == 'auth_key_chain':
        return
    key_record = record if record['rule'] == 'auth_key_id' else state.records.get(record['context_lines'][-1])
    if not key_record or key_record['rule'] != 'auth_key_id':
        return
    keys = collection(chain, 'keys')
    key = next((k for k in keys if k.identifier == key_record['values']['key_id']), None)
    if key is None:
        key = s.KeyChainKey(identifier=key_record['values']['key_id'])
        keys.append(key)
    path += f'/keys/{keys.index(key)}'
    state.bind(path + '/identifier', key_record['source_line'])
    if record['rule'].startswith('auth_key_string'):
        state.assign(key, 'secret_configured', True, path, record['source_line'])
        if 'credential_format' in record['values']:
            state.assign(key, 'credential_format', record['values']['credential_format'], path, record['source_line'])
        else:
            state.unbind(path + '/credential_format')
            key.credential_format = None
    elif record['rule'] == 'auth_key_algorithm':
        state.assign(key, 'cryptographic_algorithm', record['values']['algorithm'], path, record['source_line'])
