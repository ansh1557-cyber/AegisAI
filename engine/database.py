"""
Aegis AI
Module: Database
Version: 1.1.0
"""

import sqlite3


class Database:

    def __init__(self):

        self.connection = sqlite3.connect(
            "aegis.db",
            check_same_thread=False,
        )

        self.cursor = self.connection.cursor()

        self.create_tables()

    def create_tables(self):

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS trades (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            ticket INTEGER,

            symbol TEXT,

            signal TEXT,

            volume REAL,

            entry REAL,

            stop_loss REAL,

            take_profit REAL,

            confidence INTEGER,

            status TEXT,

            profit REAL,

            open_time TEXT,

            close_time TEXT

        )
        """)

        self.connection.commit()

    def save_trade(
        self,
        ticket,
        symbol,
        signal,
        volume,
        entry,
        stop_loss,
        take_profit,
        confidence,
        status,
        open_time,
    ):

        self.cursor.execute(
            """
            INSERT INTO trades (

                ticket,
                symbol,
                signal,
                volume,
                entry,
                stop_loss,
                take_profit,
                confidence,
                status,
                profit,
                open_time,
                close_time

            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ticket,
                symbol,
                signal,
                volume,
                entry,
                stop_loss,
                take_profit,
                confidence,
                status,
                0,
                open_time,
                None,
            ),
        )

        self.connection.commit()

    def close_trade(
        self,
        ticket,
        profit,
        close_time,
    ):

        self.cursor.execute(
            """
            UPDATE trades

            SET

                profit=?,
                status=?,
                close_time=?

            WHERE ticket=?
            """,
            (
                profit,
                "CLOSED",
                close_time,
                ticket,
            ),
        )

        self.connection.commit()

    def get_trade(self, ticket):

        self.cursor.execute(
            "SELECT * FROM trades WHERE ticket=?",
            (ticket,),
        )

        return self.cursor.fetchone()

    def get_all_trades(self):

        self.cursor.execute(
            "SELECT * FROM trades ORDER BY id DESC"
        )

        return self.cursor.fetchall()