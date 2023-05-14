from typing import Literal, TypeAlias, Union

# access_credential
ACCESS_TYPE: TypeAlias = Literal['ssh_password', 'ssh_private_key']

# user_defined_script
OUTPUT_TYPE: TypeAlias = Literal['none', 'json', 'csv']

# scrape
SCRAPE_CATEGORY: TypeAlias = Literal['linux_system_memory', 'user_defined_script']

# report
REPORT_TYPE_IMAGE: TypeAlias = Literal['graph24']
REPORT_TYPE_STATS: TypeAlias = Literal['avg24', 'var24', 'std24']
REPORT_TYPE_CHANGE: TypeAlias = Literal['diff', 'diff24']
REPORT_TYPE: TypeAlias = Union[REPORT_TYPE_IMAGE,
                               REPORT_TYPE_STATS, REPORT_TYPE_CHANGE]
