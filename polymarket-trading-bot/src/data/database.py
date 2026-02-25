"""数据库连接管理"""

from contextlib import contextmanager
from typing import Optional, Generator
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session, scoped_session
from sqlalchemy.pool import StaticPool
from loguru import logger

from .models import Base
from ..utils.config import get_config
from ..utils.exceptions import DatabaseError


class Database:
    """数据库管理类"""

    def __init__(self, config=None):
        """
        初始化数据库

        Args:
            config: 配置对象,如果不提供则使用全局配置
        """
        self.config = config or get_config()
        self._engine: Optional[Engine] = None
        self._session_factory: Optional[sessionmaker] = None
        self._scoped_session: Optional[scoped_session] = None

    def _get_database_url(self) -> str:
        """获取数据库URL"""
        db_config = self.config.database

        if db_config.type == 'sqlite':
            db_path = self.config.root_dir / db_config.sqlite_path
            db_path.parent.mkdir(parents=True, exist_ok=True)
            return f'sqlite:///{db_path}'
        elif db_config.type == 'postgresql':
            if db_config.postgresql_url:
                return db_config.postgresql_url
            else:
                raise DatabaseError("PostgreSQL配置不完整")
        else:
            raise DatabaseError(f"不支持的数据库类型: {db_config.type}")

    def get_engine(self) -> Engine:
        """获取数据库引擎"""
        if self._engine is None:
            database_url = self._get_database_url()

            # SQLite特殊配置
            if database_url.startswith('sqlite'):
                self._engine = create_engine(
                    database_url,
                    echo=self.config.debug,
                    connect_args={'check_same_thread': False},
                    poolclass=StaticPool
                )

                # 启用外键约束
                @event.listens_for(self._engine, "connect")
                def set_sqlite_pragma(dbapi_conn, connection_record):
                    cursor = dbapi_conn.cursor()
                    cursor.execute("PRAGMA foreign_keys=ON")
                    cursor.close()

            # PostgreSQL配置
            else:
                self._engine = create_engine(
                    database_url,
                    echo=self.config.debug,
                    pool_size=self.config.database.pool_size,
                    max_overflow=20,
                    pool_pre_ping=True  # 检测连接是否有效
                )

            logger.info(f"数据库引擎已创建: {database_url.split('@')[-1] if '@' in database_url else 'sqlite'}")

        return self._engine

    def get_session_factory(self) -> sessionmaker:
        """获取Session工厂"""
        if self._session_factory is None:
            engine = self.get_engine()
            self._session_factory = sessionmaker(
                bind=engine,
                autocommit=False,
                autoflush=False,
                expire_on_commit=False
            )
        return self._session_factory

    def get_scoped_session(self) -> scoped_session:
        """获取线程安全的Session"""
        if self._scoped_session is None:
            session_factory = self.get_session_factory()
            self._scoped_session = scoped_session(session_factory)
        return self._scoped_session

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        获取数据库会话的上下文管理器

        Yields:
            Session对象

        Example:
            with db.get_session() as session:
                markets = session.query(Market).all()
        """
        session = self.get_session_factory()()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"数据库会话错误: {e}")
            raise DatabaseError(f"数据库操作失败: {e}")
        finally:
            session.close()

    def init_db(self, drop_all: bool = False):
        """
        初始化数据库表

        Args:
            drop_all: 是否先删除所有表
        """
        try:
            engine = self.get_engine()

            if drop_all:
                logger.warning("删除所有数据库表...")
                Base.metadata.drop_all(engine)

            logger.info("创建数据库表...")
            Base.metadata.create_all(engine)
            logger.info("✓ 数据库表创建成功")

        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
            raise DatabaseError(f"数据库初始化失败: {e}")

    def check_connection(self) -> bool:
        """
        检查数据库连接

        Returns:
            连接是否正常
        """
        try:
            engine = self.get_engine()
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            return False

    def close(self):
        """关闭数据库连接"""
        if self._scoped_session:
            self._scoped_session.remove()

        if self._engine:
            self._engine.dispose()
            logger.info("数据库连接已关闭")


# 全局数据库实例
_db: Optional[Database] = None


def get_database() -> Database:
    """
    获取全局数据库实例

    Returns:
        Database实例
    """
    global _db
    if _db is None:
        _db = Database()
    return _db


def init_database(drop_all: bool = False):
    """
    初始化数据库

    Args:
        drop_all: 是否先删除所有表
    """
    db = get_database()
    db.init_db(drop_all=drop_all)


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """
    便捷函数: 获取数据库会话

    Yields:
        Session对象
    """
    db = get_database()
    with db.get_session() as session:
        yield session
