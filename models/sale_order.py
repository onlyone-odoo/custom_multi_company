from odoo import api, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.constrains(
        "company_id", "partner_id", "partner_invoice_id", "partner_shipping_id"
    )
    def _check_company_id_out_model(self):
        for rec in self:
            if not rec.company_id:
                continue
            # Permitir si la company del partner es child de la del order
            for field_name in [
                "partner_id",
                "partner_invoice_id",
                "partner_shipping_id",
            ]:
                partner = rec[field_name]
                if (
                    partner
                    and partner.company_id
                    and partner.company_id.parent_id == rec.company_id
                ):
                    continue  # Bypass para childs
                # Llama al super para el resto
                super(SaleOrder, rec)._check_company_id_out_model()
