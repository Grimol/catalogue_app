# Copyright (c) 2025, Arthur Rouelle and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import cint

from typing import Any

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

@frappe.whitelist()
def get_item_catalogue_links(item_code):
	links = frappe.get_all("Item Catalogue Link",
		filters={"item_code": item_code},
		fields=["catalogue"])

	return [link.catalogue for link in links]

@frappe.whitelist()
def get_catalogues_for_item(item_code: str) -> list[dict[str, Any]]:
    print("Getting catalogues for item:", item_code)
    CATALOGUE_DOCTYPE = "Catalogue"
    LEVEL_FIELD = "level"
    PARENT_FIELD = "parent_catalogue"
    ACTIVE_FIELD = "is_active"
    VISIBLE_FIELD = "is_website_visible"

    # Récupération des univers liés à l'article
    univers_rows = frappe.get_all(
        "Univers Items",
        fields=["item", "item_name", "parent"],
        distinct=True
    )
    univers_rows = list(filter(lambda row: row.item == item_code, univers_rows))
    if not univers_rows:
        return []
    univers_names = [row.parent for row in univers_rows]

    # Récupération des catalogues correspondant aux univers
    univers_docs = frappe.get_all(
        CATALOGUE_DOCTYPE,
        filters={
            LEVEL_FIELD: "Univers",
            ACTIVE_FIELD: 1,
            "name": ["in", univers_names]
        },
        fields=["name", PARENT_FIELD, VISIBLE_FIELD]
    )
    
    # Organisation des univers par catalogue parent
    univers_by_catalogue: dict[str, list[tuple[str, bool]]] = {}
    for univers in univers_docs:
        if not univers.get(PARENT_FIELD):
            continue
        univers_by_catalogue.setdefault(univers.parent_catalogue, []).append((univers.name, univers.is_website_visible))
    if not univers_by_catalogue:
        return []

    # Récupération des catalogues parents actifs et visibles
    catalogue_docs = frappe.get_all(
        CATALOGUE_DOCTYPE,
        filters={
            "name": ("in", list(univers_by_catalogue.keys())),
            ACTIVE_FIELD: 1,
            LEVEL_FIELD: "Catalogue"
        },
        fields=["name", VISIBLE_FIELD],
    )
    visibles = {c["name"]: int(c.get(VISIBLE_FIELD) or 0) for c in catalogue_docs}

    # Construction du résultat final
    result = []
    for catalogue_name, univers_list in univers_by_catalogue.items():
        if catalogue_name not in visibles:
            continue
        result.append({
            "catalogue": catalogue_name,
            "is_website_visible": visibles[catalogue_name],
            "univers": univers_list
        })
    return result