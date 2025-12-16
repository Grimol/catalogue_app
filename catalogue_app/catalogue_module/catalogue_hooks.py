def item_on_update(doc, method=None):
    if doc.disabled:
        doc.is_sales_item = 0
        doc.is_purchase_item = 0