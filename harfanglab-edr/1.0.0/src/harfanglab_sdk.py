import requests
import json
from datetime import datetime, timedelta, timezone
import requests
import dateutil.parser
import time
import logging
import markdown

STRING_TYPES = (str, bytes)
MARKDOWN_CHARS = r"\`*_{}[]()#+-!|"

def get_params(params):
    res = []
    if params:
        for k, v in params.items():
            res.append(f'{k}={v}')
        return '?' + '&'.join(res)
    else:
        return ''


def string_escape(st):
    """
       Escape any chars that might break a markdown string

       :type st: ``str``
       :param st: The string to be modified (required)

       :return: A modified string
       :rtype: ``str``
    """
    st = st.replace('\r\n', '<br>')  # Windows
    st = st.replace('\r', '<br>')  # old Mac
    st = st.replace('\n', '<br>')  # Unix

    for c in ('|', '`'):
        st = st.replace(c, '\\' + c)

    return st

def get_markdown_from_table(name, t, headers=None, headerTransform=None, url_keys=None):
    """
       Converts a JSON table to a Markdown table

       :type name: ``str``
       :param name: The name of the table (required)

       :type t: ``dict`` or ``list``
       :param t: The JSON table - List of dictionaries with the same keys or a single dictionary (required)

       :type headers: ``list`` or ``string``
       :param headers: A list of headers to be presented in the output table (by order). If string will be passed
            then table will have single header. Default will include all available headers.

       :type headerTransform: ``function``
       :param headerTransform: A function that formats the original data headers (optional)

       :type url_keys: ``list``
       :param url_keys: a list of keys in the given JSON table that should be turned in to clickable

       :return: A string representation of the markdown table
       :rtype: ``str``
    """
    # Turning the urls in the table to clickable
    if url_keys:
        t = url_to_clickable_markdown(t, url_keys)

    result = ''
    if name:
        result = '### ' + name + '\n'

    if not t or len(t) == 0:
        result += '**No entries.**\n'
        return result

    if not headers and isinstance(t, dict) and len(t.keys()) == 1:
        # in case of a single key, create a column table where each element is in a different row.
        headers = list(t.keys())
        t = list(t.values())[0]

    if not isinstance(t, list):
        t = [t]

    if headers and isinstance(headers, STRING_TYPES):
        headers = [headers]

    if not isinstance(t[0], dict):
        # the table contains only simple objects (strings, numbers)
        # should be only one header
        if headers and len(headers) > 0:
            header = headers[0]
            t = [{header: item} for item in t]
        else:
            raise Exception(
                "Missing headers param for get_markdown_from_table. Example: headers=['Some Header']")

    # in case of headers was not provided (backward compatibility)
    if not headers:
        headers = list(t[0].keys())
        headers.sort()

    if t and len(headers) > 0:
        newHeaders = []
        if headerTransform is None:  # noqa
            def headerTransform(s): return string_escape(s.title())  # noqa
        for header in headers:
            newHeaders.append(headerTransform(header))
        result += '|'
        if len(newHeaders) == 1:
            result += newHeaders[0]
        else:
            result += '|'.join(newHeaders)
        result += '|\n'
        sep = '---'
        result += '|' + '|'.join([sep] * len(headers)) + '|\n'
        for entry in t:
            entry_copy = entry.copy()

            vals = [string_escape(str(entry_copy.get(h, '') if entry_copy.get(
                h) is not None else '')) for h in headers]

            # this pipe is optional
            result += '| '
            try:
                result += ' | '.join(vals)
            except UnicodeDecodeError:
                vals = [str(v) for v in vals]
                result += ' | '.join(vals)
            result += ' |\n'

    else:
        result += '**No entries.**\n'

    return result

def url_to_clickable_markdown(data, url_keys):
    """
    Transform the urls fields into clickable url in markdown.

    :type data: ``[Union[str, List[Any], Dict[str, Any]]]``
    :param data: a dictionary or a list containing data with some values that are urls

    :type url_keys: ``Dict[str, str]``
    :param url_keys: a dict whose keys correspond to the url fields to turn into clickable, and values correspond to the link texts

    :return: markdown format for clickable url
    :rtype: ``[Union[str, List[Any], Dict[str, Any]]]``
    """

    if isinstance(data, list):
        data = [url_to_clickable_markdown(item, url_keys) for item in data]

    elif isinstance(data, dict):
        data = {key: get_clickable_url(value, url_keys.get(key, None)) if key in url_keys else url_to_clickable_markdown(data[key], url_keys)
                for key, value in data.items()}

    return data

def get_clickable_url(url, text=None):
    """
    Make the given url clickable in markdown format

    :type url: ``Union[List[str], str]``
    :param url: the url of interest or a list of urls

    :type text: ``str``
    :param text: the link text to print

    :return: markdown format for clickable url
    :rtype: ``str``

    """
    if not url:
        return None
    elif isinstance(url, list):
        if text:
            return ['[{}]({})'.format(text, item) for item in url]
        else:
            return ['[{}]({})'.format(item, item) for item in url]

    if text:
        return '[{}]({})'.format(text, url)
    else:
        return '[{}]({})'.format(url, url)

