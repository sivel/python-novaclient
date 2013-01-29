# Copyright 2013 Hewlett-Packard Development Company, L.P.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
Baremetal interface (v2 extension).
"""

import urllib

from novaclient import base
from novaclient import utils


class BareMetalNode(base.Resource):
    """
    A baremetal node (typically a physical server or an empty VM).
    """

    def __repr__(self):
        return "<BareMetalNode: %s>" % self.id


class BareMetalNodeInterface(base.Resource):
    """
    An interface belonging to a baremetal node.
    """

    def __repr__(self):
        return "<BareMetalNodeInterface: %s>" % self.id


class BareMetalNodeManager(base.ManagerWithFind):
    """
    Manage :class:`BareMetalNode` resources.
    """
    resource_class = BareMetalNode

    def create(self,
               service_host,
               cpus,
               memory_mb,
               local_gb,
               prov_mac_address,
               pm_address=None,
               pm_user=None,
               pm_password=None,
               prov_vlan_id=None,
               terminal_port=None):
        """
        Create a baremetal node.

        :param service_host: Name of controlling compute host
        :param cpus: Number of CPUs in the node
        :param memory_mb: Megabytes of RAM in the node
        :param local_gb: Gigabytes of local storage in the node
        :param pm_address: Power management IP for the node
        :param pm_user: Username for the node's power management
        :param pm_password: Password for the node's power management
        :param prov_mac_address: MAC address to provision the node
        :param prov_vlan_id: VLAN ID to use to provision the node
        :param terminal_port: ShellInABox port
        :rtype: :class:`BareMetalNode`
        """
        body = {'node': {'service_host': service_host,
                        'cpus': cpus,
                        'memory_mb': memory_mb,
                        'local_gb': local_gb,
                        'pm_address': pm_address,
                        'pm_user': pm_user,
                        'pm_password': pm_password,
                        'prov_mac_address': prov_mac_address,
                        'prov_vlan_id': prov_vlan_id,
                        'terminal_port': terminal_port}}

        return self._create('/os-baremetal-nodes', body, 'node')

    def delete(self, node):
        """
        Delete a baremetal node.

        :param node: The :class:`BareMetalNode` to delete.
        """
        self._delete('/os-baremetal-nodes/%s' % base.getid(node))

    def get(self, node_id):
        """
        Get a baremetal node.

        :param node_id: The ID of the node to delete.
        :rtype: :class:`BareMetalNode`
        """
        return self._get("/os-baremetal-nodes/%s" % node_id, 'node')

    def list(self):
        """
        Get a list of all baremetal nodes.

        :rtype: list of :class:`BareMetalNode`
        """
        return self._list('/os-baremetal-nodes', 'nodes')

    def add_interface(self, node_id, address, datapath_id=0, port_no=0):
        """
        Add an interface to a baremetal node.

        :param node_id: The ID of the node to modify.
        :param address: The MAC address to add.
        :param datapath_id: Datapath ID of OpenFlow switch for the interface
        :param port_no: OpenFlow port number for the interface
        :rtype: :class:`BareMetalNodeInterface`
        """
        body = {'add_interface': {'address': address,
                                  'datapath_id': datapath_id,
                                  'port_no': port_no}}
        url = '/os-baremetal-nodes/%s/action' % node_id
        _resp, body = self.api.client.post(url, body=body)
        return BareMetalNodeInterface(self, body['interface'])

    def remove_interface(self, node_id, address):
        """
        Remove an interface from a baremetal node.

        :param node_id: The ID of the node to modify.
        :param address: The MAC address to remove.
        :rtype: bool
        """
        req_body = {'remove_interface': {'address': address}}
        url = '/os-baremetal-nodes/%s/action' % node_id
        self.api.client.post(url, body=req_body)


@utils.arg('service_host',
    metavar='<service_host>',
    help='Name of nova compute host which will control this baremetal node')
@utils.arg('cpus',
    metavar='<cpus>',
    type=int,
    help='Number of CPUs in the node')
@utils.arg('memory_mb',
    metavar='<memory_mb>',
    type=int,
    help='Megabytes of RAM in the node')
@utils.arg('local_gb',
    metavar='<local_gb>',
    type=int,
    help='Gigabytes of local storage in the node')
@utils.arg('prov_mac_address',
    metavar='<prov_mac_address>',
    help='MAC address to provision the node')
@utils.arg('--pm_address', default=None,
    metavar='<pm_address>',
    help='Power management IP for the node')
@utils.arg('--pm_user', default=None,
    metavar='<pm_user>',
    help='Username for the node\'s power management')
@utils.arg('--pm_password', default=None,
    metavar='<pm_password>',
    help='Password for the node\'s power management')
@utils.arg('--prov_vlan_id', default=None,
    metavar='<prov_vlan_id>',
    type=int,
    help='VLAN ID to use to provision the node')
@utils.arg('--terminal_port', default=None,
    metavar='<terminal_port>',
    type=int,
    help='ShellInABox port?')
def do_baremetal_node_create(cs, args):
    """Create a baremetal node"""
    return cs.baremetal.create(args.service_host, args.cpus,
            args.memory_mb, args.local_gb, args.prov_mac_address,
            pm_address=args.pm_address, pm_user=args.pm_user,
            pm_password=args.pm_password,
            prov_vlan_id=args.prov_vlan_id,
            terminal_port=args.terminal_port)


@utils.arg('node',
    metavar='<node>',
    help='ID of the node to delete.')
def do_baremetal_node_delete(cs, args):
    """Remove a volume."""
    node = _find_baremetal_node(cs, args.node)
    cs.baremetal.delete(node)


def _translate_baremetal_node_keys(collection):
    convert = [('service_host', 'host'),
               ('local_gb', 'disk_gb'),
               ('prov_mac_address', 'mac_address'),
               ('prov_vlan_id', 'vlan'),
               ('pm_address', 'pm_address'),
               ('pm_user', 'pm_username'),
               ('pm_password', 'pm_password'),
               ('terminal_port', 'terminal_port'),
               ]
    for item in collection:
        keys = item.__dict__.keys()
        for from_key, to_key in convert:
            if from_key in keys and to_key not in keys:
                setattr(item, to_key, item._info[from_key])


def _print_baremetal_nodes_list(cs, nodes):
    """Print the list of baremetal nodes"""
    _translate_baremetal_node_keys(nodes)
    utils.print_list(nodes, [
        'ID',
        'Host',
        'CPUs',
        'Memory_MB',
        'Disk_GB',
        'MAC Address',
        'VLAN',
        'PM Address',
        'PM Username',
        'PM Password',
        'Terminal Port',
        ])


def do_baremetal_node_list(cs, _args):
    """Print a list of available baremetal nodes."""
    nodes = cs.baremetal.list()
    _print_baremetal_nodes_list(cs, nodes)


def _find_baremetal_node(cs, node):
    """Get a node by ID."""
    return utils.find_resource(cs.baremetal, node)


def _print_baremetal_node(cs, node):
    """Print the details of a baremetal node"""
    info = node._info.copy()
    utils.print_dict(info)


@utils.arg('node',
     metavar='<node>',
     help="ID of node")
def do_baremetal_node_show(cs, args):
    """Show information about a node"""
    node = _find_baremetal_node(cs, args.node)
    _print_baremetal_node(cs, node)


@utils.arg('node',
    metavar='<node>',
    help="ID of node")
@utils.arg('address',
    metavar='<address>',
    help="MAC address of interface")
@utils.arg('--datapath_id',
    default=0,
    metavar='<datapath_id>',
    help="OpenFlow Datapath ID of interface")
@utils.arg('--port_no',
    default=0,
    metavar='<port_no>',
    help="OpenFlow port number of interface")
def do_baremetal_add_interface(cs, args):
    """Add a network interface to a baremetal node"""
    return cs.baremetal.add_interface(args.node, args.address,
            args.datapath_id, args.port_no)


@utils.arg('node', metavar='<node>', help="ID of node")
@utils.arg('address', metavar='<address>', help="MAC address of interface")
def do_baremetal_remove_interface(cs, args):
    """Remove a network interface from a baremetal node"""
    cs.baremetal.remove_interface(args.node, args.address)
