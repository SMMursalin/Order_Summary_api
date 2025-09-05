from odoo import http
from odoo.http import request

class OrderSummaryController(http.Controller):

    @http.route('/api/v1/order-summary', type='json', auth='user', methods=['POST'], csrf=False)
    def order_summary(self, **kwargs):
        """
        Optimized SQL version for large datasets (50k+ lines).
        Filters:
          - delivery_ids (list of picking IDs)
          - product_templates (list of template IDs)
        """

        delivery_ids = kwargs.get("delivery_ids", [])
        product_templates = kwargs.get("product_templates", [])

        # Base SQL
        sql = """
            SELECT so.id AS order_id,
                   so.name AS order_name,
                   rp.name AS customer,
                   so.date_order,
                   so.amount_total,
                   sol.id AS line_id,
                   pt.name AS product,
                   sol.product_uom_qty,
                   sol.price_unit,
                   sol.price_subtotal
            FROM sale_order so
            JOIN res_partner rp ON so.partner_id = rp.id
            JOIN sale_order_line sol ON sol.order_id = so.id
            JOIN product_product pp ON sol.product_id = pp.id
            JOIN product_template pt ON pp.product_tmpl_id = pt.id
        """

        # Build WHERE conditions
        conditions = []
        params = []

        if delivery_ids:
            sql += " JOIN stock_picking sp ON sp.id = ANY(%s) AND sp.id = ANY(so.picking_ids)"
            params.append(delivery_ids)

        if product_templates:
            conditions.append("pp.product_tmpl_id = ANY(%s)")
            params.append(product_templates)

        if conditions:
            sql += " WHERE " + " AND ".join(conditions)

        # Execute query
        request.env.cr.execute(sql, tuple(params))
        rows = request.env.cr.dictfetchall()

        # Group results by order
        result = {}
        for row in rows:
            oid = row["order_id"]
            if oid not in result:
                result[oid] = {
                    "order_id": oid,
                    "name": row["order_name"],
                    "customer": row["customer"],
                    "date_order": row["date_order"],
                    "amount_total": row["amount_total"],
                    "lines": [],
                }
            result[oid]["lines"].append({
                "line_id": row["line_id"],
                "product": row["product"],
                "qty": row["product_uom_qty"],
                "price_unit": row["price_unit"],
                "subtotal": row["price_subtotal"],
            })

        return {"status": "success", "data": list(result.values())}
