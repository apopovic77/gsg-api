"""
Database Connection Manager for MSSQL
"""
import pyodbc
from contextlib import contextmanager
from typing import Generator, List, Dict, Any, Optional
from .config import get_settings


class DatabaseManager:
    """Manages MSSQL database connections"""

    def __init__(self):
        self._connection_string = get_settings().mssql_connection_string

    @contextmanager
    def get_connection(self) -> Generator[pyodbc.Connection, None, None]:
        """Get a database connection (context manager)"""
        conn = pyodbc.connect(self._connection_string)
        try:
            yield conn
        finally:
            conn.close()

    def execute_query(
        self,
        query: str,
        params: Optional[tuple] = None,
        fetch_all: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Execute a query and return results as list of dicts.

        Args:
            query: SQL query string
            params: Optional query parameters
            fetch_all: If True, fetch all rows; if False, fetch one

        Returns:
            List of dictionaries with column names as keys
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            # Get column names
            columns = [column[0] for column in cursor.description]

            if fetch_all:
                rows = cursor.fetchall()
            else:
                row = cursor.fetchone()
                rows = [row] if row else []

            # Convert to list of dicts
            return [dict(zip(columns, row)) for row in rows]

    def execute_scalar(self, query: str, params: Optional[tuple] = None) -> Any:
        """Execute a query and return single value"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            row = cursor.fetchone()
            return row[0] if row else None


# Global instance
db = DatabaseManager()
