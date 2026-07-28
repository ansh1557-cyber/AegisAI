"""
Aegis AI
Module: Session Filter
Version: 1.0.0
"""

from datetime import datetime


class SessionFilter:

    def allowed(self):

        hour = datetime.utcnow().hour

        # London: 07:00–16:00 UTC
        london = 7 <= hour < 16

        # New York: 12:00–21:00 UTC
        new_york = 12 <= hour < 21

        return london or new_york

    def current_session(self):

        hour = datetime.utcnow().hour

        if 7 <= hour < 12:
            return "London"

        if 12 <= hour < 16:
            return "London / New York Overlap"

        if 16 <= hour < 21:
            return "New York"

        return "Off Session"