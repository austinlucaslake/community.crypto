#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2024, Austin Lucas Lake <53884490+austinlucaslake@users.noreply.github.com>
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: gpg_keypair
author: "Austin Lucas Lake (@austinlucaslake)"
short_description: Generate or delete GPG private and public keys
version_added: 2.20.0
description:
    - "This module allows one to generate or delete GPG private and public keys using GnuPG (gpg)."
requirements:
    - gpg >= 2.1
    - python-dateutil
extends_documentation_fragment:
  - community.crypto.attributes
attributes:
    check_mode:
        support: full
    diff_mode:
        support: none
options:
    state:
        description:
            - Whether the private and public keys should exist or not, taking action if the state is different from what is stated.
            - This module will fail if O(state=present), and neither O(name), O(comment), or O(email) are provided.
            - This module will fail if O(state=present), and neither O(name), O(comment), O(email), O(fingerprints) are provided.
        type: str
        default: present
        choices: [ present, absent ]
    key_type:
        description:
            - Specifies the type of key to create.
        type: str
        choices: [ 'RSA', 'DSA', 'ECDSA', 'EDDSA' ]
    key_size:
        description:
            - For non-ECC keys, this specifies the number of bits in the key to create.
            - If O(key_type=RSA), the minimum is V(1024), the maximum is V(4096), and the default is V(3072).
            - IF O(key_type=DSA), the minimum is V(768), the maximum is V(3072), and the default is V(2048).
            - As per GPG's behavior, values below the allowed ranges will be set to the respective defaults, and values above will saturate at the maximum.
        type: int
        aliases:
            - key_length
    key_curve:
        description:
            - For ECC keys, this specifies the curve used to generate the keys.
            - If O(key_type=EDDSA), O(key_curve=ed25519) is required.
            - If O(key_curve=ed25519) is only supported if O(key_type=EDDSA).
            - This parameter is required if O(key_type=ECDSA) or O(key_type=EDDSA).
            - This parameter is ignored if O(key_type=RSA) or O(key_type=DSA).
            - This module will fail if an unsupported O(key_curve) is provided for the given O(key_type).
        type: str
        choices: [ 'nistp256', 'nistp384', 'nistp521', 'brainpoolP256r1', 'brainpoolP384r1', 'brainpoolP512r1', 'secp256k1', 'ed25519' ]
    key_usage:
        description:
            - Specifies usage(s) for key.
            - V(cert) is given to all primary keys regardess, however can be used to only give V(vert) usage to a key.
            - If O(key_usage) is not specified, all of valid usages for the given O(key_type) are assigned.
            - O(key_usage=encr) is only supported if O(key_type=RSA).
            - This module will fail if an unsupported O(key_usage) is provided for the given O(key_type).
        type: list
        elements: str
        default: []
        choices: [ 'encr', 'sign', 'auth', 'cert' ]
    subkeys:
        description:
            - List of subkeys with their own respective key types, lengths, curves, and usages.
        type: list
        elements: dict
        default: []
        suboptions:
            key_type:
                description:
                 - Similar to O(key_type).
                 - Also supports ECDH and ELG keys.
                type: str
                choices: [ 'RSA', 'DSA', 'ECDSA', 'EDDSA', 'ECDH', 'ELG' ]
            key_size:
                description:
                    - Similar to O(key_size).
                    - If O(subkeys[].key_type=ELG), the minimum is V(1024) bits, the maximum is V(4096) bits, and the default is V(3072) bits.
                type: int
                aliases:
                    - key_length
            key_curve:
                description:
                    - Similar to O(key_curve).
                    - O(subkeys[].key_curve=cv25519) is supported if O(subkeys[].key_type=ECDH).
                    - This parameter is required if O(subkeys[].key_type) is V(ECDSA), V(EDDSA), or V(ECDH).
                    - This parameter is ignored if O(subkeys[].key_type) is V(RSA), V(DSA), or V(ELG).
                    - This module will fail if an unsupported O(subkeys[].key_curve) is provided for the given O(subkeys[].key_type).
                type: str
                choices: ['nistp256', 'nistp384', 'nistp521', 'brainpoolP256r1', 'brainpoolP384r1', 'brainpoolP512r1', 'secp256k1', 'ed25519', 'cv25519']
            key_usage:
                description:
                    - Similar to O(key_usage).
                    - V(encr) is supported if O(subkeys[].key_type) is V(RSA), V(ECDH), or V(ELG).
                    - If O(subkeys[].key_type) is V(ECDH) or V(ELG), only V(encr) is supported.
                    - This module will fail if an unsupported O(subkeys[].key_usage) is provided for the given O(subkeys[].key_type).
                type: list
                elements: str
                default: []
                choices: [ 'encr', 'sign', 'auth' ]
    expire_date:
        description:
            - Sets the expire date for the key.
            - If O(expire_date=0), the key never expires.
            - If O(expire_date=<n>), the key expires in V(n) days.
            - If O(expire_date=<n>w), the key expires in V(n) weeks.
            - If O(expire_date=<n>m), the key expires in V(n) months.
            - If O(expire_date=<n>y), the key expires in V(n) years.
            - Also excepts dates in ISO formats.
            - If left unspecified, any created GPG keys never expire.
            - This module will fail if an unsupported format for O(expire_date) is provided.
            - This module will fail if O(expire_date) is provided, the python-dateutil package is not found, and O(install_python_dateutil=false).
            - This module will fail if O(expire_date) is provided, the python-dateutil package is not found, O(install_python_dateutil=true), and check_mode is enabled.
        type: str
    name:
        description:
            - Specifies a name for the key's user ID.
        type: str
    comment:
        description:
            - Specifies a comment for the key's user ID.
        type: str
    email:
        description:
            - Specifies an email for the key's user ID.
        type: str
    passphrase:
        description:
            - Passphrase used to decrypt an existing private key or encrypt a newly generated private key.
        type: str
    fingerprints:
        description:
            - Specifies keys to match against.
        type: list
        elements: str
        default: []
    force:
        description:
            - If O(force=true), key generation is executed using the module's options, even a matching key is found.
            - This parameter does not override V(check_mode).
            - This parameter is ignored if O(state=absent).
        type: bool
        default: true
    install_python_dateutil:
        description:
            - Specifies whether or not to try to install python-dateutil package if not found.
        type: str
