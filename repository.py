from sqlalchemy.orm import Session
from models import TradingResult


class TradingResultRepository:
    """
    Репозиторий для управления операциями с моделью TradingResult.

    Attributes:
        db (Session): Сессия базы данных для выполнения операций.
    """

    def __init__(self, db: Session):
        """
        Инициализация репозитория с сессией базы данных.

        Args:
            db (Session): Сессия базы данных для выполнения операций.
        """
        self.db = db

    def create(self, trading_result: TradingResult) -> TradingResult:
        """
        Создает новую запись TradingResult в базе данных.

        Args:
            trading_result (TradingResult): Объект TradingResult для добавления в базу данных.

        Returns:
            TradingResult: Созданный объект TradingResult с обновленными данными.
        """
        self.db.add(trading_result)
        self.db.commit()
        self.db.refresh(trading_result)
        return trading_result