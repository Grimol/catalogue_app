# Copyright (c) 2025, Arthur Rouelle and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

from typing import Any


class Catalogue(Document):
	pass

@frappe.whitelist()
def get_active_catalogues(doctype: set, parent: str | None = None, is_root: Any = None):
	print("Fetching active catalogues...")
	return frappe.get_all('Catalogue', filters={'is_active': '1'}, fields=['title', 'is_active'])