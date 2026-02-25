"""数据库初始化脚本"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from loguru import logger
from src.data.database import init_database as init_db
from src.utils.config import get_config

def init_database():
    try:
        logger.info("=" * 60)
        logger.info("数据库初始化")
        logger.info("=" * 60)
        
        config = get_config()
        logger.info(f"数据库类型: {config.database.type}")
        
        if config.database.type == 'sqlite':
            db_path = config.root_dir / config.database.sqlite_path
            logger.info(f"数据库路径: {db_path}")
        
        init_db(drop_all=False)
        
        logger.info("=" * 60)
        logger.info("✓ 数据库初始化成功!")
        logger.info("=" * 60)
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}", exc_info=True)
        return 1
    return 0

if __name__ == "__main__":
    exit_code = init_database()
    sys.exit(exit_code)
