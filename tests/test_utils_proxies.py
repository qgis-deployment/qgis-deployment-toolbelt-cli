#! python3  # noqa E265

"""
Usage from the repo root folder:

.. code-block:: bash
    # for whole tests
    python -m unittest tests.test_utils_proxies
    # for specific test
    python -m unittest tests.test_utils_proxies.TestUtilsNetworkProxies.test_proxy_settings
"""

# standard library
import unittest
from os import environ
from pathlib import Path

# project
from qgis_deployment_toolbelt.utils.proxies import get_proxy_settings


# ############################################################################
# ########## Classes #############
# ################################


class TestUtilsNetworkProxies(unittest.TestCase):
    """Test network proxy utilities."""

    def test_proxy_settings(self):
        """Test proxy settings retriever."""
        # by default, no proxy
        self.assertDictEqual(get_proxy_settings(), {})

        # using generic - only http
        get_proxy_settings.cache_clear()
        environ["HTTP_PROXY"] = "http://proxy.example.com:3128"
        self.assertIsInstance(get_proxy_settings(), dict)
        self.assertEqual(
            get_proxy_settings().get("http"), "http://proxy.example.com:3128"
        )
        self.assertIsNone(get_proxy_settings().get("https"))

        environ.pop("HTTP_PROXY")  # clean up

        # using generic - only https
        get_proxy_settings.cache_clear()
        environ["HTTPS_PROXY"] = "https://proxy.example.com:3128"
        self.assertIsInstance(get_proxy_settings(), dict)
        self.assertEqual(
            get_proxy_settings().get("https"), "https://proxy.example.com:3128"
        )
        self.assertIsNone(get_proxy_settings().get("http"))

        environ.pop("HTTPS_PROXY")  # clean up

        # using generic - both http and https
        get_proxy_settings.cache_clear()
        environ["HTTP_PROXY"] = "http://proxy.example.com:3128"
        environ["HTTPS_PROXY"] = "https://proxy.example.com:3128"
        self.assertIsInstance(get_proxy_settings(), dict)
        self.assertEqual(
            get_proxy_settings().get("https"), "https://proxy.example.com:3128"
        )
        self.assertEqual(
            get_proxy_settings().get("http"), "http://proxy.example.com:3128"
        )

        environ.pop("HTTP_PROXY")  # clean up
        environ.pop("HTTPS_PROXY")  # clean up

        # using custom QDT
        get_proxy_settings.cache_clear()
        environ["QDT_PROXY_HTTP"] = "http://user:p8ùX45@proxy.example.com:3128"
        self.assertIsInstance(get_proxy_settings(), dict)
        self.assertEqual(
            get_proxy_settings().get("http"),
            "http://user:p8ùX45@proxy.example.com:3128",
        )
        self.assertEqual(
            get_proxy_settings().get("https"),
            "http://user:p8ùX45@proxy.example.com:3128",
        )

        environ.pop("QDT_PROXY_HTTP")  # clean up

        # not valid URL - just to check the case
        environ["QDT_PROXY_HTTP"] = "socks5://user:motdepasse@proxy.example.com:1182"
        environ.pop("QDT_PROXY_HTTP")  # clean up
        get_proxy_settings.cache_clear()

    def test_pac_file(self):
        """Test PAC file proxies retriver"""

        get_proxy_settings.cache_clear()

        ## url
        environ["QDT_PAC_FILE"] = (
            "https://raw.githubusercontent.com/qgis-deployment/qgis-deployment-toolbelt-cli/refs/heads/main/tests/fixtures/pac/proxy.pac"
        )

        ### QGIS plugin : use proxy
        qgis_plugin_proxy_settings = get_proxy_settings(
            "https://plugins.qgis.org/plugins/french_locator_filter/version/1.1.1/download/"
        )
        self.assertIsInstance(qgis_plugin_proxy_settings, dict)
        self.assertEqual(
            qgis_plugin_proxy_settings.get("http"),
            "http://myproxy:8080",  # NOSONAR
        )
        self.assertEqual(
            qgis_plugin_proxy_settings.get("https"),
            "http://myproxy:8080",  # NOSONAR
        )

        ### In no proxy rules
        grand_plugin_proxy_settings = get_proxy_settings(
            "https://qgis-plugin.no-proxy.fr/plugin.zip"
        )
        self.assertIsInstance(grand_plugin_proxy_settings, dict)
        self.assertIsNone(grand_plugin_proxy_settings.get("http"))
        self.assertIsNone(grand_plugin_proxy_settings.get("https"))

        ### No url
        no_url_proxy_settings = get_proxy_settings()
        self.assertIsInstance(no_url_proxy_settings, dict)
        self.assertEqual(
            no_url_proxy_settings.get("http"),
            "http://myproxy:8080",  # NOSONAR
        )
        self.assertEqual(
            no_url_proxy_settings.get("http"),
            "http://myproxy:8080",  # NOSONAR
        )

        ## Local file
        get_proxy_settings.cache_clear()
        pac_file = Path("tests/fixtures/pac/proxy.pac")
        environ["QDT_PAC_FILE"] = str(pac_file.absolute())

        ### QGIS plugin : use proxy
        qgis_plugin_proxy_settings = get_proxy_settings(
            "https://plugins.qgis.org/plugins/french_locator_filter/version/1.1.1/download/"
        )
        self.assertIsInstance(qgis_plugin_proxy_settings, dict)
        self.assertEqual(
            qgis_plugin_proxy_settings.get("http"),
            "http://myproxy:8080",  # NOSONAR
        )
        self.assertEqual(
            qgis_plugin_proxy_settings.get("https"),
            "http://myproxy:8080",  # NOSONAR
        )

        ### In no proxy rules
        grand_plugin_proxy_settings = get_proxy_settings(
            "https://qgis-plugin.no-proxy.fr/plugin.zip"
        )
        self.assertIsInstance(grand_plugin_proxy_settings, dict)
        self.assertIsNone(grand_plugin_proxy_settings.get("http"))
        self.assertIsNone(grand_plugin_proxy_settings.get("https"))

        ### No url
        no_url_proxy_settings = get_proxy_settings()
        self.assertIsInstance(no_url_proxy_settings, dict)
        self.assertEqual(
            no_url_proxy_settings.get("http"),
            "http://myproxy:8080",  # NOSONAR
        )
        self.assertEqual(
            no_url_proxy_settings.get("http"),
            "http://myproxy:8080",  # NOSONAR
        )

        environ.pop("QDT_PAC_FILE")  # clean up
        get_proxy_settings.cache_clear()


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()
