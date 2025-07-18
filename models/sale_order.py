from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _check_company_domain(self, company, field=None):
        self.ensure_one()
        if field and field.name in [
            "partner_id",
            "partner_invoice_id",
            "partner_shipping_id",
        ]:
            if not company:
                return True
            if company == self.company_id:
                return True
            # Permitir si la company del partner es child (descendiente) de la del order
            if (
                self.company_id
                and company.parent_path
                and f"{self.company_id.id}/" in company.parent_path
            ):
                return True
            return False
        return super()._check_company_domain(company, field=field)
