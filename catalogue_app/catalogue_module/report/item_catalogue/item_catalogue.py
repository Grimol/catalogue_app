# Copyright (c) 2025, Arthur Rouelle and contributors
# For license information, please see license.txt

import frappe
from typing import Any, Dict, List, Tuple

def execute(filters=None):
    columns, data = [], []
    
    CATALOGUE_DOCTYPE = "Catalogue"
    CHILD_DOCTYPE = "Univers Items"
    LEVEL_FIELD = "level"
    PARENT_FIELD = "parent_catalogue"
    ITEM_LINK_FIELD = "item"

    # Récupération des items
    items = frappe.get_all(
        "Item",
        filters={"disabled": 0},
        fields=["name", "item_name"],
    )
    if not items:
        return columns, data
    item_codes = [row.name for row in items]
    
    # Récupération des univers correspondant aux items
    links = frappe.get_all(
        CHILD_DOCTYPE,
        filters={
            ITEM_LINK_FIELD: ["in", item_codes]
        },
        fields=[ITEM_LINK_FIELD, "parent"]
    )

    # Charger les Univers + les catalogues parents
    univers_names = sorted({row.parent for row in links})
    univers_docs = frappe.get_all(
		CATALOGUE_DOCTYPE,
		filters={
			"name": ("in", univers_names),
			LEVEL_FIELD: "Univers"
		},
		fields=["name", PARENT_FIELD],
	)
    univers_to_catalogue = {doc.name: doc.parent_catalogue for doc in univers_docs}

	# Construction Item > Liste des catalogues
    item_to_catalogues: Dict[str, List[Tuple[str, str]]] = {code: [] for code in item_codes}
    for row in links:
        item_code = row.item
        univers = row.parent
        catalogue = univers_to_catalogue.get(univers)
        if not catalogue:
            continue
        item_to_catalogues[item_code].append((catalogue, univers))

	# Déterminer le nombre maximum de catalogues par item
    max_catalogues = max(len(catalogues) for catalogues in item_to_catalogues.values())
    
	# Construction des colonnes dynamiques
    columns = _build_columns(max_catalogues)
        
    # Construction du résultat final
    data = []
    for item in items:
        item_code = item.name
        nom = item.item_name
        pairs = item_to_catalogues.get(item_code, [])
        
        row = {
            "item_code": item_code,
			"designation": nom,
		}
        for index in range(max_catalogues):
            catalogue_key = f"catalogue_{index+1}"
            univers_key = f"univers_{index+1}"
            if index < len(pairs):
                row[catalogue_key] = pairs[index][0]
                row[univers_key] = pairs[index][1]
            else:
                row[catalogue_key] = ""
                row[univers_key] = ""
        data.append(row)
    return columns, data

def _build_columns(max_pairs: int):
    columns = [
        {"label": "Nom (Item Code)", "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 180},
        {"label": "Désignation", "fieldname": "designation", "fieldtype": "Data", "width": 250},
    ]

    for i in range(1, max_pairs + 1):
        columns.append({"label": f"Catalogue {i}", "fieldname": f"catalogue_{i}", "fieldtype": "Link", "options": "Catalogue", "width": 180})
        columns.append({"label": f"Univers {i}", "fieldname": f"univers_{i}", "fieldtype": "Link", "options": "Catalogue", "width": 180})

    return columns