class HarfangLabConnector:

    SEVERITIES = ['Informational', 'Low', 'Medium', 'High', 'Critical']
    MAX_NUMBER_OF_ALERTS_PER_CALL = 200
    MAX_NUMBER_OF_ITEMS = 10000

    def __init__(self, base_url, api_key, verify_certificate=True, http_proxy=None, https_proxy=None, logger=logging.getLogger('HarfangLab SDK')):
        """
           Initialize a HarfangLab EDR connector

           :param base_url: The base_url of the HarfangLab EDR manager (https://hurukai:8443)
           :param api_key: The API key to use to connect to the EDR Manager
           :param verify_certificate: Either a boolean True or False or a string 'true' or 'false'
           :param http_proxy: Proxy to use for HTTP connections
           :param https_proxy: Proxy to use for HTTPS connections
           :param logger: Logger to use
        """

        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.hlSession = requests.Session()
        self.logger = logger

        self.verify = True
        if type(verify_certificate) == bool:
            self.verify = verify_certificate
        elif isinstance(verify_certificate, str) and verify_certificate.lower() == 'false':
            self.verify = False
        else:
            self.verify = True

        self.logger.debug(f'Verify: {self.verify}')

        self.hlSession.verify = self.verify
        self.hlSession.headers.update(
            {
                'Authorization': f'Token {self.api_key}'
            }
        )
        proxies = {}
        if http_proxy and len(http_proxy) > 4:
            proxies['http'] = http_proxy
        if https_proxy and len(http_proxy) > 5:
            proxies['https'] = https_proxy
        self.hlSession.proxies = proxies
        self.logger = logger

    def __get_first_element(self, table):
        """
           Return the first element of a table

           :type table: ``List[Any]``
           :param table: The table to extract the first element of

           :return: The first element of the table
           :rtype: ``Any``
        """

        if table and isinstance(table, list) and len(table) > 0:
            return table[0]
        else:
            return None

    def __flatten_table(self, table):
        """
           Return a flattened string of all elements of a table joined with a ','

           :type table: ``List[Any]``
           :param table: The table to flatten

           :return: The flattened table
           :rtype: ``str``
        """

        if table and isinstance(table, list) and len(table) > 0:
            return ', '.join(table)
        else:
            return None

    def __get_hash_parameter(self, binary_hash):
        """
           Return a tuple (hash filter name, hash value) to be used as filter for the HarfangLab API

           :type binary_hash: ``str``
           :param str: The raw binary hash (either MD5, SHA1 or SHA256)

           :return: A tuple (hash filter name, hash value)
           :rtype: ``Tuple(str,str)``
        """

        hash_type = None
        if binary_hash is not None:
            if len(binary_hash) == 64:
                hash_type = "sha256"
            elif len(binary_hash) == 40:
                hash_type = "sha1"
            elif len(binary_hash) == 32:
                hash_type = "md5"

            return (f'hashes.{hash_type}__exact', binary_hash)

        return (None, None)

    def __generate_link_for_binary(self, v):
        """
           Return a HarfangLab download link for a binary including a temporary api token

           :type v: ``str``
           :param v: The binary SHA256 hash

           :return: A download link
           :rtype: ``str``
        """

        url = f'{self.base_url}/api/user/api_token/'
        api_token = None

        try:
            token = self.hlSession.post(
                url=url, data={'is_expirable': True}).json()
            if 'api_token' in token:
                api_token = token['api_token']
            link = f'{self.base_url}/api/data/telemetry/Binary/download/{v}'
            if api_token:
                link += f'?hl_expiring_key={api_token}'
            return link

        except Exception as e:
            return 'N/A'

    def __generate_link_for_artifact(self, v):
        """
           Return a HarfangLab download link for a job artifact from its id

           :type v: ``str``
           :param v: The artifact id

           :return: A download link
           :rtype: ``str``
        """

        url = f'{self.base_url}/api/user/api_token/'
        api_token = None

        try:
            token = self.hlSession.post(
                url=url, data={'is_expirable': True}).json()
            if 'api_token' in token:
                api_token = token['api_token']
            link = f'{self.base_url}/api/data/investigation/artefact/Artefact/{v}/download/'
            if api_token:
                link += f'?hl_expiring_key={api_token}'

            return link
        except Exception as e:
            return 'N/A'

    def __get_destination_ip(self, v):
        """
           Return a tuple (hash filter name, hash value) to be used as filter for the HarfangLab API for a destination IP filter

           :type v: ``str``
           :param v: The IP address

           :return: A tuple (hash filter name, hash value)
           :rtype: ``Tuple(str,str)``
        """

        return ('daddr', v)

    def __get_source_ip(self, v):
        """
           Return a tuple (hash filter name, hash value) to be used as filter for the HarfangLab API for a source IP filter

           :type v: ``str``
           :param v: The IP address

           :return: A tuple (hash filter name, hash value)
           :rtype: ``Tuple(str,str)``
        """
        return ('saddr', v)

    def __generate_view_link_for_source_ip(self, filters):
        """
           Return a HarfangLab view link for an IP IOC

           :type filters: ``Dict[str,str]``
           :param filters: The filters with their associated value to pass as query parameters

           :return: A view link
           :rtype: ``str``
        """
        f = []
        for filter, v in filters.items():
            f.append(f'{filter}={v}')
        return f'{self.base_url}/telemetry/network-connections?offset=0&{"&".join(f)}&ordering=-event_create_date'

    def __generate_view_link_for_destination_ip(self, filters):
        """
           Return a HarfangLab view link for an IP IOC

           :type filters: ``Dict[str,str]``
           :param filters: The filters with their associated value to pass as query parameters

           :return: A view link
           :rtype: ``str``
        """
        f = []
        for filter, v in filters.items():
            f.append(f'{filter}={v}')
        return f'{self.base_url}/telemetry/network-connections?offset=0&{"&".join(f)}&ordering=-event_create_date'

    def __generate_view_link_for_hash(self, filters):
        """
           Return a HarfangLab view link for an IP IOC

           :type filters: ``List[str]``
           :param filters: The list of parameters required to generate the link

           :return: A view link
           :rtype: ``str``
        """

        f = []
        for filter, v in filters.items():
            f.append(f'{filter}={v}')
        return f'{self.base_url}/telemetry/processes?limit=25&offset=0&{"&".join(f)}&ordering=-event_create_date'


    """
    The JOBS dict contains all the job services and their description. Its keys correspond to the service names in the service description file in JSON format.
    Each job is associated to a responder flavor. When called from a TheHive case, it generates a dedicated task in TheHive whose description contains the job result in Markdown.

    Job description structure:
      * request_api_endpoint: HarfangLab API endpoint to start a job and get its status
      * result_api_endpoint: HarfangLab API endpoint to get job results
      * title: Title associated to the job result, that is provided in the task description
      * task_title: Description of the TheHive task
      * action: Job action that is transmitted to the HarfangLab API
      * ordering: Value ordering field (format corresponding to HarfangLab API)
      * fields: List of output fields to provide in the resulting markdown table.

    Each output field is described with the following parameters:
      * name: Name of the field as provided in the result table headers
      * path: Path of the field value for extraction from the job results. The path is composed of all dict keys separated by a '.'
      * default: Default value to use if the path does not exist
      * transform: Function to use to transform the field before inserting into the resulting table
      * is_url: Indicates whether the field must be rendered as a markdown URL
      * link_text: Corresponds to the link text to show if the field must be rendered as a markdown URL. It not specified, the URL will be used as the text to show.
    """

    JOBS = {
        'getProcesses': {
            'request_api_endpoint': '/api/data/Job/',
            'status_api_endpoint': '/api/data/Job/',
            'result_api_endpoint': '/api/data/investigation/hunting/Process/',
            'title': 'Process list',
            'task_title': 'Review process list',
            'action': 'getProcessList',
            'ordering': 'name',
            'fields': [
                {'name': 'name', 'path': 'name', 'default': None},
                {'name': 'session', 'path': 'session', 'default': None},
                {'name': 'username', 'path': 'username', 'default': None},
                {'name': 'integrity', 'path': 'integrity_level', 'default': None},
                {'name': 'pid', 'path': 'pid', 'default': None},
                {'name': 'ppid', 'path': 'ppid', 'default': None},
                {'name': 'cmdline', 'path': 'cmdline', 'default': None},
                {'name': 'fullpath', 'path': 'binaryinfo.fullpath', 'default': None},
                {'name': 'signed', 'path': 'binaryinfo.binaryinfo.signed',
                 'default': False},
                {'name': 'md5', 'path': 'binaryinfo.binaryinfo.md5', 'default': None},
                {'name': 'sha1', 'path': 'binaryinfo.binaryinfo.sha1',
                 'default': None},
                {'name': 'sha256', 'path': 'binaryinfo.binaryinfo.sha256',
                 'default': None}
            ]
        },
        'getServices': {
            'request_api_endpoint': '/api/data/Job/',
            'status_api_endpoint': '/api/data/Job/',
            'result_api_endpoint': '/api/data/investigation/hunting/Service/',
            'title': 'Service list',
            'task_title': 'Review service list',
            'action': 'getHives',
            'ordering': 'service_name',
            'fields': [
                {'name': 'name', 'path': 'service_name', 'default': None},
                {'name': 'image path', 'path': 'image_path', 'default': None},
                {'name': 'fullpath', 'path': 'binaryinfo.fullpath', 'default': None},
                {'name': 'signed', 'path': 'binaryinfo.binaryinfo.signed',
                 'default': False},
                {'name': 'md5', 'path': 'binaryinfo.binaryinfo.md5', 'default': None},
                {'name': 'sha1', 'path': 'binaryinfo.binaryinfo.sha1',
                 'default': None},
                {'name': 'sha256', 'path': 'binaryinfo.binaryinfo.sha256',
                 'default': None}
            ]
        },
        'getPipes': {
            'request_api_endpoint': '/api/data/Job/',
            'status_api_endpoint': '/api/data/Job/',
            'result_api_endpoint': '/api/data/investigation/hunting/Pipe/',
            'title': 'Pipe list',
            'task_title': 'Review pipe list',
            'action': 'getPipeList',
            'ordering': 'name',
            'fields': [
                    {'name': 'name', 'path': 'name', 'default': None}
            ]
        },
        'getDrivers': {
            'request_api_endpoint': '/api/data/Job/',
            'status_api_endpoint': '/api/data/Job/',
            'result_api_endpoint': '/api/data/investigation/hunting/Driver/',
            'title': 'Loaded driver list',
            'task_title': 'Review loaded driver list',
            'action': 'getLoadedDriverList',
            'ordering': 'short_name',
            'fields': [
                {'name': 'fullpath', 'path': 'binaryinfo.fullpath', 'default': None},
                {'name': 'signed', 'path': 'binaryinfo.binaryinfo.signed',
                 'default': False},
                {'name': 'md5', 'path': 'binaryinfo.binaryinfo.md5', 'default': None},
                {'name': 'sha1', 'path': 'binaryinfo.binaryinfo.sha1',
                 'default': None},
                {'name': 'sha256', 'path': 'binaryinfo.binaryinfo.sha256',
                 'default': None}
            ]
        },
        'getPrefetches': {
            'request_api_endpoint': '/api/data/Job/',
            'status_api_endpoint': '/api/data/Job/',
            'result_api_endpoint': '/api/data/investigation/hunting/Prefetch/',
            'title': 'Prefetch list',
            'task_title': 'Review prefetch list',
            'action': 'getPrefetch',
            'ordering': '-last_executed',
            'fields': [
                {'name': 'executable name',
                        'path': 'executable_name', 'default': None},
                {'name': 'last executed', 'path': 'last_executed',
                 'default': None, 'transform': __get_first_element},
            ]
        },
        'getScheduledTasks': {
            'request_api_endpoint': '/api/data/Job/',
            'status_api_endpoint': '/api/data/Job/',
            'result_api_endpoint': '/api/data/investigation/hunting/ScheduledTaskXML/',
            'title': 'Scheduled task list',
            'task_title': 'Review scheduled task list',
            'action': 'getScheduledTasks',
            'ordering': 'short_name',
            'fields': [
                {'name': 'name', 'path': 'short_name', 'default': None},
                {'name': 'fullpath', 'path': 'binaryinfo.fullpath', 'default': None},
                {'name': 'signed', 'path': 'binaryinfo.binaryinfo.signed',
                 'default': False},
                {'name': 'md5', 'path': 'binaryinfo.binaryinfo.md5', 'default': None},
                {'name': 'sha1', 'path': 'binaryinfo.binaryinfo.sha1',
                 'default': None},
                {'name': 'sha256', 'path': 'binaryinfo.binaryinfo.sha256',
                 'default': None}
            ]
        },
        'getRunKeys': {
            'request_api_endpoint': '/api/data/Job/',
            'status_api_endpoint': '/api/data/Job/',
            'result_api_endpoint': '/api/data/investigation/hunting/RunKey/',
            'title': 'Run key list',
            'task_title': 'Review run key list',
            'action': 'getHives',
            'ordering': '-last_executed',
            'fields': [
                {'name': 'name', 'path': 'short_name', 'default': None},
                {'name': 'fullpath', 'path': 'binaryinfo.fullpath', 'default': None},
                {'name': 'signed', 'path': 'binaryinfo.binaryinfo.signed',
                 'default': False},
                {'name': 'md5', 'path': 'binaryinfo.binaryinfo.md5', 'default': None},
                {'name': 'sha1', 'path': 'binaryinfo.binaryinfo.sha1',
                 'default': None},
                {'name': 'sha256', 'path': 'binaryinfo.binaryinfo.sha256',
                 'default': None}
            ]
        },
        'getStartupFiles': {
            'request_api_endpoint': '/api/data/Job/',
            'status_api_endpoint': '/api/data/Job/',
            'result_api_endpoint': '/api/data/investigation/hunting/Startup/',
            'title': 'Startup file list',
            'task_title': 'Review startup file list',
            'action': 'getStartupFileList',
            'ordering': 'filename',
            'fields': [
                {'name': 'startup file name',
                        'path': 'filename', 'default': None},
                {'name': 'startup file full path',
                 'path': 'fullpathfilename', 'default': None},
                {'name': 'fullpath', 'path': 'binaryinfo.fullpath', 'default': None},
                {'name': 'signed', 'path': 'binaryinfo.binaryinfo.signed',
                 'default': False},
                {'name': 'md5', 'path': 'binaryinfo.binaryinfo.md5', 'default': None},
                {'name': 'sha1', 'path': 'binaryinfo.binaryinfo.sha1',
                 'default': None},
                {'name': 'sha256', 'path': 'binaryinfo.binaryinfo.sha256',
                 'default': None}
            ]
        },
        'getPersistence': {
            'request_api_endpoint': '/api/data/Job/',
            'status_api_endpoint': '/api/data/Job/',
            'result_api_endpoint': '/api/data/investigation/hunting/PersistanceFile/',
            'title': 'Persistence list',
            'task_title': 'Review persistence list',
            'action': 'persistanceScanner',
            'ordering': 'short_name',
            'fields': [
                {'name': 'type', 'path': 'persistance_type', 'default': None},
                {'name': 'filename', 'path': 'binaryinfo.filename', 'default': None},
                {'name': 'fullpath', 'path': 'binaryinfo.fullpath', 'default': None},
            ]
        },
        'getWMI': {
            'request_api_endpoint': '/api/data/Job/',
            'status_api_endpoint': '/api/data/Job/',
            'result_api_endpoint': '/api/data/investigation/hunting/Wmi/',
            'title': 'WMI list',
            'task_title': 'Review  list',
            'action': 'getWMI',
            'ordering': 'filename',
            'fields': [
                {'name': 'filter to consumer type',
                        'path': 'filtertoconsumertype', 'default': None},
                {'name': 'event filter name',
                 'path': 'eventfiltername', 'default': None},
                {'name': 'event consumer name',
                 'path': 'eventconsumername', 'default': None},
                {'name': 'event filter', 'path': 'eventfilter', 'default': None},
                {'name': 'consumer data', 'path': 'consumerdata', 'default': None},
            ]
        },
        'getNetworkShares': {
            'request_api_endpoint': '/api/data/Job/',
            'status_api_endpoint': '/api/data/Job/',
            'result_api_endpoint': '/api/data/investigation/hunting/NetworkShare/',
            'title': 'Network share list',
            'task_title': 'Review network share list',
            'action': 'getNetworkShare',
            'ordering': 'name',
            'fields': [
                {'name': 'name', 'path': 'name', 'default': None},
                {'name': 'caption', 'path': 'caption', 'default': None},
                {'name': 'description', 'path': 'description', 'default': None},
                {'name': 'path', 'path': 'path', 'default': None},
                {'name': 'status', 'path': 'status', 'default': None},
                {'name': 'share type val',
                 'path': 'sharetypeval', 'default': None},
                {'name': 'share type', 'path': 'sharetype', 'default': None},
                {'name': 'hostname', 'path': 'agent.hostname', 'default': None},
            ]
        },
        'getSessions': {
            'request_api_endpoint': '/api/data/Job/',
            'status_api_endpoint': '/api/data/Job/',
            'result_api_endpoint': '/api/data/investigation/hunting/Session/',
            'title': 'Session list',
            'task_title': 'Review session list',
            'action': 'getSessions',
            'ordering': 'name',
            'fields': [
                {'name': 'logon id', 'path': 'logonid', 'default': None},
                {'name': 'authentication package',
                 'path': 'authenticationpackage', 'default': None},
                {'name': 'logon type', 'path': 'logontype', 'default': None},
                {'name': 'logon type str',
                 'path': 'logontypestr', 'default': None},
                {'name': 'session start time',
                 'path': 'sessionstarttime', 'default': None},
                {'name': 'hostname', 'path': 'agent.hostname', 'default': None},
            ]
        },
        'getArtifactMFT': {
            'request_api_endpoint': '/api/data/Job/',
            'status_api_endpoint': '/api/data/Job/',
            'result_api_endpoint': '/api/data/investigation/artefact/Artefact/',
            'title': 'MFT',
            'task_title': 'Analyze MFT',
            'action': 'collectRAWEvidences',
            'parameters': {'hives': False, 'evt': False, 'mft': True,
                           'prefetch': False, 'usn': False, 'logs': False, 'fs': False},
            'ordering': 'name',
            'fields': [
                {'name': 'hostname', 'path': 'agent.hostname', 'default': None},
                {'name': 'message', 'path': 'msg', 'default': None},
                {'name': 'size', 'path': 'size', 'default': None},
                {'name': 'download_link', 'path': 'id', 'default': None,
                 'transform': __generate_link_for_artifact, 'is_url': True, 'link_text': 'Download'}
            ]
        },
        'getArtifactHives': {
            'request_api_endpoint': '/api/data/Job/',
            'status_api_endpoint': '/api/data/Job/',
            'result_api_endpoint': '/api/data/investigation/artefact/Artefact/',
            'title': 'Hives',
            'task_title': 'Analyze Hives',
            'action': 'collectRAWEvidences',
            'parameters': {'hives': True, 'evt': False, 'mft': False,
                           'prefetch': False, 'usn': False, 'logs': False, 'fs': False},
            'ordering': 'name',
            'fields': [
                {'name': 'hostname', 'path': 'agent.hostname', 'default': None},
                {'name': 'message', 'path': 'msg', 'default': None},
                {'name': 'size', 'path': 'size', 'default': None},
                {'name': 'download_link', 'path': 'id', 'default': None,
                 'transform': __generate_link_for_artifact, 'is_url': True, 'link_text': 'Download'}
            ]
        },
        'getArtifactEvtx': {
            'request_api_endpoint': '/api/data/Job/',
            'status_api_endpoint': '/api/data/Job/',
            'result_api_endpoint': '/api/data/investigation/artefact/Artefact/',
            'title': 'Windows event logs',
            'task_title': 'Analyze event logs',
            'action': 'collectRAWEvidences',
            'parameters': {'hives': False, 'evt': True, 'mft': False,
                           'prefetch': False, 'usn': False, 'logs': False, 'fs': False},
            'ordering': 'name',
            'fields': [
                {'name': 'hostname', 'path': 'agent.hostname', 'default': None},
                {'name': 'message', 'path': 'msg', 'default': None},
                {'name': 'size', 'path': 'size', 'default': None},
                {'name': 'download_link', 'path': 'id', 'default': None,
                 'transform': __generate_link_for_artifact, 'is_url': True, 'link_text': 'Download'}
            ]
        },
        'getArtifactLogs': {
            'request_api_endpoint': '/api/data/Job/',
            'status_api_endpoint': '/api/data/Job/',
            'result_api_endpoint': '/api/data/investigation/artefact/Artefact/',
            'title': 'Linux logs',
            'task_title': 'Analyze logs',
            'action': 'collectRAWEvidences',
            'parameters': {'hives': False, 'evt': False, 'mft': False,
                           'prefetch': False, 'usn': False, 'logs': True, 'fs': False},
            'ordering': 'name',
            'fields': [
                {'name': 'hostname', 'path': 'agent.hostname', 'default': None},
                {'name': 'message', 'path': 'msg', 'default': None},
                {'name': 'size', 'path': 'size', 'default': None},
                {'name': 'download_link', 'path': 'id', 'default': None,
                 'transform': __generate_link_for_artifact, 'is_url': True, 'link_text': 'Download'}
            ]
        },
        'getArtifactFilesystem': {
            'request_api_endpoint': '/api/data/Job/',
            'status_api_endpoint': '/api/data/Job/',
            'result_api_endpoint': '/api/data/investigation/artefact/Artefact/',
            'title': 'Linux filesystem',
            'task_title': 'Analyze filesystem',
            'action': 'collectRAWEvidences',
            'parameters': {'hives': False, 'evt': False, 'mft': False,
                           'prefetch': False, 'usn': False, 'logs': False, 'fs': True},
            'ordering': 'name',
            'fields': [
                {'name': 'hostname', 'path': 'agent.hostname', 'default': None},
                {'name': 'message', 'path': 'msg', 'default': None},
                {'name': 'size', 'path': 'size', 'default': None},
                {'name': 'download_link', 'path': 'id', 'default': None,
                 'transform': __generate_link_for_artifact, 'is_url': True, 'link_text': 'Download'}
            ]
        },
        'getArtifactUSN': {
            'request_api_endpoint': '/api/data/Job/',
            'status_api_endpoint': '/api/data/Job/',
            'result_api_endpoint': '/api/data/investigation/artefact/Artefact/',
            'title': 'USN logs',
            'task_title': 'Analyze USN logs',
            'action': 'collectRAWEvidences',
            'parameters': {'hives': False, 'evt': False, 'mft': False,
                           'prefetch': False, 'usn': True, 'logs': False, 'fs': False},
            'ordering': 'name',
            'fields': [
                {'name': 'hostname', 'path': 'agent.hostname', 'default': None},
                {'name': 'message', 'path': 'msg', 'default': None},
                {'name': 'size', 'path': 'size', 'default': None},
                {'name': 'download_link', 'path': 'id', 'default': None,
                 'transform': __generate_link_for_artifact, 'is_url': True, 'link_text': 'Download'}
            ]
        },
        'getArtifactPrefetch': {
            'request_api_endpoint': '/api/data/Job/',
            'status_api_endpoint': '/api/data/Job/',
            'result_api_endpoint': '/api/data/investigation/artefact/Artefact/',
            'title': 'USN logs',
            'task_title': 'Analyze prefetches',
            'action': 'collectRAWEvidences',
            'parameters': {'hives': False, 'evt': False, 'mft': False,
                           'prefetch': True, 'usn': False, 'logs': False, 'fs': False},
            'ordering': 'name',
            'fields': [
                {'name': 'hostname', 'path': 'agent.hostname', 'default': None},
                {'name': 'message', 'path': 'msg', 'default': None},
                {'name': 'size', 'path': 'size', 'default': None},
                {'name': 'download_link', 'path': 'id', 'default': None,
                 'transform': __generate_link_for_artifact, 'is_url': True, 'link_text': 'Download'}
            ]
        },
        'getArtifactAll': {
            'request_api_endpoint': '/api/data/Job/',
            'status_api_endpoint': '/api/data/Job/',
            'result_api_endpoint': '/api/data/investigation/artefact/Artefact/',
            'title': 'All raw artifacts',
            'task_title': 'Analyze all raw artifacts',
            'action': 'collectRAWEvidences',
            'parameters': {'hives': True, 'evt': True, 'mft': True,
                           'prefetch': True, 'usn': True, 'logs': True, 'fs': True},
            'ordering': 'name',
            'fields': [
                {'name': 'hostname', 'path': 'agent.hostname', 'default': None},
                {'name': 'message', 'path': 'msg', 'default': None},
                {'name': 'size', 'path': 'size', 'default': None},
                {'name': 'download_link', 'path': 'id', 'default': None,
                 'transform': __generate_link_for_artifact, 'is_url': True, 'link_text': 'Download'}
            ]
        },
        'getArtifactRamdump': {
            'request_api_endpoint': '/api/data/Job/',
            'status_api_endpoint': '/api/data/Job/',
            'result_api_endpoint': '/api/data/investigation/artefact/Artefact/',
            'title': 'RAM Dump',
            'task_title': 'Analyze RAM dump',
            'action': 'memoryDumper',
            'ordering': 'name',
            'fields': [
                {'name': 'hostname', 'path': 'agent.hostname', 'default': None},
                {'name': 'message', 'path': 'msg', 'default': None},
                {'name': 'size', 'path': 'size', 'default': None},
                {'name': 'download_link', 'path': 'id', 'default': None,
                 'transform': __generate_link_for_artifact, 'is_url': True, 'link_text': 'Download'}
            ]
        },
        'killProcess': {
            'request_api_endpoint': None,
            'status_api_endpoint': '/api/data/Job/',
            'result_api_endpoint': '/api/data/investigation/job/Simple/',
            'title': 'Killed process',
            'task_title': 'Review process kill report',
            'action': 'knownProcessFinderKiller',
            'ordering': 'name',
            'fields': [
                {'name': 'message', 'path': 'msg', 'default': None},
                {'name': 'date', 'path': 'date', 'default': None},
                {'name': 'hostname', 'path': 'agent.hostname', 'default': None}
            ]
        },
        'dumpProcess': {
            'request_api_endpoint': None,
            'status_api_endpoint': '/api/data/Job/',
            'result_api_endpoint': '/api/data/investigation/artefact/Artefact/',
            'title': 'Dumped process',
            'task_title': 'Analyze dumped process',
            'action': 'processDumper',
            'ordering': '-date',
            'fields': [
                {'name': 'message', 'path': 'msg', 'default': None},
                {'name': 'date', 'path': 'date', 'default': None},
                {'name': 'size', 'path': 'size', 'default': None},
                {'name': 'hostname', 'path': 'agent.hostname', 'default': None},
                {'name': 'download_link', 'path': 'id', 'default': None,
                 'transform': __generate_link_for_artifact, 'is_url': True, 'link_text': 'Download'}
            ]
        },
    }

    TELEMETRY_SEARCHES = {
        'searchHash': {
            'api_endpoint': '/api/data/telemetry/Processes/',
            'title': 'Hash search',
            'task_title': 'Review hash search in telemetry',
            'inputs': [
                {'name': 'hash', 'filter': 'hash',
                 'transform': __get_hash_parameter, 'mandatory': True},
                {'name': 'process_name', 'filter': 'process_name'},
                {'name': 'image_name', 'filter': 'image_name'},
                {'name': 'limit', 'filter': 'limit'}
            ],
            'fields': [
                {'name': 'name', 'path': 'name', 'default': None},
                {'name': 'creation date',
                 'path': '@event_create_date', 'default': None},
                {'name': 'hostname', 'path': 'agent.hostname', 'default': None},
                {'name': 'process name', 'path': 'process_name', 'default': None},
                {'name': 'image name', 'path': 'image_name', 'default': None},
                {'name': 'command line', 'path': 'commandline', 'default': None},
                {'name': 'integrity level',
                 'path': 'integrity_level', 'default': None},
                {'name': 'parent image', 'path': 'parent_image', 'default': None},
                {'name': 'parent command line',
                 'path': 'parent_commandline', 'default': None},
                {'name': 'username', 'path': 'username', 'default': None},
                {'name': 'signed', 'path': 'signed', 'default': None},
                {'name': 'signer', 'path': 'signature_info.signer_info.display_name',
                 'default': None},
                {'name': 'md5', 'path': 'hashes.md5', 'default': None},
                {'name': 'sha1', 'path': 'hashes.sha1', 'default': None},
                {'name': 'sha256', 'path': 'hashes.sha256', 'default': None},
                {'name': 'process UUID', 'path': 'process_unique_id', 'default': None},
                {'name': 'agent id', 'path': 'agent.agentid', 'default': None}
            ],
            'link': {
                'link_href': None,
                'transform': __generate_view_link_for_hash
            }
        },
        'getBinary': {
            'api_endpoint': '/api/data/telemetry/Binary/',
            'title': 'Binary download',
            'task_title': 'Analyze binary',
            'inputs': [
                {'name': 'hash', 'filter': 'hash',
                 'transform': __get_hash_parameter, 'mandatory': True}
            ],
            'fields': [
                {'name': 'path', 'path': 'paths', 'default': None,
                 'transform': __flatten_table},
                {'name': 'size', 'path': 'size', 'default': None},
                {'name': 'signed', 'path': 'signed', 'default': None},
                {'name': 'signer', 'path': 'signature_info.signer_info.display_name',
                 'default': None},
                {'name': 'md5', 'path': 'hashes.md5', 'default': None},
                {'name': 'sha1', 'path': 'hashes.sha1', 'default': None},
                {'name': 'sha256', 'path': 'hashes.sha256', 'default': None},
                {'name': 'download_link', 'path': 'hashes.sha256', 'default': None,
                 'transform': __generate_link_for_binary, 'is_url': True, 'link_text': 'Download'}
            ]
        },
        'searchSourceIP': {
            'api_endpoint': '/api/data/telemetry/Network/',
            'title': 'IP search',
            'task_title': 'Review Source IP search in telemetry',
            'inputs': [
                {'name': 'ip', 'filter': 'saddr',
                 'transform': __get_source_ip, 'mandatory': True},
                {'name': 'limit', 'filter': 'limit'}
            ],
            'fields': [
                {'name': 'creation date',
                 'path': '@event_create_date', 'default': None},
                {'name': 'hostname', 'path': 'agent.hostname', 'default': None},
                {'name': 'image name', 'path': 'image_name', 'default': None},
                {'name': 'username', 'path': 'username', 'default': None},
                {'name': 'source address', 'path': 'saddr', 'default': None},
                {'name': 'source port', 'path': 'sport', 'default': None},
                {'name': 'destination address',
                 'path': 'daddr', 'default': None},
                {'name': 'destination port', 'path': 'dport', 'default': None},
                {'name': 'direction', 'path': 'direction', 'default': None},
            ],
            'link': {
                'link_href': None,
                'transform': __generate_view_link_for_source_ip
            }
        },
        'searchDestinationIP': {
            'api_endpoint': '/api/data/telemetry/Network/',
            'title': 'IP search',
            'task_title': 'Review Destination IP search in telemetry',
            'inputs': [
                {'name': 'ip', 'filter': 'daddr',
                 'transform': __get_destination_ip, 'mandatory': True},
                {'name': 'limit', 'filter': 'limit'}
            ],
            'fields': [
                {'name': 'creation date',
                 'path': '@event_create_date', 'default': None},
                {'name': 'hostname', 'path': 'agent.hostname', 'default': None},
                {'name': 'image name', 'path': 'image_name', 'default': None},
                {'name': 'username', 'path': 'username', 'default': None},
                {'name': 'source address', 'path': 'saddr', 'default': None},
                {'name': 'source port', 'path': 'sport', 'default': None},
                {'name': 'destination address',
                 'path': 'daddr', 'default': None},
                {'name': 'destination port', 'path': 'dport', 'default': None},
                {'name': 'direction', 'path': 'direction', 'default': None},
            ],
            'link': {
                'link_href': None,
                'transform': __generate_view_link_for_destination_ip
            }
        },
        'searchDriverByFileName': {
            'api_endpoint': '/api/data/telemetry/DriverLoad/',
            'title': 'Driver load search',
            'task_title': 'Review driver load search in telemetry',
            'inputs': [
                {'name': 'filename', 'filter': 'imagename', 'mandatory': True},
                {'name': 'limit', 'filter': 'limit'}
            ],
            'fields': [
                {'name': 'loading time', 'path': '@timestamp', 'default': None},
                {'name': 'hostname', 'path': 'agent.hostname', 'default': None},
                {'name': 'image name', 'path': 'imagename', 'default': None},
                {'name': 'image path', 'path': 'imagepath', 'default': None},
                {'name': 'size', 'path': 'size', 'default': None},
                {'name': 'signed', 'path': 'signed', 'default': None},
                {'name': 'signer', 'path': 'signature_info.signer_info.display_name',
                 'default': None},
                {'name': 'md5', 'path': 'hashes.md5', 'default': None},
                {'name': 'sha1', 'path': 'hashes.sha1', 'default': None},
                {'name': 'sha256', 'path': 'hashes.sha256', 'default': None}
            ]
        },
        'searchDriverByHash': {
            'api_endpoint': '/api/data/telemetry/DriverLoad/',
            'title': 'Driver load search',
            'task_title': 'Review driver load search in telemetry',
            'inputs': [
                {'name': 'hash', 'filter': 'hash',
                 'transform': __get_hash_parameter, 'mandatory': True},
                {'name': 'limit', 'filter': 'limit'}
            ],
            'fields': [
                {'name': 'loading time', 'path': '@timestamp', 'default': None},
                {'name': 'hostname', 'path': 'agent.hostname', 'default': None},
                {'name': 'image name', 'path': 'imagename', 'default': None},
                {'name': 'image path', 'path': 'imagepath', 'default': None},
                {'name': 'size', 'path': 'size', 'default': None},
                {'name': 'signed', 'path': 'signed', 'default': None},
                {'name': 'signer', 'path': 'signature_info.signer_info.display_name',
                 'default': None},
                {'name': 'md5', 'path': 'hashes.md5', 'default': None},
                {'name': 'sha1', 'path': 'hashes.sha1', 'default': None},
                {'name': 'sha256', 'path': 'hashes.sha256', 'default': None}
            ]
        }

    }

    """
       Fetches security events from a HarfangLab EDR manager

       :type first_fetch: ``int``
       :param first_fetch: The number of days to look back for alerts

       :type alert_status: ``str``
       :param alert_status: Status of alerts to fetch ('ACTIVE' for alerts in the new, probable_false_positive or investigating statuses, 'CLOSED' for alerts in the closed or false_positive states, None for all alerts

       :type alert_type: ``str``
       :param alert_type: A comma-separated list of alert types (e.g. 'sigma,yara,hlai') or None to fetch all types

       :type min_severity: ``int``
       :param min_severity: The minimum severity of alerts to fetch ('Informational' or None for Informational and higher, 'Low' for Low and higher, 'Medium' for Medium and higer, 'High' for High and higher, 'Critical' for Critical)

       :type max_fetch: ``int``
       :param max_fetch: The maximum number of alerts to fetch (None to remove the limit)

       :type last_fetch: ``int``
       :param last_fetch: The timestamp in micro-seconds of the last fetch time

       :type delay: ``int``
       :param delay: Number of seconds back in the past for the upper limit of security event timestamps (keep a value of minimum 120 secondes)

       :type exclude_rules: ``List[str]``
       :param exclude_rules: The list of rule names to exclude (case insensitive)

       :return: A tuple with the last fetch time in micro-seconds since epoch and the list of security events
       :rtype: ``(int,List[Any])``
    """

    def fetch_security_events(self, first_fetch = None, alert_status = None, alert_type = None, min_severity = None, max_fetch = None, last_fetch = None, delay = 0, exclude_rules = None):

        url = f'{self.base_url}/api/data/alert/alert/Alert/'
        last_fetch = None
        max_results = None
        days = 0
        excluded_rules = set()

        if exclude_rules:
            excluded_rules = [x.lower() for x in exclude_rules]

        if first_fetch:
            try:
                days = int(first_fetch)
            except Exception as e:
                days = 0

        first_fetch_time = int(datetime.timestamp(
            datetime.now() - timedelta(days=days)) * 1000000)

        if not min_severity:
            min_severity = HarfangLabConnector.SEVERITIES[0]

        if max_fetch:
            try:
                max_results = int(max_fetch)
            except Exception as e:
                max_results = None

        severity = ','.join(HarfangLabConnector.SEVERITIES[HarfangLabConnector.SEVERITIES.index(min_severity):]).lower()

        if last_fetch is None:
            # if missing, use what provided via first_fetch_time
            last_fetch = first_fetch_time
        else:
            # otherwise use the stored last fetch
            try:
                last_fetch = int(last_fetch)
            except Exception as e:
                last_fetch = first_fetch_time

        if alert_status == 'ACTIVE':
            status = ['new', 'probable_false_positive', 'investigating']
        elif alert_status == 'CLOSED':
            status = ['closed', 'false_positive']
        else:
            status = None

        latest_created_time_us = int(last_fetch)

        incidents = []
        total_number_of_alerts = 0

        date_min = datetime.fromtimestamp(latest_created_time_us / 1000000)
        try:
            delay = int(delay)
        except Exception as e:
            delay = 0
        date_max = datetime.fromtimestamp(datetime.timestamp(datetime.now() - timedelta(seconds=int(delay))))

        cursor_min = date_min
        cursor_max = date_max

        self.logger.debug(f'Getting events between {date_min.strftime("%Y-%m-%dT%H:%M:%SZ")} and {date_max.strftime("%Y-%m-%dT%H:%M:%SZ")}')
        while cursor_min != cursor_max:
            offset = 0
            while True:
                args = {
                    'ordering': '+alert_time',
                    'level': severity,
                    'limit': HarfangLabConnector.MAX_NUMBER_OF_ALERTS_PER_CALL,
                    'offset': offset,
                    'alert_time__gt': cursor_min.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    'alert_time__lte': cursor_max.strftime('%Y-%m-%dT%H:%M:%SZ')
                }  # type: Dict[str,Any]

                if status:
                    args['status'] = ','.join(status)

                if alert_type:
                    args['alert_type'] = alert_type

                try:
                    u=f'{url}'+get_params(args)
                    response = self.hlSession.get(u)
                    response.raise_for_status()
                    results = response.json()
                except Exception as e:
                    raise Exception(f'Failed to fetch security events: {str(e)}')

                #print(
                #    f'Getting events between {date_min.strftime("%Y-%m-%dT%H:%M:%SZ")} and {date_max.strftime("%Y-%m-%dT%H:%M:%SZ")}: {results["count"]}')

                if results['count'] >= HarfangLabConnector.MAX_NUMBER_OF_ITEMS:
                    cursor_max = cursor_min + (cursor_max - cursor_min) / 2
                    break

                if 'count' in results and 'results' in results:
                    self.logger.debug(f'Fetched {total_number_of_alerts} / {results["count"]} events')

                    for alert in results['results']:

                        if alert.get('rule_name').lower() in excluded_rules:
                            continue

                        alert_id = alert.get('id', None)
                        alert['incident_link'] = f'{self.base_url}/security-event/{alert_id}/summary'
                        incident = {
                            'name': alert.get('rule_name', None),
                            'occurred': alert.get('alert_time', None),
                            'severity': HarfangLabConnector.SEVERITIES.index(alert.get('level', '').capitalize()) + 1,
                            'alert': alert
                        }

                        incidents.append(incident)

                        total_number_of_alerts += 1
                        if max_results and total_number_of_alerts >= max_results:
                            break

                offset += len(results['results'])
                if results['count'] == 0 or not results['next'] or (max_results and total_number_of_alerts >= max_results):
                    cursor_min = cursor_max
                    cursor_max = date_max
                    break

            if max_results and total_number_of_alerts >= max_results:
                break

        last_fetch = int(datetime.timestamp(date_max)*1000000)
        return (last_fetch, incidents)

    """
       Get a security event by ID

       :type event_id: ``str``
       :param event_id: The agent security event ID
    """
    def get_event_by_id(self, event_id):
        try:
            return self.hlSession.get(
                url=f'{self.base_url}/api/data/alert/alert/Alert/{event_id}/details/'
            ).json()

        except Exception as e:
            raise Exception(f'Failed to get security event information: {str(e)}')


    """
       Search an endpoint in HarfangLab EDR manager

       :type hostname: ``str``
       :param hostname: The agent hostname

       :type ostype: ``str``
       :param ostype: The agent platform ("windows", "linux", "macos")

       :type status: ``str``
       :param status: The agent status ("online", "offline")

       :type offset: ``Integer``
       :param offset: The search offset

       :type limit: ``Integer``
       :param limit: The search total number of records to fetch per call

       :type fields: ``List[str]``
       :param fields: The list of fields to provide in the output

       :type format: ``str``
       :param format: The output format (either 'mardown' or 'html')

       :return: The list of searched endpoints
       :rtype: ``Dict[str,Any]``
    """
    def search_endpoint(self, hostname=None, ostype=None, status=None, offset=0, limit=10, fields=None, format='markdown'):

        data = {
            'hostname': hostname,
            'ostype': ostype,
            'status': status,
            'offset': offset,
            'limit': limit
        }

        try:
            result = {}
            results = self.hlSession.get(
                url=f'{self.base_url}/api/data/endpoint/Agent/',
                params=data
            ).json()['results']

            result['message'] = 'OK'
            result['output'] = results
            result['count'] = len(results)

            result['markdown'] = get_markdown_from_table(
                None, results, headers=fields)

            if format == 'html':
                result['html'] = markdown.markdown(result['markdown'], extensions=['tables'])
                del (result['markdown'])

            return result

        except Exception as e:
            raise Exception(f'Failed to search endpoint: {str(e)}')

    def search_telemetry(self, service_name, args, format='markdown'):
        """
           Search in HarfangLab telemetry and returns a markdown table with the search results

           :type service_name: ``str``
           :param service_name: The name of the telemetry search service ('searchHash', 'getBinary', 'searchSourceIP', 'searchDestinationIP', 'searchDriverByFileName', 'searchDriverByHash')

           :type args: ``Dict[str, str]``
           :param args: The arguments for the telemetry search (ip, hash, filename...)

           :type format: ``str``
           :param format: The output format (either 'mardown' or 'html')

           :return: A dict with the results with the following keys: 'message' (message associated to the operation), 'output' (the JSON table with the results), 'markdown' (the markdown table).
           :rtype: ``Dict[str,Any]``
        """

        result = {}
        result['message'] = 'Failed'
        result['markdown'] = ''
        serv = None
        if service_name in HarfangLabConnector.TELEMETRY_SEARCHES:
            serv = HarfangLabConnector.TELEMETRY_SEARCHES[service_name]
        else:
            return

        url = f'{self.base_url}{serv["api_endpoint"]}'
        params = {}

        for field in serv['inputs']:
            func = field.get('transform', None)
            data = args.get(field['name'], None)
            mandatory = field.get('mandatory', False)
            #if not data and mandatory:
            #    raise Exception(
            #        f'Mismatch between the observable type and what the responder expects ({field["name"]})')
            if func:
                (f, v) = func(self, data)
                params[f] = v
            elif data:
                params[field['filter']] = data

        try:
            response = self.hlSession.get(url=url, params=params)
            response.raise_for_status()
        except Exception as e:
            raise Exception(f'Failed to search in telemetry %s' % (str(e)))

        response = response.json()
        output = []
        url_keys = {}
        count = response['count']
        for x in response['results']:
            res = {}
            for f in serv['fields']:
                k = f['name']
                if 'is_url' in f:
                    url_keys[f['name']] = f.get('link_text', None)
                tokens = f['path'].split('.')
                v = x
                for t in tokens:
                    if v:
                        v = v.get(t, None)
                    else:
                        v = f['default']
                func = None
                if 'transform' in f.keys():
                    func = f.get('transform')
                    v = func(self, v)
                res[k] = v

            output.append(res)

        link = None
        if 'link' in serv:
            if 'transform' in serv['link'].keys():
                func = serv['link'].get('transform')
                if func:
                    link = func(self, params)
            if not link:
                link = serv.get('link',{}).get('link_href')

        result['search_type'] = service_name
        result['args'] = args
        result['message'] = 'OK'
        result['title'] = serv['title']
        result['output'] = output
        result['count'] = count
        result['link'] = link


        headers = []
        for h in serv['fields']:
            headers.append(h['name'])

        result['markdown'] += f'### {serv["title"]}\n\n'
        result['markdown'] += f'#### Search details\n\n'

        search_metadata = args.copy()
        search_metadata['Search Type'] = service_name
        search_metadata['Total number of hits'] = count
        search_metadata['Investigation link'] = link

        result['markdown'] += get_markdown_from_table(
            None, search_metadata, headers=search_metadata.keys())
        result['markdown'] += f'#### Results (fetched {len(output)}/{count} entries)\n\n'
        result['markdown'] += get_markdown_from_table(
            None, output, headers=headers, url_keys=url_keys)

        if format == 'html':
            result['html'] = markdown.markdown(result['markdown'], extensions=['tables'])
            del(result['markdown'])

        return result

    def search_multiple_iocs_in_telemetry(self, iocs, limit, format='markdown', search_types = None):
        """
           Search multiple IOCs in HarfangLab telemetry and returns a markdown table with the search results

           :type iocs: ``List[Dict[str,str]]``
           :param iocs: The IOCs to search in the following format [{'type': 'md5', value: '1234567890ABCDEF1234567890ABCDEF'}, ...] (ip, hash, filename...)

           :type limit: ``Integer``
           :param limit: Limits the number of hit results for each IOC to this number.

           :type format: ``str``
           :param format: The output format (either 'mardown' or 'html')

           :type search_types: ``Set[Str]``
           :param search_types: Indicates which types of search to perform.

           :return: A dict with the results with the following keys: 'message' (message associated to the operation), 'output' (the JSON table with the results), 'markdown' (the markdown table).
           :rtype: ``Dict[str,Any]``
        """

        url_keys = {}
        results = {}
        output = []
        exception_count = 0
        success_count = 0
        results['output'] = []
        for ioc in iocs:
            for search_type in search_types:
                try:
                    res = None

                    if ioc.get('type')[0:2] == 'ip' and search_type in ['searchSourceIP', 'searchDestinationIP']:
                        res = self.search_telemetry(search_type, {'ip': ioc.get('value'), 'limit': limit})
                    elif ioc.get('type') in ['hash', 'md5', 'sha1', 'sha256'] and search_type in ['searchHash', 'searchDriverByHash']:
                        res = self.search_telemetry(search_type, {'hash': ioc.get('value'), 'limit': limit})

                    if res:
                        search_result = ioc.copy()
                        search_result['seach_type'] = search_type
                        search_result['count'] = res['count']
                        search_result['markdown'] = res['markdown']
                        search_result['output'] = res['output']
                        search_result['message'] = 'OK'
                        output.append({
                            'IOC Type': ioc.get('type'),
                            'IOC Value': ioc.get('value'),
                            'Search Type': search_type,
                            'Hits count': res['count'],
                            'Investigation link': res['link']
                        })
                        success_count += 1
                        results['output'].append(search_result)
                except Exception as e:
                    search_result['message'] = f'Failed to search IOC {ioc.get("value")}: {str(e)}'
                    exception_count += 1
                    results['output'].append(search_result)

        if success_count > 0:
            if exception_count:
                results['message'] = 'Partially OK'
            else:
                results['message'] = 'OK'
        else:
            results['message'] = 'Failed'

        url_keys['Investigation link'] = 'View details'

        results['markdown'] = ''
        results['markdown'] += f'### IOC search\n\n'
        results['markdown'] += f'#### Synthesis\n\n'
        results['markdown'] += get_markdown_from_table(
            None, output, headers=['IOC Type', 'IOC Value', 'Search Type', 'Hits count', 'Investigation link'], url_keys=url_keys)

        results['title'] = 'IOC search'

        if format == 'html':
            results['html'] = markdown.markdown(results['markdown'], extensions=['tables'])
            del(results['markdown'])

        return results


    def run_job(self, job_name, agent_id, job_title = None, job_description = None, job_timeout = 600, format = 'markdown', request_api_endpoint = None):
        """
           Run a HarfangLab job and returns a markdown table with the results

           :type job_name: ``str``
           :param job_name: The job name from the JOBS description to trigger

           :type agent_id: ``str``
           :param agent_id: The agent identifier to run the job on

           :type job_title: ``str``
           :param job_title: The job title

           :type job_description: ``str``
           :param job_description: The job description

           :type job_timeout: ``int``
           :param job_timeout: The job timeout (in seconds)

           :type format: ``str``
           :param format: The output format (either 'mardown' or 'html')

           :type request_api_endpoint: ``str``
           :param request_api_endpoint: The request api endpoint that override the one defined in the JOBS structure

           :return: A dict with the results with the following keys: 'message' (message associated to the operation), 'output' (the JSON table with the results), 'markdown' (the markdown table) if the output format is mardown or 'html' if the output format is html.
           :rtype: ``Dict[str,Any]``
        """

        result = {}
        result['message'] = 'Failed'
        result['markdown'] = ''

        job = None
        if job_name in HarfangLabConnector.JOBS:
            job = HarfangLabConnector.JOBS[job_name]
        else:
            raise Exception('Unknown service')

        if not agent_id:
            raise Exception('No agent identifier provided.')

        """ Create job """
        api_endpoint = None
        if request_api_endpoint:
            api_endpoint = request_api_endpoint
        else:
            api_endpoint = job["request_api_endpoint"]
        if not api_endpoint:
            raise Exception('No API endpoint associated to the job name')

        url = f'{self.base_url}{api_endpoint}'

        data = {
            'title': job_title,
            'description': job_description,
            'targets': {'agents': [agent_id]},
            'actions': [
                {
                    'value': job.get('action', None),
                    'params': job.get('parameters', None),
                }
            ]
        }

        try:
            response = self.hlSession.post(url=url, json=data)
            response.raise_for_status()
            data = response.json()
            if isinstance(data, list):
                if len(data) == 0:
                    raise Exception(
                        'Failed to start job (wrong agent identifier ?)')
                job_id = data[0]['id']
            elif isinstance(data, dict):
                job_id = data['job_id']

        except Exception as e:
            raise Exception('Failed to start job: %s' % (str(e)))

        """ Get job status """
        url = f'{self.base_url}{job["status_api_endpoint"]}{job_id}/'

        duration = 0
        polling_period = 5

        while duration < job_timeout:
            try:
                response = self.hlSession.get(url=url)
                response.raise_for_status()
                info = response.json()
            except Exception as e:
                raise Exception('Failed to get job status: %s' % (str(e)))

            status = "running"

            if info['instance'] == info['done']:
                status = "finished"
            elif info['error'] > 0:
                status = "error"
            elif info['canceled'] > 0:
                status = "canceled"
            elif info['waiting'] > 0:
                status = "waiting"
            elif info['running'] > 0:
                status = "running"
            elif info['injecting'] > 0:
                status = "injecting"

            if status in ['error', 'canceled']:
                result['message'] = 'Job execution failed'
                result['markdown'] = 'Job execution failed'
                return result
            if status == 'finished':
                time.sleep(polling_period)
                break
            time.sleep(polling_period)
            duration += polling_period

        """ Get Job results """
        fields = []
        for f in job['fields']:
            fields.append(f['path'])
        fields_str = ','.join(fields)
        url = f'{self.base_url}{job["result_api_endpoint"]}?limit=10000&job_id={job_id}&fields={fields_str}'

        if job['ordering'] is not None:
            url += f'&ordering={job["ordering"]}'

        try:
            retries = 0
            while retries < 3:
                response = self.hlSession.get(url=url)
                response.raise_for_status()
                data = response.json()
                if data['count'] > 0:
                    break
                else:
                    time.sleep(10)
                    retries += 1
        except Exception as e:
            raise Exception('Failed to get job results: %s' % (str(e)))

        output = []
        url_keys = {}
        for x in data['results']:
            res = {}
            for f in job['fields']:
                k = f['name']
                if 'is_url' in f:
                    url_keys[f['name']] = f.get('link_text', None)

                tokens = f['path'].split('.')
                v = x
                for t in tokens:
                    if v:
                        v = v.get(t, None)
                    else:
                        v = f['default']
                func = None
                if 'transform' in f.keys():
                    func = f.get('transform')
                    v = func(self, v)
                res[k] = v

            output.append(res)

        result['message'] = 'OK'
        result['output'] = output
        result['title'] = job['title']

        headers = []
        for h in job['fields']:
            headers.append(h['name'])
        result['markdown'] = get_markdown_from_table(
            job['title'], output, headers=headers, url_keys=url_keys)

        if format == 'html':
            result['html'] = markdown.markdown(result['markdown'], extensions=['tables'])
            del(result['markdown'])

        return result

    def dump_process(self, agent_id, process_uuid, format='markdown', job_timeout = 600):
        """
           Dump a process

           :type agent_id: ``str``
           :param agent_id: The agent identifier to run the job on

           :type format: ``str``
           :param format: The output format (either 'mardown' or 'html')

           :type job_timeout: ``int``
           :param job_timeout: The job timeout (in seconds)

           :return: A dict with the results with the following keys: 'message' (message associated to the operation), 'output' (the JSON table with the results), 'markdown' (the markdown table).
           :rtype: ``Dict[str,Any]``
        """
        return self.run_job('dumpProcess', agent_id, job_timeout, format, f'/api/data/telemetry/Processes/{process_uuid}/requestDumpProcess/')

    def kill_process(self, agent_id, process_uuid, format = 'markdown', job_timeout = 600):
        """
           Kill a process

           :type agent_id: ``str``
           :param agent_id: The agent identifier to run the job on

           :type process_uuid: ``str``
           :param process_uuid: The process unique identifier (as defined in the HarfangLab EDR Manager)

           :type format: ``str``
           :param format: The output format (either 'mardown' or 'html')

           :type job_timeout: ``int``
           :param job_timeout: The job timeout (in seconds)

           :return: A dict with the results with the following keys: 'message' (message associated to the operation), 'output' (the JSON table with the results), 'markdown' (the markdown table).
           :rtype: ``Dict[str,Any]``
        """
        return self.run_job('killProcess', agent_id, job_timeout, format, f'/api/data/telemetry/Processes/{process_uuid}/requestKillProcess/')

    def list_sources(self, source_type, source_name=None):
        '''
            List existing Threat Intelligence sources

            :param source_type: Source type

            :param source_name: Source name

            :returns A list of sources matching input criteria
        '''
        data = {}

        if source_name:
            data['search'] = source_name

        if source_type == 'yara':
            url_suffix = '/api/data/threat_intelligence/YaraSource/'
        elif source_type == 'sigma':
            url_suffix = '/api/data/threat_intelligence/SigmaSource/'
        elif source_type == 'ioc':
            url_suffix = '/api/data/threat_intelligence/IOCSource/'

        url = f'{self.base_url}{url_suffix}'

        try:
            response = self.hlSession.get(url, params=data)
            response.raise_for_status()
        except Exception as e:
            raise Exception(f'Failed to list sources: %s'  % (str(e)))

        return response.json()['results']

    def get_ioc(self, ioc_value, source_id):
        '''
            Get an IOC in a source identified by its id

            :param ioc_value: IOC value to search

            :param source_id: Identifier of the Threat Intelligence source

            :returns: true if IOC exists, else false.
        '''
        data = {
            'source_id': source_id,
            'search': ioc_value
        }

        url = f'{self.base_url}/api/data/threat_intelligence/IOCRule/'
        try:
            response = self.hlSession.get(url, params=data)
            response.raise_for_status()
        except Exception as e:
            raise Exception(f'Failed to search IOC {ioc_value}: %s' % (str(e)))
        results = response.json()

        if results['count'] > 0:
            for ioc in results['results']:
                if ioc['value'] == ioc_value:
                    return ioc
        return None

    def add_ioc_to_source(self, ioc_value, ioc_type, ioc_comment, ioc_status, source_name):
        '''
            Add an IOC to a Threat Intelligence source

            :param ioc_value: IOC value

            :param ioc_type: IOC type (ip, hash, filename...)

            :param ioc_comment: Comment associated to an IOC

            :param source_name: Name of the Threat Intelligence source to add the IOC to
        '''

        try:
            results = self.list_sources(source_type='ioc', source_name=source_name)
        except Exception as e:
            raise Exception(f'Failed to list sources and identify {source_name}: %s' % (str(e)))

        source_id = None

        for source in results:
            self.logger.debug(f'Found source {source["name"]}')
            if source['name'] == source_name:
                source_id = source['id']

        self.logger.debug(f'Searching for IOC')
        if self.get_ioc(ioc_value, source_id):
            return
        else:

            testing_status = None

            if ioc_status == 'testing':
                testing_status = 'in_progress'

            port = None
            if ioc_type[0:2] == 'ip':
                res = ioc_value.split('|')
                if len(res) >= 2:
                    ioc_value = res[0]
                    port = res[1]

            data = {
                'type': ioc_type,
                'value': ioc_value,
                'port': port,
                'comment': ioc_comment,
                'source_id': source_id,
                'hl_status': ioc_status,
                'hl_local_testing_status': testing_status
            }

            url = f'{self.base_url}/api/data/threat_intelligence/IOCRule/'

            self.logger.debug(f'Adding for IOC')

            try:
                response = self.hlSession.post(url, json=data)
                response.raise_for_status()
                self.logger.debug(f'IOC added')
            except Exception as e:
                raise Exception(f'Failed to add IOC {ioc_value} to source {source_id}: %s' % (str(e)))

    def change_security_event_status(self, security_event_id, status):
        '''
            Change the status of a security event

            :param security_event_id: Security Event ID or list of IDs

            :param status: The security event status ('New', 'Investigating', 'False Positive' or 'Closed'
        '''

        try:
            url = f'{self.base_url}/api/data/alert/alert/Alert/tag/'

            data = {}  # type: Dict[str,Any]

            if isinstance(security_event_id, list):
                data['ids'] = security_event_id
            else:
                data['ids'] = [security_event_id]

            if status.lower() == 'new':
                data['new_status'] = 'new'
            elif status.lower() == 'investigating':
                data['new_status'] = 'investigating'
            elif status.lower() == 'false positive' or status.lower() == 'false_positive':
                data['new_status'] = 'false_positive'
            elif status.lower() == 'closed':
                data['new_status'] = 'closed'
            else:
                raise Exception('Status must be either new, investigating, false_positive or closed')

            response = self.hlSession.post(url=url, json=data)
            response.raise_for_status()

        except Exception as e:
            raise Exception(f'Failed to change security event status: %s' % (str(e)))

    def isolate_endpoint(self, agent_id):
        '''
            Isolate an endpoint

            :param agent_id: Agent identifier

            :return: A string with the result message
        '''
        url = f'{self.base_url}/api/data/endpoint/Agent/{agent_id}/isolate/'

        if not agent_id:
            raise Exception(
                'No agent Id provided')

        try:
            response = self.hlSession.post(url=url)
            if response.status_code != 200:
                raise Exception(
                    f'Failed to isolate host {agent_id}: {response.status_code} ({response.reason})')
            else:
                """
                Isolation has successfully been requested. We need to check that the policy allows isolation.
                """
                if len(response.json().get('policy_not_allowed', [])) > 0:
                    raise Exception(
                        f'Unable to isolate host {agent_id} since isolation is not allowed in the policy.')

                """
                Isolation has successfully been requested and policy allows isolation. We need to check when isolation is effective.
                """
                polling_period = 2
                sleep_time = 60

                duration = 0
                while duration < 3 * sleep_time:

                    url = f'{self.base_url}/api/data/endpoint/Agent/{agent_id}/'
                    response = self.hlSession.get(url=url)
                    if response.status_code != 200:
                        raise Exception(
                            f'Failed to get agent\'s status for host {agent_id}: {response.status_code} ({response.reason})')
                    else:
                        sleep_time = int(response.json().get(
                            'policy', {}).get('sleeptime', 60)) * 2
                        isolation_state = response.json().get('isolation_state')

                        if isolation_state:
                            return f'Host {agent_id} successfully isolated'
                        else:
                            duration += polling_period
                            time.sleep(polling_period)
                raise Exception(
                    f'Host isolation successfully requested but host never switched to an isolated state...')

        except requests.exceptions.RequestException as e:
            raise Exception(e)

    def unisolate_endpoint(self, agent_id):
        '''
            Unisolate an endpoint

            :param agent_id: Agent identifier

            :return: A string with the result message
        '''

        url = f'{self.base_url}/api/data/endpoint/Agent/{agent_id}/deisolate/'

        if not agent_id:
            raise Exception(
                'No agent Id provided')

        try:
            response = self.hlSession.post(url=url)
            if response.status_code != 200:
                raise Exception(
                    f'Failed to unisolate host {agent_id}: {response.status_code} ({response.reason})')
            else:

                """
                Unisolation has successfully been requested. We need to check when unisolation is effective.
                """
                polling_period = 2
                sleep_time = 60

                duration = 0
                while duration < 3 * sleep_time:

                    url = f'{self.base_url}/api/data/endpoint/Agent/{agent_id}/'
                    response = self.hlSession.get(url=url)
                    if response.status_code != 200:
                        raise Exception(
                            f'Failed to get agent\'s status for host {agent_id}: {response.status_code} ({response.reason})')
                    else:
                        sleep_time = int(response.json().get(
                            'policy', {}).get('sleeptime', 60))*2
                        isolation_state = response.json().get('isolation_state')

                        if not isolation_state:
                            return f'Host {agent_id} successfully unisolated'

                        else:
                            duration += polling_period
                            time.sleep(polling_period)
                raise Exception(
                    f'Host unisolation successfully requested but host never switched to an unisolated state...')

        except requests.exceptions.RequestException as e:
            raise Exception(e)
