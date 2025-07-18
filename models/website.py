from odoo import models


class Website(models.Model):
    _inherit = "website"

    def sale_get_order(
        self,
        force_create=False,
        code=None,
        update_pricelist=False,
        force_pricelist=False,
    ):
        # Llamamos super para obtener/crear el order standard (inicialmente en website.company_id)
        order = super().sale_get_order(
            force_create=force_create,
            code=code,
            update_pricelist=update_pricelist,
            force_pricelist=force_pricelist,
        )
        # Si es portal user y partner tiene company distinta, switchamos
        user = request.env.user
        if (
            order
            and user.portal
            and user.partner_id.company_id
            and order.company_id != user.partner_id.company_id
        ):
            # Usamos sudo y contexto para bypass validaciones iniciales
            order.sudo().with_context(
                company_id=user.partner_id.company_id.id
            ).company_id = user.partner_id.company_id
        return order
