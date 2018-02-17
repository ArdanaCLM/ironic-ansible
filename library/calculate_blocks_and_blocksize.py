#!/usr/bin/python
#
# (c) Copyright 2018 SUSE LLC
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['preview'],
    'supported_by': 'SuSE'
}

DOCUMENTATION = '''
---
module: calculate_blocks_and_blocksize

short_description: Calculate the blocks and blocksize of a given file.

version_added: "1.9"

description:
    - This action module will determine the blocks and blocksize of the
      the given file. The algorithm is taken from

      https://github.com/openSUSE/kiwi/blob/master/modules/KIWIImage.pm#L4549

      It will return two integers. The first is the number of blocks and
      the second is the blocksize for each block.

options:
    filename:
        description:
            - The complete path the file in question
        required: true

extends_documentation_fragment:
    -

author:
    - Guang Yee (guang.yee@suse.com)
'''

EXAMPLES = '''
- name: ironic-common | _suse_add_cert_iso | Calculate blocks and blocksize
  calculate_blocks_and_blocksize:
    file: "{{ openstack_ironic_image_gz }}"
  register: calculate_blocks_and_blocksize_result
'''

RETURN = '''
blocks:
    description: Number of blocks in the given file.
    type: int
blocksize:
    description: Size of each block
    type: int
'''

from ansible.module_utils.basic import *


def calculate_blocks_and_blocksize(filename):
    statinfo = os.stat(filename)
    size = statinfo.st_size
    factors_out = subprocess.check_output(['factor', str(size)])
    factors = factors_out.split(':')[1].split()
    blocksize = 1
    for factor in factors:
        factor = int(factor)
        if blocksize * factor > 65464:
            break
        blocksize *= factor
    blocks = size / blocksize
    return (blocks, blocksize)


def run_module():
    # define the available arguments/parameters that a user can pass to
    # the module
    module_args = dict(
        filename=dict(type='str', required=True),
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # change is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
        original_message='',
        message='',
        blocks=None,
        blocksize=None
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        return result

    # manipulate or modify the state as needed (this is going to be the
    # part where your module will do what it needs to do)
    filename = module.params.get('filename')

    try:
        (blocks, blocksize) = calculate_blocks_and_blocksize(filename)
        result['blocks'] = blocks
        result['blocksize'] = blocksize
    except Exception, e:
        module.fail_json(msg=e.message)
    else:
        module.exit_json(**result)


def main():
    run_module()

if __name__ == '__main__':
    main()
