# Copyright (c) 2025, JACQUES Chan Alex and Contributors
# See license.txt

# import frappe
from frappe.tests import IntegrationTestCase, UnitTestCase


# On IntegrationTestCase, the doctype test records and all
# link-field test record dependencies are recursively loaded
# Use these module variables to add/remove to/from that list
EXTRA_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]
IGNORE_TEST_RECORD_DEPENDENCIES = []  # eg. ["User"]


class UnitTestFile3QuotationRequestSupplier(UnitTestCase):
	"""
	Unit tests for File3QuotationRequestSupplier.
	Use this class for testing individual functions and methods.
	"""

	pass


class IntegrationTestFile3QuotationRequestSupplier(IntegrationTestCase):
	"""
	Integration tests for File3QuotationRequestSupplier.
	Use this class for testing interactions between multiple components.
	"""

	pass