notes:
    - If a user ID is provided, the module's options are matched against all keys with said user ID.
    - Matched parameters only include those in which an user has specified.
    - If a fingerprint is provided but no user ID is provided, the module's options are matched against the fingerprint(s).
    - If neither a fingerprint or user ID is provided, the module's options are matched against all keys.
'''

EXAMPLES = '''
- name: Generate the default GPG keypair
  community.crypto.gpg_keypair:

- name: Generate the default GPG keypair with a passphrase
  community.crypto.gpg_keypair:
    passphrase: '{{ passphrase }}'

- name: Generate a RSA GPG keypair with the default RSA size (2048 bits)
  community.crypto.gpg_keypair:
    key_type: RSA

- name: Generate a RSA GPG keypair with custom size (4096 bits)
  community.crypto.gpg_keypair:
    key_type: RSA
    key_size: 4096

-~/.local/share/nvim/swap/ name: Generate an ECC GPG keypair
  community.crypto.gpg_keypair:
    key_type: EDDSA
    key_curve: ed25519

- name: Generate a GPG keypair and with a subkey
  community.crypto.gpg_keypair:
    subkeys:
        - { key_type: ECDH, key_curve: cv25519 }

- name: Generate a GPG keypair with custom user-id
  community.crypto.gpg_keypair:
    name: name
    comment: comment
    email: name@email.com

- name: Delete a GPG keypair matching a specified fingerprint
  community.crypto.gpg_keypair:
    state: absent
    fingerprints:
      - ABC123...
'''

RETURN = '''
changed:
    description: Indicates if changes were made to GPG keyring.
    returned: success
    type: bool
    sample: True
fingerprints:
    description: Fingerprint(s) of matching, created, or deleted primary key(s).
    returned: success
    type: list
    elements: str
    sample: [ ABC123... ]
