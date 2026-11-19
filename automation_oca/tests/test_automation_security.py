# Copyright 2024 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import AccessError
from odoo.tests.common import users
from odoo.tools import mute_logger

from odoo.addons.mail.tests.common import mail_new_test_user

from .common import AutomationTestCase


class TestAutomationSecurity(AutomationTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Removing rules in order to check only what we expect
        cls.env["ir.access"].search(
            [("model_id", "=", cls.env.ref("base.model_res_partner").id)]
        ).action_archive()

        cls.user_automation_01 = mail_new_test_user(
            cls.env,
            login="user_automation_01",
            name="User automation 01",
            email="user_automation_01@test.example.com",
            company_id=cls.env.user.company_id.id,
            notification_type="inbox",
            groups="base.group_user,automation_oca.group_automation_user",
        )
        cls.user_automation_02 = mail_new_test_user(
            cls.env,
            login="user_automation_02",
            name="User automation 01",
            email="user_automation_02@test.example.com",
            company_id=cls.env.user.company_id.id,
            notification_type="inbox",
            groups="base.group_user,automation_oca.group_automation_user",
        )
        for number, user, partner in (
            ("G1", cls.user_automation_01, cls.partner_01),
            ("G2", cls.user_automation_02, cls.partner_02),
        ):
            group = cls.env["res.groups"].create(
                {"name": number, "user_ids": [(4, user.id)]}
            )
            # In Odoo 20 the group rules are ir.access records with a domain
            cls.env["ir.access"].create(
                {
                    "name": f"Rule {number}",
                    "model_id": cls.env.ref("base.model_res_partner").id,
                    "group_id": group.id,
                    "operation": "crud",
                    "domain": f"[('id', '!=', {partner.id})]",
                }
            )
            setattr(cls, f"group_{number[1]}", group)
        cls.configuration.editable_domain = [
            ("id", "in", (cls.partner_01 | cls.partner_02).ids)
        ]
        cls.configuration.start_automation()
        cls.env["automation.configuration"].cron_automation()

    @users("user_automation_01")
    def test_security_01(self):
        record = self.env["automation.record"].search(
            [("configuration_id", "=", self.configuration.id)]
        )
        self.assertEqual(1, len(record))
        self.assertEqual(self.partner_02, record.resource_ref)

    @users("user_automation_02")
    def test_security_02(self):
        record = self.env["automation.record"].search(
            [("configuration_id", "=", self.configuration.id)]
        )
        self.assertEqual(1, len(record))
        self.assertEqual(self.partner_01, record.resource_ref)

    @users("user_automation_01")
    @mute_logger("odoo.addons.automation_oca.models.automation_record")
    def test_security_deleted_record(self):
        self.env.user.group_ids = [(4, self.env.ref("base.group_system").id)]
        original_record = self.env["automation.record"].search(
            [("configuration_id", "=", self.configuration.id)]
        )
        self.partner_02.unlink()
        record = self.env["automation.record"].search(
            [("configuration_id", "=", self.configuration.id)]
        )
        self.assertTrue(record)
        self.assertTrue(record.is_orphan_record)
        self.assertTrue(original_record)
        self.assertTrue(original_record.read())

    @users("user_automation_01")
    def test_security_record_without_res_id(self):
        """A record without res_id has no document to check: only managers see it."""
        record = self.env["automation.record"].sudo().search(
            [("configuration_id", "=", self.configuration.id)], limit=1
        )
        record.write({"res_id": False})
        with self.assertRaises(AccessError):
            record.with_user(self.env.user).read(["name"])
        self.env.user.group_ids = [
            (4, self.env.ref("automation_oca.group_automation_manager").id)
        ]
        self.env.invalidate_all()
        self.assertTrue(record.with_user(self.env.user).read(["model"]))

    @users("user_automation_01")
    def test_security_search_record_without_model(self):
        """A record with no document at all is listed only for managers."""
        record = self.env["automation.record"].sudo().search(
            [("configuration_id", "=", self.configuration.id)], limit=1
        )
        record.write({"model": False, "res_id": False})
        domain = [("id", "=", record.id)]
        self.assertFalse(self.env["automation.record"].search(domain))
        self.env.user.group_ids = [
            (4, self.env.ref("automation_oca.group_automation_manager").id)
        ]
        self.env.invalidate_all()
        self.assertTrue(self.env["automation.record"].search(domain))
