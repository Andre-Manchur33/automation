# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import odoo

from odoo.addons.web.tests.test_js import HootCommon, unit_test_error_checker


@odoo.tests.tagged("post_install", "-at_install")
class TestAutomationOCA(HootCommon):
    """Test Automation OCA (Odoo 20: the Hoot suite takes the modules to test)"""

    @odoo.tests.no_retry
    def test_automation_oca(self):
        addons = self._get_addons_from_asset_bundle("web.assets_unit_tests")
        filters = self._get_hoot_filters(addons, ["automation_oca"])
        if not filters:
            return
        self.browser_js(
            f"/web/tests?&headless&loglevel=2&preset=desktop&timeout=15000{filters}",
            "",
            "",
            login="admin",
            timeout=1800,
            success_signal="[HOOT] Test suite succeeded",
            error_checker=unit_test_error_checker,
        )
