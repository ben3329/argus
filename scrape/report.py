from settings import *
from errors import *
from dataclass import ScrapeDTO
import type_alias

from typing import List
import aiosmtplib
import pandas as pd
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from premailer import Premailer
import base64


class Reporter(object):

    def create_image_message(self, data: ScrapeDTO, report_type: type_alias.REPORT_TYPE_IMAGE) -> str:
        match report_type:
            case 'graph24':
                image_data = base64.b64encode(data.graph_image_24h).decode()
                alt = '24-hour graph'
            case _:
                raise InvalidReportTypeError(report_type, data.name)
        return f'<img src="data:image/png;base64,{image_data}" alt="{alt}">'

    def create_stats_message(self, data: ScrapeDTO, report_type_list: List[type_alias.REPORT_TYPE_STATS]) -> str:
        title = f'<h3>Statistics Table for 24 hours</h3>\n'
        series_list = []
        series_keys = []
        for report_type in report_type_list:
            match report_type:
                case 'avg24':
                    series_list.append(data.average_24h)
                    series_keys.append('Average')
                case 'var24':
                    series_list.append(data.variance_24h)
                    series_keys.append('Variance')
                case 'std24':
                    series_list.append(data.std_deviation_24h)
                    series_keys.append('Standard Deviation')
                case _:
                    raise InvalidReportTypeError(report_type, data.name)

        df = pd.concat(series_list, axis=1, keys=series_keys)
        df = df.T.reset_index().rename(columns={'index': 'type'})
        html_table = df.to_html(index=False)
        html_table = html_table.replace(
            '<tr style="text-align: right;">', '<tr>')
        return title + html_table

    def create_change_message(self, data: ScrapeDTO, report_type: type_alias.REPORT_TYPE_CHANGE) -> str:
        match report_type:
            case 'diff':
                df = data.diff
                title = f'<h3>First-Last Table</h3>\n'
            case 'diff24':
                df = data.diff_24h
                title = f'<h3>First-Last Table for 24 hours</h3>\n'
            case _:
                raise InvalidReportTypeError(report_type, data.name)
        html_table = df.to_html(index=False)
        html_table = html_table.replace(
            '<tr style="text-align: right;">', '<tr>')
        return title + html_table

    async def send_email(self, data: ScrapeDTO, report_list: List[type_alias.REPORT_TYPE], recipients: List[str], css='email.css'):
        msg = MIMEMultipart()
        msg['Subject'] = f'Monitoring Report: {data.name}'
        msg['From'] = 'noreply@argus.com'
        msg['To'] = ', '.join(recipients)
        report_type_image_values = []
        report_type_stats_values = []
        report_type_change_values = []
        for report_type in report_list:
            match report_type:
                case 'graph24':
                    report_type_image_values.append(report_type)
                case 'avg24' | 'var24' | 'std24':
                    report_type_stats_values.append(report_type)
                case 'diff' | 'diff24':
                    report_type_change_values.append(report_type)
                case _:
                    raise InvalidReportTypeError(report_type, data.name)
        html_content = """
<html>
<head>
    <style type="text/css">
        {}
    </style>
</head>
<body>
    {}
</body>
</html>
"""
        report_html = ''
        for report_type in report_type_image_values:
            report_html += self.create_image_message(data, report_type)
        if report_type_stats_values:
            report_html += self.create_stats_message(
                data, report_type_stats_values)
        for report_type in report_type_change_values:
            report_html += self.create_change_message(data, report_type)
        with open(css, 'r') as file:
            css = file.read()
        premailer = Premailer(html_content.format(css, report_html))
        inlined_html = premailer.transform()
        msg.attach(MIMEText(inlined_html, 'html'))
        try:
            await aiosmtplib.send(
                msg, hostname=EMAIL_HOST, port=EMAIL_PORT,
                username=EMAIL_HOST_USER, password=EMAIL_HOST_PASSWORD)
        except Exception as e:
            raise SendMailError(str(e))
