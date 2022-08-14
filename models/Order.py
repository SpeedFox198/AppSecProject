from dataclasses import dataclass
import db_fetch as dbf


@dataclass
class Order:
    """ Defines a Order class """
    order_id: int
    user_id: str
    order_date: str
    shipping_option: str
    order_pending: str

    def get_customer_name(self):
        return dbf.retrieve_username_by_user_id(self.user_id)
