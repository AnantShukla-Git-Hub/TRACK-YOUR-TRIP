"""
Pure calculation logic for the trip expense splitter.
No DB or FastAPI dependencies here — this module is independently testable.
All money amounts are integers in paise (never floats).
"""

import heapq


class ShareValidationError(Exception):
    pass


class PayerValidationError(Exception):
    pass


def compute_expense_shares(total_amount_paise, participants):
    """
    participants: list of dicts, each {"member_id": int, "share_amount_paise": int | None}
    Returns: dict[member_id -> share_paise], guaranteed to sum exactly to total_amount_paise.

    Rule: members with an explicit share_amount_paise use that value as-is.
    Members with share_amount_paise=None split whatever amount remains, equally.
    Any leftover paise from integer division of the equal split is distributed
    one paisa at a time to the lowest-numbered member IDs, so the total always
    matches exactly (no floating point, no missing paise).
    """
    custom_shares = {
        p["member_id"]: p["share_amount_paise"]
        for p in participants
        if p["share_amount_paise"] is not None
    }
    equal_split_ids = sorted(
        p["member_id"] for p in participants if p["share_amount_paise"] is None
    )

    custom_total = sum(custom_shares.values())
    if custom_total > total_amount_paise:
        raise ShareValidationError(
            f"Custom shares add up to {custom_total} paise, which is more than "
            f"the expense total of {total_amount_paise} paise."
        )

    remaining = total_amount_paise - custom_total
    shares = dict(custom_shares)

    if equal_split_ids:
        count = len(equal_split_ids)
        base_share = remaining // count
        leftover_paise = remaining % count
        for index, member_id in enumerate(equal_split_ids):
            shares[member_id] = base_share + (1 if index < leftover_paise else 0)
    elif remaining != 0:
        raise ShareValidationError(
            f"All participants have custom shares but they add up to "
            f"{custom_total} paise, not the expense total of {total_amount_paise} paise."
        )

    return shares


def validate_payers(total_amount_paise, payers):
    """
    payers: list of dicts, each {"member_id": int, "amount_paid_paise": int}
    Raises PayerValidationError if the amounts don't sum exactly to the total.
    """
    paid_total = sum(p["amount_paid_paise"] for p in payers)
    if paid_total != total_amount_paise:
        raise PayerValidationError(
            f"Payers' amounts add up to {paid_total} paise, but the expense "
            f"total is {total_amount_paise} paise."
        )


def compute_net_balances(expenses):
    """
    expenses: list of dicts, each:
      {
        "total_amount_paise": int,
        "payers": [{"member_id": int, "amount_paid_paise": int}, ...],
        "participants": [{"member_id": int, "share_amount_paise": int | None}, ...],
      }
    Returns: dict[member_id -> net_balance_paise]
      positive = this member is owed money
      negative = this member owes money
    """
    net_balances = {}

    for expense in expenses:
        total = expense["total_amount_paise"]
        validate_payers(total, expense["payers"])
        shares = compute_expense_shares(total, expense["participants"])

        for payer in expense["payers"]:
            member_id = payer["member_id"]
            net_balances[member_id] = (
                net_balances.get(member_id, 0) + payer["amount_paid_paise"]
            )

        for member_id, share in shares.items():
            net_balances[member_id] = net_balances.get(member_id, 0) - share

    return net_balances


def minimize_transactions(net_balances):
    """
    net_balances: dict[member_id -> net_balance_paise]
    Returns: list of (debtor_member_id, creditor_member_id, amount_paise)
             representing the minimum number of transactions to settle everyone.

    Greedy algorithm: repeatedly match the biggest creditor with the biggest
    debtor, settle as much as possible between them, repeat. Implemented with
    two max-heaps for O(n log n) behaviour.
    """
    creditors = []  # max-heap via negation: (-amount_owed_to_them, member_id)
    debtors = []    # max-heap via negation: (-amount_they_owe, member_id)

    for member_id, balance in net_balances.items():
        if balance > 0:
            heapq.heappush(creditors, (-balance, member_id))
        elif balance < 0:
            heapq.heappush(debtors, (balance, member_id))  # already negative

    transactions = []

    while creditors and debtors:
        neg_credit, creditor_id = heapq.heappop(creditors)
        credit = -neg_credit

        debt, debtor_id = heapq.heappop(debtors)
        debt_amount = -debt

        settle_amount = min(credit, debt_amount)
        transactions.append((debtor_id, creditor_id, settle_amount))

        credit -= settle_amount
        debt_amount -= settle_amount

        if credit > 0:
            heapq.heappush(creditors, (-credit, creditor_id))
        if debt_amount > 0:
            heapq.heappush(debtors, (-debt_amount, debtor_id))

    return transactions