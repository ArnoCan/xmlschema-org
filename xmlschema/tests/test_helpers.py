#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c), 2016-2019, SISSA (International School for Advanced Studies).
# All rights reserved.
# This file is distributed under the terms of the MIT License.
# See the file 'LICENSE' in the root directory of the present
# distribution, or http://opensource.org/licenses/MIT.
#
# @author Davide Brunato <brunato@sissa.it>
#
"""
This module runs tests on various internal helper functions.
"""
from __future__ import unicode_literals

import unittest

from xmlschema.etree import etree_element
from xmlschema.namespaces import XSD_NAMESPACE, XSI_NAMESPACE
from xmlschema.helpers import get_xsd_annotation, iter_xsd_components, get_namespace, get_qname, \
    local_name, qname_to_prefixed, has_xsd_components, get_xsd_component, \
    get_xml_bool_attribute, get_xsd_derivation_attribute
from xmlschema.qnames import XSI_TYPE, XSD_SCHEMA, XSD_ELEMENT, XSD_SIMPLE_TYPE, XSD_ANNOTATION
from xmlschema.tests import XMLSchemaTestCase


class TestHelpers(XMLSchemaTestCase):

    def test_get_namespace_function(self):
        self.assertEqual(get_namespace(XSD_SIMPLE_TYPE), XSD_NAMESPACE)
        self.assertEqual(get_namespace(''), '')
        self.assertEqual(get_namespace(None), '')

    def test_get_qname_functions(self):
        self.assertEqual(get_qname(XSD_NAMESPACE, 'element'), XSD_ELEMENT)
        self.assertEqual(get_qname(XSI_NAMESPACE, 'type'), XSI_TYPE)

        self.assertEqual(get_qname(XSI_NAMESPACE, ''), '')
        self.assertEqual(get_qname(XSI_NAMESPACE, None), None)
        self.assertEqual(get_qname(XSI_NAMESPACE, 0), 0)
        self.assertEqual(get_qname(XSI_NAMESPACE, False), False)
        self.assertRaises(TypeError, get_qname, XSI_NAMESPACE, True)
        self.assertEqual(get_qname(None, True), True)

        self.assertEqual(get_qname(None, 'element'), 'element')
        self.assertEqual(get_qname(None, ''), '')
        self.assertEqual(get_qname('', 'element'), 'element')

    def test_local_name_functions(self):
        self.assertEqual(local_name(XSD_SCHEMA), 'schema')
        self.assertEqual(local_name('schema'), 'schema')
        self.assertEqual(local_name(''), '')
        self.assertEqual(local_name(None), None)

        self.assertRaises(ValueError, local_name, '{ns name')
        self.assertRaises(TypeError, local_name, 1.0)
        self.assertRaises(TypeError, local_name, 0)

    def test_qname_to_prefixed_functions(self):
        namespaces = {'xs': XSD_NAMESPACE, 'xsi': XSI_NAMESPACE}
        self.assertEqual(qname_to_prefixed(XSD_ELEMENT, namespaces), 'xs:element')
        self.assertEqual(qname_to_prefixed('xs:element', namespaces), 'xs:element')
        self.assertEqual(qname_to_prefixed('element', namespaces), 'element')

        self.assertEqual(qname_to_prefixed('', namespaces), '')
        self.assertEqual(qname_to_prefixed(None, namespaces), None)
        self.assertEqual(qname_to_prefixed(0, namespaces), 0)

        self.assertEqual(qname_to_prefixed(XSI_TYPE, {}), XSI_TYPE)
        self.assertEqual(qname_to_prefixed(None, {}), None)
        self.assertEqual(qname_to_prefixed('', {}), '')

        self.assertEqual(qname_to_prefixed('type', {'': XSI_NAMESPACE}), 'type')
        self.assertEqual(qname_to_prefixed('type', {'ns': ''}), 'ns:type')
        self.assertEqual(qname_to_prefixed('type', {'': ''}), 'type')

    def test_get_xsd_annotation(self):
        elem = etree_element(XSD_SCHEMA)

        self.assertIsNone(get_xsd_annotation(elem))
        elem.append(etree_element(XSD_ANNOTATION))
        self.assertEqual(get_xsd_annotation(elem), elem[0])
        elem.append(etree_element(XSD_ELEMENT))
        self.assertEqual(get_xsd_annotation(elem), elem[0])

        elem.clear()
        elem.append(etree_element(XSD_ELEMENT))
        self.assertIsNone(get_xsd_annotation(elem))
        elem.append(etree_element(XSD_ANNOTATION))
        self.assertIsNone(get_xsd_annotation(elem))

    def test_iter_xsd_components(self):
        elem = etree_element(XSD_SCHEMA)
        self.assertFalse(list(iter_xsd_components(elem)))
        self.assertFalse(list(iter_xsd_components(elem, start=1)))
        elem.append(etree_element(XSD_ANNOTATION))
        self.assertFalse(list(iter_xsd_components(elem)))
        self.assertFalse(list(iter_xsd_components(elem, start=1)))
        elem.append(etree_element(XSD_ELEMENT))
        self.assertEqual(list(iter_xsd_components(elem)), [elem[1]])
        elem.append(etree_element(XSD_SIMPLE_TYPE))
        self.assertEqual(list(iter_xsd_components(elem)), elem[1:])
        self.assertEqual(list(iter_xsd_components(elem, start=1)), [elem[2]])
        elem.append(etree_element(XSD_ANNOTATION))
        self.assertRaises(ValueError, list, iter_xsd_components(elem))

    def test_has_xsd_components(self):
        elem = etree_element(XSD_SCHEMA)
        elem.append(etree_element(XSD_ELEMENT))
        self.assertTrue(has_xsd_components(elem))

        elem.clear()
        self.assertFalse(has_xsd_components(elem))
        elem.append(etree_element(XSD_ANNOTATION))
        self.assertFalse(has_xsd_components(elem))
        elem.append(etree_element(XSD_ELEMENT))
        self.assertTrue(has_xsd_components(elem))
        self.assertFalse(has_xsd_components(elem, start=1))
        elem.append(etree_element(XSD_ANNOTATION))
        self.assertRaises(ValueError, list, iter_xsd_components(elem))

    def test_get_xsd_component(self):
        elem = etree_element(XSD_SCHEMA)
        self.assertRaises(ValueError, get_xsd_component, elem)
        self.assertIsNone(get_xsd_component(elem, required=False))
        elem.append(etree_element(XSD_ELEMENT))
        self.assertEqual(get_xsd_component(elem), elem[0])
        elem.append(etree_element(XSD_SIMPLE_TYPE))
        self.assertRaises(ValueError, get_xsd_component, elem)
        self.assertEqual(get_xsd_component(elem, strict=False), elem[0])

        elem.clear()
        elem.append(etree_element(XSD_ANNOTATION))
        self.assertRaises(ValueError, get_xsd_component, elem)
        self.assertIsNone(get_xsd_component(elem, required=False))
        elem.append(etree_element(XSD_SIMPLE_TYPE))
        self.assertEqual(get_xsd_component(elem), elem[1])
        elem.append(etree_element(XSD_ELEMENT))
        self.assertRaises(ValueError, get_xsd_component, elem)
        self.assertEqual(get_xsd_component(elem, strict=False), elem[1])

        elem.clear()
        elem.append(etree_element(XSD_ANNOTATION))
        elem.append(etree_element(XSD_ANNOTATION))
        self.assertRaises(ValueError, get_xsd_component, elem, True, False)

    def test_get_xml_bool_attribute(self):
        elem = etree_element(XSD_ELEMENT, attrib={'a1': 'true', 'a2': '1', 'a3': 'false', 'a4': '0', 'a5': 'x'})
        self.assertEqual(get_xml_bool_attribute(elem, 'a1'), True)
        self.assertEqual(get_xml_bool_attribute(elem, 'a2'), True)
        self.assertEqual(get_xml_bool_attribute(elem, 'a3'), False)
        self.assertEqual(get_xml_bool_attribute(elem, 'a4'), False)
        self.assertRaises(TypeError, get_xml_bool_attribute, elem, 'a5')
        self.assertRaises(KeyError, get_xml_bool_attribute, elem, 'a6')
        self.assertEqual(get_xml_bool_attribute(elem, 'a6', True), True)
        self.assertEqual(get_xml_bool_attribute(elem, 'a6', 'true'), True)
        self.assertEqual(get_xml_bool_attribute(elem, 'a6', '1'), True)
        self.assertEqual(get_xml_bool_attribute(elem, 'a6', False), False)
        self.assertEqual(get_xml_bool_attribute(elem, 'a6', 'false'), False)
        self.assertEqual(get_xml_bool_attribute(elem, 'a6', '0'), False)
        self.assertRaises(TypeError, get_xml_bool_attribute, elem, 'a6', 1)
        self.assertRaises(TypeError, get_xml_bool_attribute, elem, 'a6', 0)
        self.assertRaises(TypeError, get_xml_bool_attribute, elem, 'a6', 'True')

    def test_get_xsd_derivation_attribute(self):
        elem = etree_element(XSD_ELEMENT, attrib={
            'a1': 'extension', 'a2': ' restriction', 'a3': '#all', 'a4': 'other',
            'a5': 'restriction extension restriction ', 'a6': 'other restriction'
        })
        values = ('extension', 'restriction')
        self.assertEqual(get_xsd_derivation_attribute(elem, 'a1', values), 'extension')
        self.assertEqual(get_xsd_derivation_attribute(elem, 'a2', values), ' restriction')
        self.assertEqual(get_xsd_derivation_attribute(elem, 'a3', values), 'extension restriction')
        self.assertRaises(ValueError, get_xsd_derivation_attribute, elem, 'a4', values)
        self.assertEqual(get_xsd_derivation_attribute(elem, 'a5', values), 'restriction extension restriction ')
        self.assertRaises(ValueError, get_xsd_derivation_attribute, elem, 'a6', values)
        self.assertEqual(get_xsd_derivation_attribute(elem, 'a7', values), '')


if __name__ == '__main__':
    from xmlschema.tests import print_test_header

    print_test_header()
    unittest.main()
