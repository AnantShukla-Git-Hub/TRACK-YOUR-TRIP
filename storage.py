import json
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Optional

STORAGE_FILE = Path("/tmp/trip_data.json")
_lock = Lock()

_data = {
    "trips": {},
    "members": {},
    "expenses": {},
    "expense_payers": {},
    "expense_participants": {},
    "next_ids": {
        "trip": 1,
        "member": 1,
        "expense": 1,
        "expense_payer": 1,
        "expense_participant": 1,
    }
}


def _load_from_file():
    global _data
    with _lock:
        if STORAGE_FILE.exists():
            try:
                with open(STORAGE_FILE, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    _data["trips"] = {int(k): v for k, v in loaded.get("trips", {}).items()}
                    _data["members"] = {int(k): v for k, v in loaded.get("members", {}).items()}
                    _data["expenses"] = {int(k): v for k, v in loaded.get("expenses", {}).items()}
                    _data["expense_payers"] = {int(k): v for k, v in loaded.get("expense_payers", {}).items()}
                    _data["expense_participants"] = {int(k): v for k, v in loaded.get("expense_participants", {}).items()}
                    _data["next_ids"] = loaded.get("next_ids", _data["next_ids"])
            except (json.JSONDecodeError, IOError):
                pass


def _save_to_file():
    with _lock:
        try:
            STORAGE_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(STORAGE_FILE, "w", encoding="utf-8") as f:
                json.dump(_data, f, indent=2, default=str)
        except IOError:
            pass


def _get_next_id(entity_type: str) -> int:
    next_id = _data["next_ids"][entity_type]
    _data["next_ids"][entity_type] += 1
    return next_id


_load_from_file()


def create_trip(name: str) -> dict:
    trip_id = _get_next_id("trip")
    trip = {
        "id": trip_id,
        "name": name,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    _data["trips"][trip_id] = trip
    _save_to_file()
    return trip


def get_trip(trip_id: int) -> Optional[dict]:
    return _data["trips"].get(trip_id)


def create_member(trip_id: int, name: str) -> dict:
    member_id = _get_next_id("member")
    member = {
        "id": member_id,
        "trip_id": trip_id,
        "name": name,
    }
    _data["members"][member_id] = member
    _save_to_file()
    return member


def get_members_by_trip(trip_id: int) -> list[dict]:
    return [m for m in _data["members"].values() if m["trip_id"] == trip_id]


def get_member(member_id: int) -> Optional[dict]:
    return _data["members"].get(member_id)


def delete_member(member_id: int) -> bool:
    if member_id in _data["members"]:
        del _data["members"][member_id]
        _save_to_file()
        return True
    return False


def is_member_used_in_expenses(member_id: int) -> bool:
    for payer in _data["expense_payers"].values():
        if payer["member_id"] == member_id:
            return True
    for participant in _data["expense_participants"].values():
        if participant["member_id"] == member_id:
            return True
    return False


def create_expense(trip_id: int, description: str, total_amount_paise: int,
                   payers: list[dict], participants: list[dict]) -> dict:
    expense_id = _get_next_id("expense")
    expense = {
        "id": expense_id,
        "trip_id": trip_id,
        "description": description,
        "total_amount_paise": total_amount_paise,
    }
    _data["expenses"][expense_id] = expense
    
    payer_records = []
    for payer in payers:
        payer_id = _get_next_id("expense_payer")
        payer_record = {
            "id": payer_id,
            "expense_id": expense_id,
            "member_id": payer["member_id"],
            "amount_paid_paise": payer["amount_paid_paise"],
        }
        _data["expense_payers"][payer_id] = payer_record
        payer_records.append(payer_record)
    
    participant_records = []
    for participant in participants:
        participant_id = _get_next_id("expense_participant")
        participant_record = {
            "id": participant_id,
            "expense_id": expense_id,
            "member_id": participant["member_id"],
            "share_amount_paise": participant.get("share_amount_paise"),
        }
        _data["expense_participants"][participant_id] = participant_record
        participant_records.append(participant_record)
    
    _save_to_file()
    
    return {
        **expense,
        "payers": payer_records,
        "participants": participant_records,
    }


def get_expenses_by_trip(trip_id: int) -> list[dict]:
    expenses = [e for e in _data["expenses"].values() if e["trip_id"] == trip_id]
    
    result = []
    for expense in expenses:
        payers = [p for p in _data["expense_payers"].values() if p["expense_id"] == expense["id"]]
        participants = [p for p in _data["expense_participants"].values() if p["expense_id"] == expense["id"]]
        result.append({
            **expense,
            "payers": payers,
            "participants": participants,
        })
    
    return result


def get_expense(expense_id: int) -> Optional[dict]:
    expense = _data["expenses"].get(expense_id)
    if not expense:
        return None
    
    payers = [p for p in _data["expense_payers"].values() if p["expense_id"] == expense_id]
    participants = [p for p in _data["expense_participants"].values() if p["expense_id"] == expense_id]
    
    return {
        **expense,
        "payers": payers,
        "participants": participants,
    }


def clear_all_data():
    global _data
    _data = {
        "trips": {},
        "members": {},
        "expenses": {},
        "expense_payers": {},
        "expense_participants": {},
        "next_ids": {
            "trip": 1,
            "member": 1,
            "expense": 1,
            "expense_payer": 1,
            "expense_participant": 1,
        }
    }
    _save_to_file()


def get_all_data() -> dict:
    return _data.copy()
