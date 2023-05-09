from typing import Literal, TypeAlias, Union

# access_credential
ACCESS_TYPE: TypeAlias = Literal['ssh_password', 'ssh_private_key']

# script
OUTPUT_TYPE: TypeAlias = Literal['none', 'json', 'csv']
LINUX_SYSTEM_MEMORY_FIELDS: TypeAlias = Literal['used', 'utilization']
# BUILT_IN_FIELDS: TypeAlias = Union[LINUX_SYSTEM_MEMORY_FIELDS]

# report
REPORT_TYPE_IMAGE: TypeAlias = Literal['graph24']
REPORT_TYPE_STATS: TypeAlias = Literal['avg24', 'var24', 'std24']
REPORT_TYPE_CHANGE: TypeAlias = Literal['diff', 'diff24']
REPORT_TYPE: TypeAlias = Union[REPORT_TYPE_IMAGE,
                               REPORT_TYPE_STATS, REPORT_TYPE_CHANGE]
