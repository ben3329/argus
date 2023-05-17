from pydantic import BaseModel, validator, EmailStr, constr
import type_alias
from typing import Optional, List, Dict, Union, Literal
from collections import OrderedDict
from dataclasses import dataclass
import matplotlib.pyplot as plt
from io import BytesIO
import pandas as pd
from croniter import croniter
from built_in_scripts import *


class AccessCredentialModel(BaseModel):
    access_type: type_alias.ACCESS_TYPE
    username: str
    password: str = None
    secret: str = None


class UserDefinedScriptModel(BaseModel):
    name: constr(min_length=1)
    language: Literal['python2', 'python3', 'bash']
    code: str
    output_type: type_alias.OUTPUT_TYPE
    fields: List[str]
    parameters: List[str]
    revision: int



class AssetModel(BaseModel):
    ip: str
    port: int
    asset_type: str
    access_credential: AccessCredentialModel


class ScrapeModel(BaseModel):
    name: constr(min_length=1)
    asset: AssetModel
    scrape_category: type_alias.SCRAPE_CATEGORY
    scrape_fields: Optional[List[str]] = None
    scrape_parameters: Optional[Dict[str, str]] = None
    user_defined_script: Optional[UserDefinedScriptModel] = None
    interval: int
    report_list: List[type_alias.REPORT_TYPE]
    report_time: Optional[str] = None
    recipients: List[EmailStr] = []

    @validator('report_time')
    def validate_report_time(cls, v):
        try:
            if v:
                croniter(v)
            return v
        except:
            raise ValueError('Invalid report time format')

    @validator('scrape_fields')
    def validate_scrape_fields(cls, v, values, **kwargs):
        if 'scrape_category' in values:
            valid_fields = {
                'linux_system_memory': linux_system_memory.LinuxSystemMemory._fields
            }
            if values.get('user_defined_script'):
                valid_fields['user_defined_script'] = values['user_defined_script']['fields']
            category = values['scrape_category']
            if category in valid_fields:
                if v is not None and any(field not in valid_fields[category] for field in v):
                    raise ValueError(f'Invalid fields for category {category}')
        return v

    @validator('scrape_parameters')
    def validate_scrape_parameters(cls, v, values, **kwargs):
        if 'scrape_parameters' in values:
            valid_parameters = {
                'linux_system_memory': linux_system_memory.LinuxSystemMemory._parameters
            }
            if values.get('user_defined_script'):
                valid_parameters['user_defined_script'] = values['user_defined_script']['parameters']
            category = values['scrape_category']
            if category in valid_parameters:
                if v is not None and any(key not in valid_parameters[category] for key in v):
                    raise ValueError(f'Invalid parameters for category {category}')
        return v

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
        image_data = img_buffer.getvalue()
        plt.close()
        return image_data

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
