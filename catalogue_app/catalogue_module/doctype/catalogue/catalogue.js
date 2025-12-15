// Copyright (c) 2025, Arthur Rouelle and contributors
// For license information, please see license.txt

frappe.ui.form.on("Catalogue", {
 	refresh(frm) {
        // Afficher la liste des univers si le niveau est "Catalogue"
        if(frm.doc.level !== "Catalogue" || frm.is_new()) return;

        frappe.db.get_list("Catalogue", {
            fields: ["name", "title"],
            filters: {
                parent_catalogue: frm.doc.name
            },
            order_by: "title asc",
            limit: 100
        }).then(children => {
            if(!children.length){
                frm.fields_dict.univers_list_html.$wrapper.html(
                    "<div>Aucun univers</div>"
                );
                return;
            }
            const items = children
                .map(child => `<li><a href="/app/catalogue/${child.name}">${frappe.utils.escape_html(child.title)}</a></li>`)
                .join("");
            frm.fields_dict.univers_list_html.$wrapper.html(
                `<div><b>Univers</b><ul>${items}</ul></div>`
            );
        });

        // Sécurité pour forcer la cohérence entre le niveau et is_group
        if (frm.doc.level === "Catalogue" && !frm.doc.is_group) {
            frm.set_value("is_group", 1);
        }
        if (frm.doc.level === "Univers" && frm.doc.is_group) {
            frm.set_value("is_group", 0);
        }
	},

    // Forcer le rafraîchissement de la vue lorsque le niveau change
    level(frm) {
        if (frm.doc.level === "Catalogue") {
            frm.set_value("is_group", 1);
        } else if ( frm.doc.level === "Univers") {
            frm.set_value("is_group", 0);
        }
        frm.refresh();
    }
});