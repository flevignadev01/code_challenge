from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum


class ActivityType(Enum):
    PAYMENT = "payment"
    FRIEND_ADDED = "friend_added"


class Activity:

    def __init__(
        self,
        activity_type: ActivityType,
        timestamp: datetime,
        actor: "User",
        target: Optional["User"] = None,
        amount: Optional[float] = None,
        note: Optional[str] = None,
    ):

        self.activity_type = activity_type
        self.timestamp = timestamp
        self.actor = actor
        self.target = target
        self.amount = amount
        self.note = note

    def __repr__(self):
        if self.activity_type == ActivityType.PAYMENT:
            return f"{self.actor.username} paid {self.target.username} ${self.amount:.2f} for {self.note}"
        elif self.activity_type == ActivityType.FRIEND_ADDED:
            return f"{self.actor.username} added {self.target.username} as a friend"

        return str(self)


class CreditCard:
    def __init__(
        self,
        card_number: str,
        cardholder_name: str,
        expiry_date: str,
        cvv: str,
        balance: float = 0.0,
    ):

        self.card_number = card_number
        self.cardholder_name = cardholder_name
        self.expiry_date = expiry_date
        self.cvv = cvv
        self.balance = balance

    def charge(self, amount: float):
        if amount <= 0:
            return False

        if amount > self.balance:
            return False
        self.balance -= amount

        return True

    def get_balance(self):
        return self.balance


class User:
    def __init__(
        self,
        username: str,
        balance: float = 0.0,
        credit_card: Optional[CreditCard] = None,
    ):
        self.username = username
        self.balance = balance
        self.credit_card = credit_card
        self.friends: List["User"] = []
        self.activity_feed: List[Activity] = []

    def get_username(self):
        return self.username

    def get_balance(self):
        return self.balance

    def add_friend(self, friend: "User"):
        if friend is None:
            return False

        if friend == self:
            return False

        if friend in self.friends:
            return False

        self.friends.append(friend)

        activity = Activity(
            activity_type=ActivityType.FRIEND_ADDED,
            timestamp=datetime.now(),
            actor=self,
            target=friend,
        )

        self.activity_feed.append(activity)
        friend.activity_feed.append(activity)

        return True

    def pay(self, recipient: "User", amount: float, note: str = ""):
        if recipient is None:
            return False

        if recipient == self:
            return False

        if amount <= 0:
            return False

        if self.balance >= amount:
            self.balance -= amount
            recipient.balance += amount
            payment_source = "balance"

        elif self.credit_card is not None and self.credit_card.get_balance() >= amount:
            if not self.credit_card.charge(amount):
                return False
            recipient.balance += amount
            payment_source = "credit_card"
        else:
            return False

        activity = Activity(
            activity_type=ActivityType.PAYMENT,
            timestamp=datetime.now(),
            actor=self,
            target=recipient,
            amount=amount,
            note=note,
        )

        self.activity_feed.append(activity)
        recipient.activity_feed.append(activity)
        return True

    def retrieve_activity(self):
        return sorted(self.activity_feed, key=lambda x: x.timestamp, reverse=True)


class MiniVenmo:

    def __init__(self):
        self.users: Dict[str, User] = {}

    def create_user(
        self,
        username: str,
        balance: float = 0.0,
        credit_card: Optional[CreditCard] = None,
    ):
        if username in self.users:  # User already exists
            return None

        user = User(username, balance, credit_card)
        self.users[username] = user
        return user

    def get_user(self, username: str):
        return self.users.get(username)

    def render_feed(self):
        all_activities: List[Activity] = []
        seen_activities = set()
        for user in self.users.values():
            for activity in user.activity_feed:
                activity_id = id(activity)
                if activity_id not in seen_activities:
                    seen_activities.add(activity_id)
                    all_activities.append(activity)

        all_activities.sort(key=lambda x: x.timestamp, reverse=True)

        return "\n".join(repr(activity) for activity in all_activities)
