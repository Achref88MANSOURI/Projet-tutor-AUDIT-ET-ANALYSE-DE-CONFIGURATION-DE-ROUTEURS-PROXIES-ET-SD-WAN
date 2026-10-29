"""Scrub administrative credentials before inventory and all TTP execution.

Keep names, declared formats and irreversible presence markers. The routing
redactor remains separate and unchanged. No secret-derived reference is made.
"""
import re

MARKER = '__ADMIN_SECRET_PRESENT__'
CREDENTIALS = (
    re.compile(r'^(?:no\s+)?username\s+\S+(?:\s+privilege\s+\d+)?\s+(?:password|secret)\s+', re.I),
    re.compile(r'^(?:no\s+)?enable\s+(?:password|secret)(?:\s+level\s+\d+)?\s+', re.I),
    re.compile(r'^(?:no\s+)?password\s+', re.I),
    re.compile(r'^(?:no\s+)?(?:radius-server|tacacs-server)\s+key\s+', re.I),
    re.compile(r'^(?:no\s+)?(?:radius-server|tacacs-server)\s+host\s+.+?\s+key\s+', re.I),
)


def redact_admin_secrets(text):
    result = []
    root = ''
    for raw in text.splitlines(keepends=True):
        value = raw.strip()
        if value and not value.startswith('!') and not raw[0].isspace():
            root = value
        community = re.match(r'^(snmp-server\s+community\s+)(\S+)(.*)$', value, re.I)
        if community:
            # Existing SNMP rules ignore the community value, but inventory and
            # official TTP must not receive it either. Preserve access/ACL syntax.
            indent = raw[:len(raw)-len(raw.lstrip())]
            ending = '\r\n' if raw.endswith('\r\n') else '\n' if raw.endswith('\n') else ''
            result.append(indent + community[1] + MARKER + community[3] + ending)
            continue
        prefix = None
        for pattern in CREDENTIALS:
            match = pattern.match(value)
            if match:
                prefix = match.end()
                break
        if prefix is None and re.match(r'^aaa group server (?:radius|tacacs\+) ', root, re.I):
            private = re.match(r'^(?:no\s+)?(?:server-private|server)\s+.+?\s+key\s+', value, re.I)
            if private:
                prefix = private.end()  # Redact unsupported legacy/private endpoints too.
        key = re.match(r'^(?:no\s+)?key\s+', value, re.I)
        if prefix is None and key and not root.lower().startswith('key chain '):
            # A routing key ID is not a credential. Within named AAA servers,
            # even a numeric one-word key is a secret and must be erased.
            payload = value[key.end():]
            named_server = re.match(r'^(?:radius|tacacs) server \S+$', root, re.I)
            if named_server or not payload.isdigit():
                prefix = key.end()
        if prefix is None:
            result.append(raw)
            continue
        payload = value[prefix:].strip()
        if not payload or payload == MARKER or re.fullmatch(r'\d+ ' + MARKER, payload):
            result.append(raw)
            continue
        tokens = payload.split(maxsplit=1)
        format_prefix = tokens[0] + ' ' if len(tokens) == 2 and tokens[0].isdigit() else ''
        indent = raw[:len(raw)-len(raw.lstrip())]
        ending = '\r\n' if raw.endswith('\r\n') else '\n' if raw.endswith('\n') else ''
        result.append(indent + value[:prefix] + format_prefix + MARKER + ending)
    return ''.join(result)
