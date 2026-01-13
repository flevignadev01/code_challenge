from minivenmo import MiniVenmo, User, CreditCard, ActivityType


def test_credit_card_initialization():
    card = CreditCard("1234-5678-9012-3456", "John Doe", "12/25", "123", 1000.0)
    assert card.card_number == "1234-5678-9012-3456"
    assert card.cardholder_name == "John Doe"
    assert card.balance == 1000.0


def test_credit_card_charge_success():
    card = CreditCard("1234-5678-9012-3456", "John Doe", "12/25", "123", 1000.0)
    result = card.charge(100.0)
    assert result is True
    assert card.balance == 900.0


def test_credit_card_charge_insufficient_funds():
    card = CreditCard("1234-5678-9012-3456", "John Doe", "12/25", "123", 100.0)
    result = card.charge(200.0)
    assert result is False
    assert card.balance == 100.0


def test_credit_card_charge_invalid_amount():
    card = CreditCard("1234-5678-9012-3456", "John Doe", "12/25", "123", 1000.0)
    result = card.charge(-50.0)
    assert result is False
    result = card.charge(0.0)
    assert result is False


def test_user_initialization():
    user = User("bobby", 100.0)
    assert user.username == "bobby"
    assert user.balance == 100.0
    assert len(user.friends) == 0
    assert len(user.activity_feed) == 0


def test_user_pay_with_balance():
    bobby = User("bobby", 100.0)
    carol = User("carol", 50.0)

    result = bobby.pay(carol, 30.0, "Coffee")
    assert result is True
    assert bobby.balance == 70.0
    assert carol.balance == 80.0

    activities = bobby.retrieve_activity()
    assert len(activities) == 1
    assert activities[0].activity_type == ActivityType.PAYMENT
    assert activities[0].amount == 30.0


def test_user_pay_with_credit_card():
    card = CreditCard("1234-5678-9012-3456", "Bobby", "12/25", "123", 1000.0)
    bobby = User("bobby", 50.0, card)
    carol = User("carol", 0.0)

    result = bobby.pay(carol, 100.0, "Lunch")
    assert result is True
    assert bobby.balance == 50.0
    assert card.balance == 900.0
    assert carol.balance == 100.0


def test_user_pay_balance_partial_credit_card():
    card = CreditCard("1234-5678-9012-3456", "Bobby", "12/25", "123", 1000.0)
    bobby = User("bobby", 50.0, card)
    carol = User("carol", 0.0)

    result = bobby.pay(carol, 100.0, "Dinner")
    assert result is True
    assert bobby.balance == 50.0
    assert card.balance == 900.0
    assert carol.balance == 100.0


def test_user_pay_insufficient_funds():
    bobby = User("bobby", 50.0)
    carol = User("carol", 0.0)

    result = bobby.pay(carol, 100.0, "Lunch")
    assert result is False
    assert bobby.balance == 50.0
    assert carol.balance == 0.0


def test_user_pay_to_self():
    bobby = User("bobby", 100.0)
    result = bobby.pay(bobby, 50.0, "Test")
    assert result is False
    assert bobby.balance == 100.0


def test_user_pay_invalid_amount():
    bobby = User("bobby", 100.0)
    carol = User("carol", 0.0)

    result = bobby.pay(carol, -10.0, "Test")
    assert result is False
    result = bobby.pay(carol, 0.0, "Test")
    assert result is False


def test_user_add_friend():
    bobby = User("bobby", 100.0)
    carol = User("carol", 50.0)

    result = bobby.add_friend(carol)
    assert result is True
    assert carol in bobby.friends
    assert len(bobby.friends) == 1

    activities = bobby.retrieve_activity()
    assert len(activities) == 1
    assert activities[0].activity_type == ActivityType.FRIEND_ADDED


def test_user_add_friend_duplicate():
    bobby = User("bobby", 100.0)
    carol = User("carol", 50.0)

    result1 = bobby.add_friend(carol)
    assert result1 is True

    result2 = bobby.add_friend(carol)
    assert result2 is False
    assert len(bobby.friends) == 1


def test_user_add_friend_to_self():
    bobby = User("bobby", 100.0)
    result = bobby.add_friend(bobby)
    assert result is False
    assert len(bobby.friends) == 0


