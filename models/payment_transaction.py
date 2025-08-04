from odoo import models


class PaymentTransaction(models.Model):
    _inherit = "payment.transaction"

    def _send_payment_notification(self):
        for tx in self:
            if tx.sale_order_id.website_id and tx.provider_code == "wire_transfer":
                continue  # Skip notificación para wire_transfer en website
            super(PaymentTransaction, tx)._send_payment_notification()
