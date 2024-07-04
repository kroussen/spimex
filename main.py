import pandas
from urllib.request import urlopen
from urllib.error import HTTPError
from datetime import datetime, timedelta
from typing import Optional, List, Dict

from repository import TradingResultRepository
from models import TradingResult
from database import SessionLocal, init_db

init_db()
db = SessionLocal()
repository = TradingResultRepository(db)


def check_file_availability(url: str) -> Optional[bytes]:
    """
    Проверяет доступность файла по указанному URL.

    Args:
        url (str): URL для проверки.

    Returns:
        Optional[bytes]: Содержимое файла в байтах, если файл доступен; None в противном случае.
    """
    try:
        response = urlopen(url=url)
        return response.read()
    except HTTPError:
        return None


def is_unit_of_measurement_metric_ton(file: pandas.DataFrame) -> bool:
    """
    Проверяет, является ли единицей измерения в файле метрическая тонна.

    Args:
        file (pandas.DataFrame): DataFrame, представляющий файл Excel.

    Returns:
        bool: True, если единицей измерения является метрическая тонна, иначе False.
    """
    return file.iloc[4].values[1] == 'Единица измерения: Метрическая тонна'


def parse_data(start_date: datetime, end_date: datetime) -> None:
    """
    Парсит данные за указанный период и сохраняет их в базу данных.

    Args:
        start_date (datetime): Начальная дата периода.
        end_date (datetime): Конечная дата периода.
    """
    current_date = start_date

    while current_date <= end_date:
        date_str = current_date.strftime('%Y%m%d')
        url = f'https://spimex.com/upload/reports/oil_xls/oil_xls_{date_str}162000.xls'

        if check_file_availability(url) is not None:
            all_data = get_data_from_excel(url, current_date)

            for data in all_data:
                trading_result = TradingResult(
                    exchange_product_id=data['exchange_product_id'],
                    exchange_product_name=data['exchange_product_name'],
                    oil_id=data['oil_id'],
                    delivery_basis_id=data['delivery_basis_id'],
                    delivery_basis_name=data['delivery_basis_name'],
                    delivery_type_id=data['delivery_type_id'],
                    volume=data['volume'],
                    total=data['total'],
                    count=data['count'],
                    date=data['date'],
                    created_on=datetime.now(),
                    updated_on=datetime.now()
                )

                repository.create(trading_result)

        current_date += timedelta(days=1)


def get_data_from_excel(url: str, file_date: datetime) -> List[Dict[str, str]]:
    """
    Извлекает данные из Excel файла по указанному URL.

    Args:
        url (str): URL Excel файла.
        file_date (datetime): Дата файла.

    Returns:
        List[Dict[str, str]]: Список словарей с данными, извлеченными из файла.
    """
    excel_file = pandas.read_excel(url)
    list_data = []

    if is_unit_of_measurement_metric_ton(excel_file):
        clear_date = excel_file.iloc[7:-2]
        positive_clear_data = clear_date[clear_date.iloc[:, 14].values != '-']

        for row in positive_clear_data.iloc[:, [1, 2, 3, 4, 5, 14]].values:
            data = {
                'exchange_product_id': row[0],
                'exchange_product_name': row[1],
                'oil_id': row[0][:4],
                'delivery_basis_id': row[0][4:7],
                'delivery_basis_name': row[2],
                'delivery_type_id': row[0][-1],
                'volume': row[3],
                'total': row[4],
                'count': row[5],
                'date': file_date.strftime('%d.%m.%Y'),
            }
            list_data.append(data)
    return list_data


if __name__ == "__main__":
    start_date = datetime(2023, 1, 1)
    final_date = datetime.now()
    parse_data(start_date, final_date)