def test_user_retrieve_activity():
    bobby = User("bobby", 100.0)
    carol = User("carol", 50.0)

    bobby.add_friend(carol)
    bobby.pay(carol, 30.0, "Coffee")

    activities = bobby.retrieve_activity()
    assert len(activities) == 2
    assert activities[0].activity_type == ActivityType.PAYMENT
    assert activities[1].activity_type == ActivityType.FRIEND_ADDED


def test_create_user():
    app = MiniVenmo()
    user = app.create_user("bobby", 100.0)

    assert user is not None
    assert user.username == "bobby"
    assert user.balance == 100.0
    assert "bobby" in app.users


def test_create_user_duplicate():
    app = MiniVenmo()
    user1 = app.create_user("bobby", 100.0)
    user2 = app.create_user("bobby", 50.0)

    assert user1 is not None
    assert user2 is None


def test_create_user_with_credit_card():
    app = MiniVenmo()
    card = CreditCard("1234-5678-9012-3456", "Bobby", "12/25", "123", 1000.0)
    user = app.create_user("bobby", 100.0, card)

    assert user is not None
    assert user.credit_card == card


def test_render_feed_simple():
    app = MiniVenmo()
    bobby = app.create_user("bobby", 100.0)
    carol = app.create_user("carol", 50.0)

    bobby.pay(carol, 5.0, "Coffee")
    carol.pay(bobby, 15.0, "Lunch")

    feed = app.render_feed()
    assert "bobby paid carol $5.00 for Coffee" in feed
    assert "carol paid bobby $15.00 for Lunch" in feed


def test_render_feed_with_friends():
    app = MiniVenmo()
    bobby = app.create_user("bobby", 100.0)
    carol = app.create_user("carol", 50.0)
    alice = app.create_user("alice", 75.0)

    bobby.add_friend(carol)
    bobby.pay(carol, 10.0, "Coffee")
    carol.add_friend(alice)

    feed = app.render_feed()
    assert "bobby added carol as a friend" in feed
    assert "bobby paid carol $10.00 for Coffee" in feed
    assert "carol added alice as a friend" in feed


def test_render_feed_ordering():
    app = MiniVenmo()
    bobby = app.create_user("bobby", 100.0)
    carol = app.create_user("carol", 50.0)

    bobby.pay(carol, 5.0, "Coffee")
    carol.pay(bobby, 15.0, "Lunch")

    feed = app.render_feed()
    feed_lines = feed.split("\n")

    assert "carol paid bobby $15.00 for Lunch" in feed_lines[0]
    assert "bobby paid carol $5.00 for Coffee" in feed_lines[1]


def test_complete_workflow():
    app = MiniVenmo()

    bobby = app.create_user("bobby", 100.0)
    carol = app.create_user("carol", 50.0)
    alice = app.create_user("alice", 75.0)

    assert bobby is not None
    assert carol is not None
    assert alice is not None

    bobby.add_friend(carol)
    carol.add_friend(alice)

    bobby.pay(carol, 5.0, "Coffee")
    carol.pay(bobby, 15.0, "Lunch")
    alice.pay(carol, 10.0, "Dinner")

    assert bobby.balance == 110.0
    assert carol.balance == 50.0
    assert alice.balance == 65.0

    feed = app.render_feed()
    assert "bobby paid carol $5.00 for Coffee" in feed
    assert "carol paid bobby $15.00 for Lunch" in feed
    assert "alice paid carol $10.00 for Dinner" in feed
    assert "bobby added carol as a friend" in feed
    assert "carol added alice as a friend" in feed


def test_payment_with_credit_card_workflow():
    app = MiniVenmo()

    card = CreditCard("1234-5678-9012-3456", "Bobby", "12/25", "123", 500.0)
    bobby = app.create_user("bobby", 50.0, card)
    carol = app.create_user("carol", 0.0)

    result = bobby.pay(carol, 100.0, "Groceries")
    assert result is True
    assert bobby.balance == 50.0
    assert card.balance == 400.0
    assert carol.balance == 100.0

    feed = app.render_feed()
    assert "bobby paid carol $100.00 for Groceries" in feed
