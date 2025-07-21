from odoo import models
import logging
_logger = logging.getLogger(__name__)

class Website(models.Model):
    _inherit = 'website'

    def sale_get_order(self, *args, **kwargs):
        user = self.env.user
        if user.has_group('base.group_portal') and user.partner_id.company_id:
            self = self.with_company(user.partner_id.company_id)
            _logger.info(f"Switching to company: {self.company_id.name}")
        order = super().sale_get_order(*args, **kwargs)
        return order

    def _complete_address_values(self, address_values, address_type, use_delivery_as_billing, order_sudo):
        user = self.env.user
        if user.has_group('base.group_portal') and user.partner_id.company_id:
            address_values['company_id'] = user.partner_id.company_id.id
            _logger.info(f"Setting address company_id to: {user.partner_id.company_id.name}")
        else:
            address_values['company_id'] = order_sudo.website_id.company_id.id
        return super()._complete_address_values(address_values, address_type, use_delivery_as_billing, order_sudo)
