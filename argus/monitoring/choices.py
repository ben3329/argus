from django.db import models


class AccessTypeChoices(models.TextChoices):
    ssh_password = 'ssh_password', 'SSH Password'
    ssh_private_key = 'ssh_private_key', 'SSH Private Key'

    def __str__(self) -> str:
        return self.value[1]


class AssetTypeChoices(models.TextChoices):
    linux = 'linux', 'Linux'

    def __str__(self) -> str:
        return self.value[1]


class LanguageChoices(models.TextChoices):
    python3 = 'python3'
    python2 = 'python2'
    shell = 'shell'


class OutputTypeChoices(models.TextChoices):
    csv = 'csv'
    json = 'json'
    none = 'none'


class ScrapeCategoryChoices(models.TextChoices):
    linux_system_memory = 'linux_system_memory', 'Linux System Memory'
    user_defined_script = 'user_defined_script', 'User Defined Script'

    def __str__(self) -> str:
        return self.value[1]


class LinuxSystemMemoryChoices(models.TextChoices):
    used = 'used', 'Used Memory. Unit: KB'
    utilization = 'utilization', 'Memory Used Rate. Unit: %'

    def __str__(self) -> str:
        return self.value[1]


class ReportListChoices(models.TextChoices):
    graph24 = 'graph24', 'Graph for 24 hours'
    avg24 = 'avg24', 'Average for 24 hours'
    var24 = 'var24', 'Variance for 24 hours'
    std24 = 'std24', 'Standard Deviation for 24 hours'
    diff = 'diff', 'Difference from first data'
    diff24 = 'diff24', 'Difference from last 24 hours data'

    def __str__(self) -> str:
        return self.value[1]
