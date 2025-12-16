frappe.treeview_settings["Catalogue"] = {
    get_tree_nodes: "catalogue_app.catalogue_module.doctype.catalogue.catalogue.get_children",
    add_tree_node: "catalogue_app.catalogue_module.doctype.catalogue.catalogue.add_node",
    title: "Catalogues",
};