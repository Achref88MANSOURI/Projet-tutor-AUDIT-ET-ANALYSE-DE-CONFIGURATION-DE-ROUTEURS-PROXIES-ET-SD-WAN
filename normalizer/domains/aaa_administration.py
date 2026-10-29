"""Direct canonical AAA and SSH mappings; no inferred service activation."""
from normalizer.common.collections import collection
from normalizer.common.configured import leaves
from schemas import router_contract_v1 as s

PROTOCOL = {'radius': 'radius', 'tacacs+': 'tacacs'}
SIMPLE = {
    ('authentication','login'): {'local','local-case','enable','line','none','krb5','krb5-telnet','passwd-expiry'},
    ('authentication','enable'): {'enable','line','none'},
    ('authorization','exec'): {'local','none','if-authenticated'},
    ('authorization','commands'): {'local','none','if-authenticated'},
    ('accounting','exec'): set(), ('accounting','commands'): set(), ('accounting','system'): set(),
}


def methods(text, category, service):
    tokens = text.split()
    result = []
    index = 0
    while index < len(tokens):
        token = tokens[index]
        if token == 'group':
            index += 1
            if index == len(tokens) or tokens[index] in SIMPLE[(category, service)] | {'group','ldap','cache'}:
                raise ValueError('Incomplete or unsupported AAA group method')
            group = tokens[index]
            result.append(s.AAAMethod(method='group', group_protocol=PROTOCOL.get(group),
                                      group_reference=None if group in PROTOCOL else group))
        elif token in SIMPLE[(category, service)]:
            result.append(s.AAAMethod(method=token))
        else:
            raise ValueError('Unsupported AAA method; no partial method list is exported')
        index += 1
    if category == 'authentication' and len(result) > 4:
        raise ValueError('AAA authentication supports at most four methods')
    return result


def _publish(state, path, record):
    from normalizer.common.contexts import at
    pointer = '/' + path.strip('/')
    current = at(state.c, pointer)
    valid = {p for p, _ in leaves(current, pointer)}
    state.bindings[:] = [b for b in state.bindings if not b.path.startswith(pointer + '/') or b.path in valid]
    state.bind(pointer, record['source_line'], list(record['values']))


def method_list(state, record):
    _, category, service, *_ = record['rule'].split('_')
    values = record['values']
    mode = values.get('accounting_mode', 'none' if record['rule'].endswith('_none') else None)
    parsed = methods(values.get('methods', ''), category, service)
    if not parsed and not (category == 'accounting' and mode == 'none'):
        raise ValueError('An AAA method list must not be silently empty')
    removed = values.get('removed', False)
    field = category + '_method_lists'
    items = collection(state.c.system.aaa, field)
    key = values['name'], service, values.get('level')
    index = next((n for n, item in enumerate(items) if (item.name,item.service,item.privilege_level) == key), len(items))
    item = s.AAAMethodList(name=key[0], service=service, privilege_level=key[2],
                          accounting_mode=None if removed else mode,
                          methods=None if removed else parsed,
                          local_setting='removed' if removed else 'configured')
    if index == len(items):items.append(item)
    else:items[index] = item
    path = f'system/aaa/{field}/{index}'
    if not removed and parsed == []:
        state.absences.confirm(path + '/methods', explicit=True)
    _publish(state, path, record)


def server_declare(state, record):
    values = record['values']
    protocol = 'radius' if record['rule'] == 'services_radius' else 'tacacs'
    items = collection(state.c.system.aaa, 'servers')
    item = next((server for server in items if server.protocol == protocol and server.name == values['name']), None)
    if item is None:
        item = s.AuthServer(protocol=protocol, name=values['name'])
        items.append(item)
    path = f'system/aaa/servers/{items.index(item)}'
    state.entities[record['source_line']] = path
    _publish(state, path, record)
    return True


def group_declare(state, record):
    values = record['values']
    items = collection(state.c.system.aaa, 'server_groups')
    protocol = PROTOCOL[values['protocol']]
    item = next((group for group in items if group.name == values['name'] and group.protocol == protocol), None)
    if item is None:
        item = s.AAAServerGroup(name=values['name'], protocol=protocol)
        items.append(item)
    path = f'system/aaa/server_groups/{items.index(item)}'
    state.entities[record['source_line']] = path
    _publish(state, path, record)
    return True


def server_update(state, record):
    entry = state.entity(record['source_line'])
    if entry is None or not isinstance(entry[0], s.AuthServer):return
    item, path = entry
    values = record['values']
    if record['rule'] in ('services_auth_address','services_auth_ports'):
        item.address = values['address']
        if 'auth_port' in values:item.auth_port = values['auth_port']
        if 'acct_port' in values:item.accounting_port = values['acct_port']
    else:
        removed = values.get('removed', False)
        item.key_configured = not removed
        item.key_setting = 'removed' if removed else 'configured'
        item.key_format = None if removed else values.get('credential_format')
    _publish(state, path, record)


def ssh(state, record):
    item = state.c.system.management.ssh
    values = record['values']
    path = 'system/management/ssh'
    if record['rule'] == 'services_ssh_version':
        item.version = int(values['version'])
        item.version_setting = 'configured'
    elif record['rule'] == 'admin_ssh_version_remove':
        item.version = None
        item.version_setting = 'removed'
    elif record['rule'] == 'admin_ssh_timeout':item.timeout_seconds = values['seconds']
    elif record['rule'] == 'admin_ssh_retries':item.authentication_retries = values['retries']
    _publish(state, path, record)


def handle(state, record):
    rule = record['rule']
    if rule.startswith(('admin_authentication_','admin_authorization_','admin_accounting_')):
        return method_list(state, record)
    if rule.startswith('admin_ssh_') or rule == 'services_ssh_version':
        return ssh(state, record)
    if rule.startswith('admin_server_key') or rule in ('services_auth_address','services_auth_ports'):
        return server_update(state, record)
    if rule == 'admin_aaa_group_member':
        entry = state.entity(record['source_line'])
        if entry is None or not isinstance(entry[0], s.AAAServerGroup):return
        group, path = entry
        refs = collection(group, 'servers')
        if not any(ref.name == record['values']['name'] for ref in refs):
            refs.append(s.AAAServerReference(name=record['values']['name']))
        _publish(state, path, record)
