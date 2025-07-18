from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _check_company_domain(self, company):
        self.ensure_one()
        if (
            company
            and self.company_id
            and company.parent_path
            and f"{self.company_id.id}/" in company.parent_path
        ):
            return True
        return super()._check_company_domain(company)
