from odoo import models
import logging

_logger = logging.getLogger(__name__)


class Website(models.Model):
    _inherit = "website"

    def sale_get_order(self, *args, **kwargs):
        user = self.env.user
        if user.portal and user.partner_id.company_id:
            self = self.with_company(user.partner_id.company_id)
            _logger.info(f"Switching to company: {self.company_id.name}")
        order = super().sale_get_order(*args, **kwargs)
        return order