'''

from itertools import chain, permutations
import re
import sys

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.common.process import get_bin_path
from ansible.module_utils.common.respawn import has_respawned, respawn_module

def all_permutations(arr):
    return list(chain.from_iterable(
        permutations(arr, i + 1)
        for i in range(len(arr))))


def key_type_from_algo(algo):
    if algo == 1:
        return 'RSA'
    elif algo == 16:
        return 'ELG'
    elif algo == 17:
        return 'DSA'
    elif algo == 18:
        return 'ECDH'
    elif algo == 19:
        return 'ECDSA'
    elif algo == 22:
        return 'EDDSA'


def expand_usages(usages):
    usages = list(usages)
    for i in range(len(usages)):
        if usages[i] == 'c':
            usages[i] = 'cert'
        elif usages[i] == 's':
            usages[i] = 'sign'
        elif usages[i] == 'a':
            usages[i] = 'auth'
        elif usages[i] == 'e':
            usages[i] = 'encr'
    return usages


def validate_key(module, key_type, key_curve, key_usage, key_name='primary key'):
    if key_type == 'EDDSA':
        if key_curve and key_curve != 'ed25519':
            module.fail_json('Invalid key_curve for {0} {1}.'.format(key_type, key_name))
        elif key_usage and tuple(key_usage) not in all_permutations(['sign', 'auth', 'cert']):
            module.fail_json('Invalid key_usage for {0} {1}.'.format(key_type, key_name))
        pass
    elif key_type == 'ECDH':
        if key_curve:
            if key_curve not in ['nistp256', 'nistp384', 'nistp521', 'brainpoolP256r1', 'brainpoolP384r1', 'brainpoolP512r1', 'secp256k1', 'cv25519']:
                module.fail_json('Invalid curve for {0} {1}.'.format(key_type, key_name))
        elif key_usage and key_usage != ['encr']:
            module.fail_json('Invalid key_usage for {0} {1}.'.format(key_type, key_name))
        pass
    elif key_type == 'ECDSA':
        if key_curve and key_curve not in ['nistp256', 'nistp384', 'nistp521', 'brainpoolP256r1', 'brainpoolP384r1', 'brainpoolP512r1', 'secp256k1']:
            module.fail_json('Invalid key_curve for {0} {1}.'.format(key_type, key_name))
        elif key_usage and tuple(key_usage) not in all_permutations(['sign', 'auth', 'cert']):
            module.fail_json('Invalid key_usage for {0} {1}.'.format(key_type, key_name))
        pass
    elif key_type == 'RSA':
        if key_usage and tuple(key_usage) not in all_permutations(['encr', 'sign', 'auth', 'cert']):
            module.fail_json('Invalid key_usage for {0} {1}.'.format(key_type, key_name))
        pass
    elif key_type == 'DSA':
        if key_usage and tuple(key_usage) not in all_permutations(['sign', 'auth', 'cert']):
            module.fail_json('Invalid key_usage for {0} {1}.'.format(key_type, key_name))
        pass
    elif key_type == 'ELG':
        if key_usage and key_usage != ['encr']:
            module.fail_json('Invalid key_usage for {0} {1}.'.format(key_type, key_name))
        pass


def delete_keypair(module, matching_keys, check_mode):
    if matching_keys:
        module.run_command(
            [
                '--dry-run' if check_mode else None,
                '--batch',
                '--yes',
                '--delete-secret-and-public-key'
            ] + matching_keys,
            executable=get_bin_path('gpg'),
            check_rc=True
        )
    return dict(changed=bool(matching_keys), fingerprints=matching_keys)


def generate_keypair(module, params, matching_keys, check_mode):
    if matching_keys and not params['force']:
        return dict(changed=False, fingerprints=matching_keys)

    parameters = '''
        {0}
        {1}
        {2}
        {3}
        {4}
        {5}
        {6}
        {7}
        %commit
        '''.format(
        'Key-Type: {0}'.format(params['key_type'] if params['key_type'] else 'default'),
        'Key-Length: {0}'.format(params['key_size']) if params['key_size'] else '',
        'Key-Curve: {0}'.format(params['key_curve']) if params['key_curve'] else '',
        'Expire-Date: {0}'.format(params['expire_date']) if params['expire_date'] else '',
        'Name-Real: {0}'.format(params['name']) if params['name'] else '',
        'Name-Comment: {0}'.format(params['comment']) if params['comment'] else '',
        'Name-Email: {0}'.format(params['email']) if params['email'] else '',
        'Passphrase: {0}'.format(params['passphrase']) if params['passphrase'] else '%no-protection',
    )

    rc, stdout, stderr = module.run_command(
        [
            '--dry-run' if check_mode else None,
            '--batch',
            '--gen-key',
        ],
        data=parameters,
        executable=get_bin_path('gpg'),
        check_rc=True
    )

    fingerprint = re.search(r'([0-9A-Z]+)\.rev', stderr).group(1)

    for subkey in params['subkeys']:
        if subkey['key_type'] in ['RSA', 'DSA', 'ELG']:
            algo = subkey['key_type'].lower()
            if subkey['key_size']:
                algo += str(subkey['key_size'])
        elif subkey['key_curve']:
            algo = subkey['key_curve']
        else:
            algo = 'default'

        module.run_command(
            [
                '--dry-run' if check_mode else None,
                '--batch',
                '--passphrase {0}'.format(params['passphrase'] if params['passphrase'] else ''),
                '--quick-add-key',
                fingerprint,
                algo,
                ' '.join(subkey['key_usage']),
                params['expire_date'] if params['expire_date'] else None
            ],
            executable=get_bin_path('gpg')
        )

    return dict(changed=True, fingerprint=[fingerprint])


def run_module(module, params, check_mode=False):
    if params['expire_date']:
        try:
            import dateutil.parser as dp
            dp.isoparse(params['expire_date'])
        except ImportError:
            if params['install_python_dateutil']:
                apt_pkg_name = 'python-dateutil'
                if has_respawned():
                    module.fail_json(msg="{0} must be installed and visible from {1}.".format(apt_pkg_name, sys.executable))
                elif module.check_mode:
                    module.fail_json("{} must be installed to use check mode. If run normally this module can auto-install it.".format(apt_pkg_name))

                else:
                    module.run_command(
                        ['-m', 'pip', 'install', apt_pkg_name],
                        executable=sys.executable
                        check_rc=True
                    )
                    respawn_module(sys.executable) # process will exit here once respawned module has completed
            else:
                module.fail_json('An expire date was specified, but the python-dateutil package was not found and install_python_dateutil=false.')
        except ValueError:
            if not (params['expire_date'].isnumeric() or (params['expire_date'][:-1].isnumeric() and params['expire_date'][-1] in ['w', 'm', 'y'])):
                module.fail_json('Invalid format for expire date.')

    validate_key(module, params['key_type'], params['key_curve'], params['key_usage'])
    for i, subkey in enumerate(params['subkeys']):
        validate_key(module, subkey['key_type'], subkey['key_curve'], subkey['key_usage'], 'subkey #{0}'.format(i + 1))

    uid = ''
    if params['name']:
        uid += '{0} '.format(params['name'])
    if params['comment']:
        uid += '({0}) '.format(params['comment'])
    if params['email']:
        uid += '<{0}>'.format(params['email'])
    uid = uid.strip()

    rc, stdout, stderr = module.run_command(
        ['--list-secret-keys', uid] + params['fingerprints'],
        executable=get_bin_path('gpg')
    )

    fingerprints = list(set([line.strip() for line in stdout.splitlines() if line.strip().isalnum()]))
    matching_keys = []
    for fingerprint in fingerprints:
        rc, stdout, stderr = module.run_command(
            ['--list-secret-keys', '--with-colons', fingerprint],
            executable=get_bin_path('gpg'),
            check_rc=True
        )

        subkey_index = 0
        uid_present = not bool(uid)
        for line in stdout.splitlines():
            if line[:3] == 'sec':
                primary_key = re.search(r'.+u:([0-9]+):([0-9]+):.+:([a-z]+)[A-Z]+.+\+:+([0-9a-zA-Z]+).+', line)
                key_type = key_type_from_algo(int(primary_key.group(2)))
                key_size = int(primary_key.group(1))
                key_curve = primary_key.group(4)
                key_usage = expand_usages(primary_key.group(3))

                if params['key_type'] and params['key_type'] != key_type:
                    break
                elif params['key_usage'] and tuple(params['key_usage']) not in permutations(key_usage):
                    break
                elif key_type in ['RSA', 'DSA', 'ELG']:
                    if params['key_size'] and params['key_size'] != key_size:
                        break
                else:
                    if params['key_curve'] and params['key_curve'] != key_curve:
                        break

            elif line[:3] == 'uid':
                if uid == re.search(r'.+:(.{{{0}}}):+0:'.format(len(line) - 75), line).group(1):
                    uid_present = True

            elif line[:3] == 'ssb':
                subkey_index += 1
                if subkey_index >= len(params['subkeys']):
                    break

                subkey = re.search(r'.+:([0-9]+):([0-9]+):.+([a-z]+):.+([0-9a-zA-Z]+)::', line)
                key_type = key_type_from_algo(int(subkey.group(2)))
                key_size = int(subkey.group(1))
                key_curve = subkey.group(4)
                key_usage = expand_usages(subkey.group(3))

                if params['subkeys'][subkey_index]['key_type'] and params['subkeys'][subkey_index]['sub_type'] != key_type:
                    break
                elif params['subkeys'][subkey_index]['key_usage'] and tuple(params['subkeys'][subkey_index]['key_usage']) not in permutations(key_usage):
                    break
                elif key_type in ['RSA', 'DSA', 'ELG']:
                    if params['subkeys'][subkey_index]['key_size'] and params['subkeys'][subkey_index]['key_size'] != key_size:
                        break
                else:
                    if params['subkeys'][subkey_index]['key_curve'] and params['subkeys'][subkey_index]['key_curve'] != key_curve:
                        break
        else:
            if uid_present:
                matching_keys.append(fingerprint)

    if params['state'] == 'present':
        result = generate_keypair(module, params, matching_keys, check_mode)
    else:
        result = delete_keypair(module, matching_keys, check_mode)
    return result


def main():
    key_types = ['RSA', 'DSA', 'ECDSA', 'EDDSA', 'ECDH', 'ELG']
    key_curves = ['nistp256', 'nistp384', 'nistp521', 'brainpoolP256r1', 'brainpoolP384r1', 'brainpoolP512r1', 'secp256k1', 'ed25519', 'cv25519']
    key_usages = ['encr', 'sign', 'auth', 'cert']

    module = AnsibleModule(
        argument_spec=dict(
            state=dict(type='str', default='present', choices=['present', 'absent']),
            key_type=dict(type='str', choices=key_types[:-2]),
            key_size=dict(type='int', aliases=['key_length'], no_log=False),
            key_curve=dict(type='str', choices=key_curves[:-1]),
            key_usage=dict(type='list', elements='str', default=[], choices=key_usages),
            subkeys=dict(
                type='list',
                elements='dict',
                no_log=False,
                default=[],
                options=dict(
                    key_type=dict(type='str', choices=key_types),
                    key_size=dict(type='int', aliases=['key_length'], no_log=False),
                    key_curve=dict(type='str', choices=key_curves),
                    key_usage=dict(type='list', elements='str', default=[], choices=key_usages[:-1])
                ),
                required_if=[
                    ['key_type', 'ECDSA', ['key_curve']],
                    ['key_type', 'EDDSA', ['key_curve']],
                    ['key_type', 'ECDH', ['key_curve']],
                ]
            ),
            expire_date=dict(type='str'),
            name=dict(type='str'),
            comment=dict(type='str'),
            email=dict(type='str'),
            passphrase=dict(type='str', no_log=True),
            fingerprints=dict(type='list', elements='str', default=[]),
            force=dict(type='bool', default=False),
            install_python_dateutil=dict(type='bool', default=True)
        ),
        supports_check_mode=True,
        required_if=[
            ['state', 'present', ['name', 'comment', 'email'], True],
            ['state', 'absent', ['name', 'comment', 'email', 'fingerprints'], True],
            ['key_type', 'ECDSA', ['key_curve']],
            ['key_type', 'EDDSA', ['key_curve']],
        ]
    )

    try:
        results = run_module(module, module.params, module.check_mode)
        module.exit_json(**results)
    except Exception as e:
        module.fail_json(str(e))


if __name__ == '__main__':
    main()
