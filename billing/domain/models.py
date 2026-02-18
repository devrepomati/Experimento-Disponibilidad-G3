class ReadyForPaymentEvent:
    def __init__(self, reserve_id, username, final_price, status):
        self.event_type = "READY_FOR_PAYMENT"
        self.reserve_id = reserve_id
        self.username = username
        self.final_price = final_price
        self.status = status

    def as_message(self):
        return {
            "event_type": self.event_type,
            "reserve_id": self.reserve_id,
            "username": self.username,
            "final_price": self.final_price,
            "status": self.status
        }