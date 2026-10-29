"""Identity, AAA, management lines, NTP, syslog and system services."""
from ipaddress import ip_address
from . import aaa_administration
from normalizer.common.collections import collection
from schemas import router_contract_v1 as s
from normalizer.common.validation import boolean


def handle(state,r):
    rule, v, line = (r['rule'], r['values'], r['source_line'])
    if rule.startswith('admin_') or rule in ('services_ssh_version', 'services_auth_address', 'services_auth_ports'):
        return aaa_administration.handle(state, r)
    if rule in ('services_ntp_source','services_logging_trap'):
        state.defer(r)
        return
    system = state.c.system
    if rule == 'services_hostname':
        state.assign(system.identity, 'hostname', v['hostname'], 'system/identity', line)
    elif rule == 'services_version':
        state.assign(state.c.device, 'software_version', v['version'], 'device', line)
    elif rule in ('services_domain', 'services_domain_alt'):
        state.assign(system.identity, 'domain_name', v['domain'], 'system/identity', line)
    elif rule == 'services_dns':
        values = [str(ip_address(value)) for value in v['addresses'].split()]
        for value in values:
            collection(system.dns, 'servers').append(value)
            state.bind(f'system/dns/servers/{len((system.dns.servers or [])) - 1}', line)
    elif rule.startswith('services_ntp') and rule != 'services_ntp_source':
        collection(system.ntp, 'servers').append(s.NTPServer(address=v['address'], prefer=True if rule.endswith('prefer') else None, network_instance=v.get('vrf')))
        state.bind(f'system/ntp/servers/{len((system.ntp.servers or [])) - 1}', line)
    elif rule in ('services_logging', 'services_logging_legacy'):
        collection(system.logging, 'destinations').append(s.SyslogDestination(address=v['address']))
        state.bind(f'system/logging/destinations/{len((system.logging.destinations or [])) - 1}', line)
    elif rule in ('services_aaa_on', 'services_aaa_off'):
        state.assign(system.aaa, 'enabled', boolean(v['enabled']), 'system/aaa', line)
    elif rule.startswith('services_user') and v['credential_type'] in ('secret', 'password'):
        collection(system.aaa, 'local_users').append(s.UserAccount(username=v['username'], privilege_level=v.get('privilege'), credential_configured=True, credential_type=v['credential_type'] + ':' + v['credential_format']))
        state.bind(f'system/aaa/local_users/{len((system.aaa.local_users or [])) - 1}', line)
    elif rule.startswith('services_snmp_community') and v['access'].lower() in ('ro', 'rw'):
        collection(system.snmp, 'communities').append(s.SNMPCommunity(identifier_redacted=True, access=v['access'].lower(), access_list=v.get('acl')))
        state.bind(f'system/snmp/communities/{len((system.snmp.communities or [])) - 1}', line)
    elif rule in ('services_snmp_location', 'services_snmp_contact'):
        state.assign(system.snmp, 'location' if rule.endswith('location') else 'contact', v['value'], 'system/snmp', line)
    elif rule in ('services_http_on', 'services_http_off', 'services_https_on', 'services_https_off'):
        service = 'https' if 'https' in rule else 'http'
        state.assign(getattr(system.management, service), 'enabled', boolean(v['enabled']), 'system/management/' + service, line)
    elif rule in ('services_transport', 'services_timeout', 'services_timeout_minutes', 'services_access_class', 'services_login', 'services_login_plain'):
        entry = state.entity(line)
        if not entry or not isinstance(entry[0], s.ManagementLine):
            return
        item, path = entry
        if rule == 'services_transport':
            tokens = v['transports'].split()
            if any((x not in ('ssh', 'telnet', 'none', 'all') for x in tokens)):
                return
            if ('all' in tokens or 'none' in tokens) and len(tokens) != 1:
                return
            state.assign(item, 'allowed_transports', [] if tokens == ['none'] else tokens, path, line, explicit_empty=tokens == ['none'])
        elif rule.startswith('services_timeout'):
            seconds = v.get('seconds', 0)
            if not 0 <= seconds <= 59:
                raise ValueError('Invalid timeout')
            state.assign(item, 'idle_timeout_seconds', v['minutes'] * 60 + seconds, path, line)
        elif rule == 'services_access_class' and v['direction'] == 'in':
            state.assign(item, 'access_list', v['acl'], path, line)
        elif rule == 'services_login':
            state.assign(item, 'authentication', authentication(v['method']), path, line)
            state.validation[line]['fields']['method'] = 'validated'
        elif rule == 'services_login_plain':
            state.assign(item, 'authentication', s.Authentication(method='line_password'), path, line)
    else:
        pass
    fields = {
        'services_login_logging': ('logging', 'login_success_logging', 'enabled'),
        'services_logging_source': ('logging', 'source_interface', 'interface'),
        'services_console_off': ('logging', 'console_logging', 'enabled'),
        'services_source_route_off': ('ip_services', 'source_routing', 'enabled'),
        'services_lookup_off': ('dns', 'lookup_enabled', 'enabled'),
        'services_password_encryption_off': ('ip_services', 'password_encryption_service', 'enabled'),
        'services_password_encryption_on': ('ip_services', 'password_encryption_service', 'enabled'),
        'services_ipv6_routing': ('ip_services', 'ipv6_unicast_routing', 'enabled'),
    }
    if rule in fields:
        owner, field, key = fields[rule]
        state.assign(getattr(system, owner), field, v[key], 'system/' + owner, line, list(v))
    v = r['values']
    line = r['source_line']
    rule = r['rule']
    if rule.startswith('services_timestamp'):
        obj = s.TimestampPolicy(category=v['category'], format=v['format'], options=v.get('options', '').split())
        collection(state.c.system.logging, 'timestamps').append(obj)
        if 'options' in v:
            state.validation[line]['fields']['options'] = 'validated'
        state.bind('system/logging/timestamps', line, list(v))
    elif rule == 'services_banner':
        node = state.nodes[line]
        # The inventory carries only an explicit presence marker, never banner text.
        present = getattr(node, 'text_present', None)
        collection(state.c.system.identity, 'banners').append(s.Banner(type=v['type'], text_present=present))
        state.bind('system/identity/banners', line, list(v))
    elif rule == 'services_http_auth':
        state.assign(system.management.http, 'authentication', v['method'], 'system/management/http', line, list(v))
    elif rule.startswith('services_line_'):
        root = state.root(r)
        if root is None or root['rule'] != 'services_line':
            return
        obj = next((o for o in (state.c.system.management.lines or []) if o.name == root['values']['name']))
        path = f'system/management/lines/{(state.c.system.management.lines or []).index(obj)}'
        pair = {'services_line_synchronous': ('logging_synchronous', 'enabled'), 'services_line_privilege': ('privilege_level', 'level'), 'services_line_stopbits': ('stopbits', 'bits'), 'services_line_length': ('screen_length', 'length')}.get(rule)
        if pair:
            state.assign(obj, pair[0], v[pair[1]], path, line, list(v))
        elif rule == 'services_line_preferred':
            tokens = v['transports'].split()
            if any((t not in ('none', 'all', 'ssh', 'telnet') for t in tokens)):
                raise ValueError('Transport protocol')
            state.assign(obj, 'preferred_transports', [] if tokens == ['none'] else tokens, path, line, list(v), explicit_empty=tokens == ['none'])
    elif rule == 'services_community_expanded':
        obj = next((c for c in (state.c.routing_policies.community_lists or []) if c.name == v['name']), None)
        if obj is None:
            obj = s.CommunityList(name=v['name'],dialect='cisco_expanded_regex')
            collection(state.c.routing_policies, 'community_lists').append(obj)
        collection(obj, 'entries').append(s.CommunityListEntry(action=v['action'], expression=v['expression']))
        # Retain a native Cisco expression as text, without evaluating it as Python regex.
        state.validation[line]['fields']['expression'] = 'validated'
        state.bind(f'routing_policies/community_lists/{(state.c.routing_policies.community_lists or []).index(obj)}', line, list(v))
    elif rule.startswith('services_flow_'):
        if system.flow_monitoring.export is None:
            system.flow_monitoring.export = s.FlowExport()
        flow_export(state, r)


