# Copyright (c) 2025, Arthur Rouelle and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import cint


class Catalogue(Document):
	pass

@frappe.whitelist()
def get_children(doctype, parent=None, is_root=False):
	if is_root:
		parent = ""
	
	fields = ["name as value", "is_group as expandable"]
	filters = [
		["ifnull(`parent_catalogue`, '')", "=", parent],
		["is_active", "=", 1]]

	return frappe.get_list(doctype, fields=fields, filters=filters, order_by="name")

@frappe.whitelist()
def add_node():
	from frappe.desk.treeview import make_tree_args

	args = make_tree_args(**frappe.form_dict)
	if cint(args.is_root):
		args.parent_catalogue = None
	frappe.get_doc(args).insert()
