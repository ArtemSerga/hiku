from __future__ import unicode_literals

import pytest

from hiku.query import Node, Field, Link
from hiku.protobuf import query_pb2 as t
from hiku.readers.protobuf import read, transform

from .base import reqs_eq_patcher


def check_read(pb_node, expected):
    query = read(pb_node.SerializeToString())
    with reqs_eq_patcher():
        assert query == expected


def test_node_field():
    node = t.Node()
    item = node.items.add()
    item.field.name = 'tratan'
    check_read(node, Node([Field('tratan')]))


def test_node_field_options():
    node = t.Node()
    item = node.items.add()
    item.field.name = 'sprayed'
    item.field.options['treason'].integer = 123
    item.field.options['prizren'].string = 'stager'
    check_read(node, Node([Field('sprayed', {'treason': 123,
                                             'prizren': 'stager'})]))


def test_link():
    node = t.Node()
    link_item = node.items.add()
    link_item.link.name = 'swaying'
    field_item = link_item.link.node.items.add()
    field_item.field.name = 'pelew'
    check_read(node, Node([Link('swaying', Node([Field('pelew')]))]))


def test_link_options():
    node = t.Node()
    link_item = node.items.add()
    link_item.link.name = 'dubiety'
    link_item.link.options['squat'].integer = 234
    link_item.link.options['liquid'].string = 'ravages'
    link_item.link.options['schlitt'].repeated_integer.items[:] = [345, 456]
    link_item.link.options['nuntius'].repeated_string.items[:] = ['queue',
                                                                  'ylem']
    field_item = link_item.link.node.items.add()
    field_item.field.name = 'gits'
    check_read(node, Node([Link('dubiety', Node([Field('gits')]),
                                {'squat': 234,
                                 'liquid': 'ravages',
                                 'schlitt': [345, 456],
                                 'nuntius': ['queue', 'ylem']})]))


def test_empty_option():
    node = t.Node()
    link_item = node.items.add()
    link_item.link.name = 'dubiety'
    assert link_item.link.options['wud']
    with pytest.raises(TypeError) as err:
        check_read(node, Node([]))
    err.match('Option value is not set')


def test_no_field_name():
    node = t.Node()
    item = node.items.add()
    item.field.CopyFrom(t.Field())
    with pytest.raises(TypeError) as err:
        transform(node)
    err.match('Field name is empty')


def test_no_link_name():
    node = t.Node()
    item = node.items.add()
    item.link.CopyFrom(t.Link())
    with pytest.raises(TypeError) as err:
        transform(node)
    err.match('Link name is empty')


def test_no_node_item():
    node = t.Node()
    node.items.add()
    with pytest.raises(TypeError) as err:
        transform(node)
    err.match('Node item is empty')
