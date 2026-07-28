"""
Aegis AI
Module: News Filter
Version: 1.0.0
"""

from datetime import datetime


class NewsFilter:

    def allowed(self):

        """
        Temporary version.

        Later this will check a live economic calendar.

        For now it always allows trading.
        """

        return True

    def reason(self):

        return "No high-impact news."

    def next_event(self):

        return None