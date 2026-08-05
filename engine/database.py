"""
Aegis AI
Module: Database Manager
Version: 0.3.0
"""

import sqlite3
from datetime import datetime
DATABASE_NAME = "aegis.db"


class Database:

    def __init__(self):

        self.connection = sqlite3.connect(
            DATABASE_NAME,
            check_same_thread=False
        )

        self.cursor = self.connection.cursor()

        self.create_table()


    def create_table(self):

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS trades
            (

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

                profit REAL DEFAULT 0,

                open_time TEXT,

                close_time TEXT

            )
            """
        )

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
        open_time
    ):

        self.cursor.execute(
            """
            INSERT INTO trades
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
                open_time
            )

            VALUES (?,?,?,?,?,?,?,?,?,?)

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
                open_time
            )
        )


        self.connection.commit()



    # ==========================
    # GET ALL TRADES
    # ==========================

    def get_trades(self):

        self.cursor.execute(
            """
            SELECT *
            FROM trades
            ORDER BY id DESC
            """
        )

        return self.cursor.fetchall()



    # ==========================
    # GET SINGLE TRADE
    # ==========================

    def get_trade(self, ticket):

        self.cursor.execute(
            """
            SELECT *
            FROM trades
            WHERE ticket=?
            """,

            (
                ticket,
            )
        )

        return self.cursor.fetchone()



    # ==========================
    # UPDATE TRADE
    # ==========================

    def update_trade(
        self,
        ticket,
        status,
        profit,
        close_time=None
    ):

        if close_time is None:

            close_time = str(datetime.now())


        self.cursor.execute(
            """
            UPDATE trades

            SET

            status=?,
            profit=?,
            close_time=?

            WHERE ticket=?

            """,

            (
                status,
                profit,
                close_time,
                ticket
            )
        )


        self.connection.commit()



    # ==========================
    # COUNT OPEN TRADES
    # ==========================

    def count_open_trades(self):

        self.cursor.execute(
            """
            SELECT COUNT(*)
            FROM trades
            WHERE status='OPEN'
            """
        )

        result = self.cursor.fetchone()

        return result[0]

    # ==========================
    # CLOSE TRADE
    # ==========================

    def close_trade(
        self,
        ticket,
        profit,
        close_time=None
    ):

        self.update_trade(
            ticket=ticket,
            status="CLOSED",
            profit=profit,
           close_time=close_time,
        )


    # ==========================
    # CLOSE DATABASE
    # ==========================

    def close(self):

        self.connection.close()