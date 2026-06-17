"""
Payment cart modifiers.
"""


class PayInAdvanceModifier:
    identifier = 'pay-in-advance'
    
    def get_choice(self):
        return (self.identifier, 'Pay in Advance')
