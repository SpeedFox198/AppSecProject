from dataclasses import dataclass

@dataclass
class Order:
    """ Defines a Order class """
    order_id: int
    user_id: int
    shipping_option: str
    order_pending: str