def flow_export(state, r):
    rule, v, line = r['rule'], r['values'], r['source_line']
    if rule == 'services_flow_source':
        state.assign(state.c.system.flow_monitoring.export, 'source_interface', v['interface'], 'system/flow_monitoring/export', line, list(v))
    elif rule == 'services_flow_version':
        state.c.system.flow_monitoring.export.version = v['version']
        state.c.system.flow_monitoring.export.as_mode = v['as_mode']
        state.bind('system/flow_monitoring/export', line, list(v))
    elif rule == 'services_flow_timeout':
        field = {'active': 'cache_timeout_active_minutes', 'inactive': 'cache_timeout_inactive_seconds'}.get(v['type'])
        if field is None:
            raise ValueError('Flow timeout mode')
        state.assign(state.c.system.flow_monitoring.export, field, v['timeout'], 'system/flow_monitoring/export', line, list(v))



def declare(state,r):
    rule,v,line=r['rule'],r['values'],r['source_line']
    if rule == 'services_line':
        item = s.ManagementLine(name=v['name'])
        collection(state.c.system.management, 'lines').append(item)
        path = f'system/management/lines/{len((state.c.system.management.lines or [])) - 1}'
        state.entities[line] = path
        state.bind(path + '/name', line)
        return True
    if rule in ('services_tacacs', 'services_radius'):
        return aaa_administration.server_declare(state, r)
    if rule == 'admin_aaa_group':
        return aaa_administration.group_declare(state, r)
    return False


def authentication(value):
    if value=='local':return s.Authentication(method='local')
    if value.startswith('authentication '):return s.Authentication(method='aaa',method_list=value[len('authentication '):])
    return None


def resolve(state,r):
    line, v = r['source_line'], r['values']
    if r['rule'] == 'services_ntp_source':
        state.assign(state.c.system.ntp, 'source_interface', v['source'], 'system/ntp', line)
    elif r['rule'] == 'services_logging_trap':
        state.assign(state.c.system.logging, 'trap_severity', v['severity'], 'system/logging', line)
