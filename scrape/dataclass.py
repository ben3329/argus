from pydantic import BaseModel, validator, EmailStr
import type_alias
from typing import Optional, List, Dict, Union, Literal
from collections import OrderedDict
from dataclasses import dataclass
import matplotlib.pyplot as plt
from io import BytesIO
import pandas as pd
from croniter import croniter


class AccessCredentialModel(BaseModel):
    access_type: type_alias.ACCESS_TYPE
    username: str
    password: str = None
    secret: str = None


class UserDefinedScriptModel(BaseModel):
    name: str
    language: Literal['python2', 'python3', 'bash']
    code: str
    output_type: type_alias.OUTPUT_TYPE
    revision: int


class BuiltInScriptModel(BaseModel):
    category: Literal['linux_system_memory']
    fields: List[type_alias.LINUX_SYSTEM_MEMORY_FIELDS]
    parameter: Optional[Dict[str, str]] = None


class AssetModel(BaseModel):
    ip: str
    port: int
    asset_type: str
    access_credential: AccessCredentialModel


class ScrapeModel(BaseModel):
    name: str
    asset: AssetModel
    script: Union[BuiltInScriptModel, UserDefinedScriptModel]
    interval: int
    report_list: List[type_alias.REPORT_TYPE]
    report_time: Optional[str] = None
    recipients: List[EmailStr] = []

    @validator('report_time')
    def validate_report_time(cls, v):
        try:
            croniter(v)
            return v
        except:
            raise ValueError('Invalid report time format')

    @property
    def report_time_as_dict(self) -> OrderedDict:
        fields = self.report_time.split()
        return OrderedDict([
            ('minute', fields[0]),
            ('hour', fields[1]),
            ('day', fields[2]),
            ('month', fields[3]),
            ('day_of_week', fields[4])
        ])


@dataclass
class ScrapeDTO:
    name: str
    first_data: pd.DataFrame
    last_24h_data: pd.DataFrame

    @property
    def average_24h(self) -> pd.Series:
        return self.last_24h_data.iloc[:, 1:].mean()

    @property
    def variance_24h(self) -> pd.Series:
        return self.last_24h_data.iloc[:, 1:].var(ddof=0)

    @property
    def std_deviation_24h(self) -> pd.Series:
        return self.last_24h_data.iloc[:, 1:].std(ddof=0)

    @property
    def graph_image_24h(self) -> bytes:
        data = self.last_24h_data.set_index('datetime')
        fig, axes = plt.subplots(nrows=len(data.columns), ncols=1, sharex=True)
        for i, col in enumerate(data.columns):
            data[col].plot(ax=axes[i], title=col)
            axes[i].set_xlabel('')
        fig.tight_layout()
        img_buffer = BytesIO()
        fig.savefig(img_buffer, format='png')
        return img_buffer.getvalue()

    @property
    def diff(self) -> pd.DataFrame:
        first_row = self.first_data.iloc[0].copy()
        first_row['datetime'] = first_row['datetime'].strftime(
            '%Y-%m-%d %H:%M:%S')
        last_row = self.last_24h_data.iloc[-1].copy()
        last_row['datetime'] = last_row['datetime'].strftime(
            '%Y-%m-%d %H:%M:%S')
        diff_row = pd.Series({'datetime': 'diff'})
        for col in self.first_data.columns[1:]:
            if col != 'datetime':
                diff_row[col] = last_row[col] - first_row[col]
        result = pd.concat([first_row, last_row, diff_row], axis=1).T
        return result

    @property
    def diff_24h(self) -> pd.DataFrame:
        first_row = self.last_24h_data.iloc[0].copy()
        first_row['datetime'] = first_row['datetime'].strftime(
            '%Y-%m-%d %H:%M:%S')
        last_row = self.last_24h_data.iloc[-1].copy()
        last_row['datetime'] = last_row['datetime'].strftime(
            '%Y-%m-%d %H:%M:%S')
        diff_row = pd.Series({'datetime': 'diff'})
        for col in self.last_24h_data.columns[1:]:
            if col != 'datetime':
                diff_row[col] = last_row[col] - first_row[col]
        result = pd.concat([first_row, last_row, diff_row], axis=1).T
        return result
