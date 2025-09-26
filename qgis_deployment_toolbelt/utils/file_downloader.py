#! python3  # noqa: E265


# ############################################################################
# ########## IMPORTS #############
# ################################

# standard library
import logging
import ssl
import warnings
from os import getenv
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

# 3rd party
import truststore
from requests import Response, Session, exceptions as requests_exceptions
from requests.adapters import HTTPAdapter
from requests.utils import requote_uri
from urllib3.exceptions import InsecureRequestWarning

# package
from qgis_deployment_toolbelt.__about__ import __title_clean__, __version__
from qgis_deployment_toolbelt.utils.formatters import convert_octets
from qgis_deployment_toolbelt.utils.proxies import get_proxy_settings
from qgis_deployment_toolbelt.utils.str2bool import str2bool


# ############################################################################
# ########## GLOBALS #############
# ################################

# logs
logger = logging.getLogger(__name__)

if not str2bool(getenv("QDT_SSL_VERIFY", True)):
    warnings.filterwarnings("ignore", category=InsecureRequestWarning)
    logger.warning(
        "SSL warnings (InsecureRequestWarning) are explicitly disabled through "
        "environment variable 'QDT_SSL_VERIFY'. HTTPS request will be unverified. "
        "Adding certificate verification is strongly advised. "
        "See: https://urllib3.readthedocs.io/en/latest/advanced-usage.html#tls-warnings"
    )


# ############################################################################
# ########## CLASSES #############
# ################################


class TruststoreAdapter(HTTPAdapter):
    """Custom HTTP transport adapter made to use local trust store.

    Source: <https://stackoverflow.com/a/78265028/2556577>
    Documentation: <https://requests.readthedocs.io/en/latest/user/advanced/#transport-adapters>
    """

    def init_poolmanager(
        self, connections: int, maxsize: int, block: bool = False
    ) -> None:
        """Initializes a urllib3 PoolManager.

        Args:
            connections (int): number of urllib3 connection pools to cache.
            maxsize (int): maximum number of connections to save in the pool.
            block (bool, optional): Block when no free connections are available.. Defaults to False.

        """
        ctx = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        return super().init_poolmanager(connections, maxsize, block, ssl_context=ctx)


# ############################################################################
# ########## FUNCTIONS ###########
# ################################


def download_remote_file_to_local(
    remote_url_to_download: str,
    local_file_path: Path,
    user_agent: str = f"{__title_clean__}/{__version__}",
    content_type: str | None = None,
    chunk_size: int = 8192,
    timeout: tuple[int, int] = (800, 800),
    use_stream: bool = True,
) -> Path:
    """Check if the local index file exists. If not, download the search index from \
        remote URL. If it does exist, check if it has been modified.

    Args:
        remote_url_to_download (str): remote URL of the search index
        local_file_path (Path): local path to the index file
        user_agent (str, optional): user agent to use to perform the request. Defaults \
            to f"{__title_clean__}/{__version__}".
        content_type (str | None, optional): HTTP content-type. Defaults to None.
        chunk_size (int, optional): size of each chunk to read and write in bytes. \
            Defaults to 8192.
        timeout (tuple[int, int], optional): custom timeout (request, response). \
            Defaults to (800, 800).
        use_stream (bool, optional): Option to enable/disable streaming download. \
            Defaults to True.

    Returns:
        Path: path to the local file (should be the same as local_file_path)
    """
    # check if file exists
    if local_file_path.exists():
        logger.info(f"{local_file_path} already exists. It's about to be replaced.")
        local_file_path.unlink(missing_ok=True)

    # make sure parents folder exist
    local_file_path.parent.mkdir(parents=True, exist_ok=True)

    # headers
    headers = {"User-Agent": user_agent}
    if content_type:
        headers["Accept"] = content_type

    try:
        with Session() as dl_session:
            dl_session.headers.update(headers)
            dl_session.proxies.update(
                get_proxy_settings(url=requote_uri(remote_url_to_download))
            )
            dl_session.verify = str2bool(getenv("QDT_SSL_VERIFY", True))

            # handle local system certificates store
            if str2bool(getenv("QDT_SSL_USE_SYSTEM_STORES", False)):
                logger.debug(
                    "Option to use native system certificates stores is enabled."
                )
                dl_session.mount("https://", TruststoreAdapter())

            # Clean url
            parsed_url = urlparse(unquote(remote_url_to_download))
            # Reconstruct base URL
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
            # Get existing params if any exist
            params = (
                parse_qs(parsed_url.query, keep_blank_values=True)
                if parsed_url.query
                else {}
            )
            with dl_session.get(
                url=base_url,
                params=params,
                stream=use_stream,
                timeout=timeout,
            ) as req:
                req.raise_for_status()
                if use_stream:
                    with local_file_path.open(mode="wb") as buffile:
                        for chunk in req.iter_content(chunk_size=chunk_size):
                            if chunk:
                                buffile.write(chunk)
                else:
                    # Download download the entire content at once
                    local_file_path.write_bytes(req.content)

            logger.info(
                f"Downloading {remote_url_to_download} to {local_file_path} "
                f"({convert_octets(local_file_path.stat().st_size)}) succeeded."
            )
    except requests_exceptions.HTTPError as error:
        logger.error(
            f"Downloading {remote_url_to_download} to {local_file_path} failed. "
            f"Cause: HTTPError. Trace: {error}."
        )
        if isinstance(req, Response):
            http_error_details = {
                "status": req.status_code,
                "headers": req.headers,
                "body": req.content,
            }
            logger.error(
                f"Addtional details grabbed from HTTP response: {http_error_details}"
            )

        raise error
    except requests_exceptions.ConnectionError as error:
        logger.error(
            f"Downloading {remote_url_to_download} to {local_file_path} failed. "
            f"Cause: ConnectionError. Trace: {error}"
        )
        raise error
    except Exception as error:
        logger.error(
            f"Downloading {remote_url_to_download} to {local_file_path} failed. "
            f"Cause: Unknown error. Trace: {error}",
            stack_info=True,
        )
        raise error

    return local_file_path
