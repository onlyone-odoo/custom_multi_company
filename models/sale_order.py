from odoo import models
from odoo.exceptions import UserError
from odoo.tools.translate import _
from odoo.tools.safe_eval import _lt  # Para _lt si no está importado
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _check_company(self, fnames=None):
        _logger.info("Entering _check_company for record IDs: %s", self.ids)
        if fnames is None:
            fnames = self._fields.keys()
        regular_fields = []
        property_fields = []
        for name in fnames:
            field = self._fields[name]
            if (
                field.relational
                and field.check_company
                and "company_id" in self.env[field.comodel_name]._fields
            ):
                if not field.company_dependent:
                    regular_fields.append(name)
                else:
                    property_fields.append(name)
        if not (regular_fields or property_fields):
            _logger.info("No fields to check, exiting early.")
            return
        inconsistencies = []
        for record in self:
            company = record.company_id if record._name != "res.company" else record
            _logger.info(
                "Checking record %s with company %s",
                record.display_name,
                company.display_name,
            )
            for name in regular_fields:
                corecords = record.sudo()[name]
                if corecords:
                    _logger.info(
                        "Field %s: corecords companies %s",
                        name,
                        [c.company_id.display_name for c in corecords],
                    )
                    bypassed = False
                    if name in [
                        "partner_id",
                        "partner_invoice_id",
                        "partner_shipping_id",
                    ]:
                        for corecord in corecords:
                            if (
                                corecord.company_id
                                and corecord.company_id.parent_path
                                and f"{record.company_id.id}/"
                                in corecord.company_id.parent_path
                            ):
                                bypassed = True
                                _logger.info(
                                    "Bypassing %s for child company %s",
                                    name,
                                    corecord.company_id.display_name,
                                )
                                break  # Si al menos uno es child, bypass (ajusta si querés estrictamente todos)
                    if not bypassed:
                        domain = corecords._check_company_domain(company)
                        if domain and corecords != corecords.with_context(
                            active_test=False
                        ).filtered_domain(domain):
                            inconsistencies.append((record, name, corecords))
                            _logger.warning(
                                "Inconsistency found in %s for record %s",
                                name,
                                record.display_name,
                            )
            company = self.env.company
            for name in property_fields:
                corecords = record.sudo()[name]
                if corecords:
                    _logger.info(
                        "Property field %s: corecords companies %s",
                        name,
                        [c.company_id.display_name for c in corecords],
                    )
                    bypassed = False
                    if name in [
                        "partner_id",
                        "partner_invoice_id",
                        "partner_shipping_id",
                    ]:
                        for corecord in corecords:
                            if (
                                corecord.company_id
                                and corecord.company_id.parent_path
                                and f"{company.id}/" in corecord.company_id.parent_path
                            ):
                                bypassed = True
                                _logger.info(
                                    "Bypassing property %s for child company %s",
                                    name,
                                    corecord.company_id.display_name,
                                )
                                break
                    if not bypassed:
                        domain = corecords._check_company_domain(company)
                        if domain and corecords != corecords.with_context(
                            active_test=False
                        ).filtered_domain(domain):
                            inconsistencies.append((record, name, corecords))
                            _logger.warning(
                                "Inconsistency in property %s for record %s",
                                name,
                                record.display_name,
                            )
        if inconsistencies:
            _logger.error("Inconsistencies detected: %s", inconsistencies)
            lines = [_("Incompatible companies on records:")]
            company_msg = _lt(
                "- Record is company %(company)r and %(field)r (%(fname)s: %(values)s) belongs to another company."
            )
            record_msg = _lt(
                "- %(record)r belongs to company %(company)r and %(field)r (%(fname)s: %(values)s) belongs to another company."
            )
            root_company_msg = _lt(
                "- Only a root company can be set on %(record)r. Currently set to %(company)r"
            )
            for record, name, corecords in inconsistencies[:5]:
                if record._name == "res.company":
                    msg, company = company_msg, record
                elif record == corecords and name == "company_id":
                    msg, company = root_company_msg, record.company_id
                else:
                    msg, company = record_msg, record.company_id
                field = self.env["ir.model.fields"]._get(self._name, name)
                lines.append(
                    str(msg)
                    % {
                        "record": record.display_name,
                        "company": company.display_name,
                        "field": field.field_description,
                        "fname": field.name,
                        "values": ", ".join(
                            repr(rec.display_name) for rec in corecords
                        ),
                    }
                )
            raise UserError("\n".join(lines))
        _logger.info("No inconsistencies after bypass, check passed.")
