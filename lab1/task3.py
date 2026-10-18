import hashlib
import os
import csv
import json
from datetime import datetime
from functools import wraps


class ValidationError(Exception):
    pass


MIN_PASSWORD_LENGTH = 10

DB_DIR = os.path.join("labs", "lab01", "data")
CSV_FILE = os.path.join(DB_DIR, "users.csv")
LOG_FILE = os.path.join(DB_DIR, "log.json")

try:
    from shared.student import STUDENT_NAME, VARIANT
except ImportError:
    STUDENT_NAME = "Бігей Євген Андрійович"
    VARIANT = 2

PERSONAL_SALT = str(VARIANT).zfill(5)


def generate_hash(password: str, salt: str = "00000") -> str:
    if not password or not salt:
        raise ValueError("Пароль або сіль не можуть бути порожніми (None або '').")
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValidationError(f"Пароль коротший за мінімальну довжину ({MIN_PASSWORD_LENGTH} символів).")

    payload = (password + salt).encode('utf-8')
    return hashlib.sha3_224(payload).hexdigest()


users_to_register = (
    ("admin", "SuperSecure1!"),
    ("yevhen", "MyP@ssw0rd34"),
    ("danylo", "P@ssw0rdDanylo"),
    ("dmytro", "VakhDmytro123!"),
    ("moderator", "ModPassw0rd#"),
    ("guest", "Guest2026Pass"),
    ("auditor", "AuditPass!22"),
    ("test_user", "Test1ng!Pass"),
    ("short", "1234567"),
    ("empty", "")
)


def create_user(username, password):
    hashed_pass = generate_hash(password, PERSONAL_SALT)
    return (username, hashed_pass)


def create_users(users_list):
    os.makedirs(DB_DIR, exist_ok=True)
    valid_users = []

    for u, p in users_list:
        try:
            valid_users.append(create_user(u, p))
        except (ValueError, ValidationError) as e:
            print(f"[Пропущено реєстрацію] {u}: {e}")

    with open(CSV_FILE, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(valid_users)


def log_event(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        status = "failure"
        result = False
        try:
            result = func(*args, **kwargs)
            status = "success" if result else "failure"
        except Exception:
            status = "failure"
            raise
        finally:
            username = kwargs.get('username') or (args[0] if args else "unknown")

            log_entry = {
                "event": "login",
                "user": username,
                "result": status,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "args": [str(a) for a in args],
                "kwargs": {k: str(v) for k, v in kwargs.items()}
            }

            logs = []
            if os.path.exists(LOG_FILE):
                try:
                    with open(LOG_FILE, 'r', encoding='utf-8') as f:
                        logs = json.load(f)
                except json.JSONDecodeError:
                    pass

            logs.append(log_entry)

            try:
                with open(LOG_FILE, 'w', encoding='utf-8') as f:
                    json.dump(logs, f, indent=2, ensure_ascii=False)
            except IOError as e:
                print(f"Помилка запису логів: {e}")

        return result

    return wrapper


users_db = []


@log_event
def login(username: str, password: str) -> bool:
    if not username or not password:
        raise ValueError("Логін або пароль при вході не можуть бути порожніми.")

    hashed_attempt = generate_hash(password, PERSONAL_SALT)

    for db_user, db_hash in users_db:
        if db_user == username and db_hash == hashed_attempt:
            return True
    return False


def main():
    global users_db
    print(f" Модуль Безпеки | Студент: {STUDENT_NAME} | Варіант: {VARIANT} ")
    print(f" Налаштування: SHA3-224 | Мін. довжина пароля: {MIN_PASSWORD_LENGTH} \n")

    try:
        print("[1] Генерація бази даних...")
        create_users(users_to_register)

        if not os.path.exists(CSV_FILE):
            raise FileNotFoundError(f"Файл бази даних {CSV_FILE} не знайдено.")

        with open(CSV_FILE, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f)
            users_db = [tuple(row) for row in reader if row]

        print("\n[2] Завантажена CSV-база користувачів:")
        print(f"{'Логін':<15} | {'Хеш пароля (SHA3-224)'}")
        print("-" * 80)
        for u, h in users_db:
            print(f"{u:<15} | {h}")

        print("\n[3] Тестування автентифікації та логування:")
        test_logins = [
            ("yevhen", "MyP@ssw0rd34"),
            ("admin", "WrongPass123"),
            ("unknown", "Pass123!45"),
            ("guest", ""),
            ("admin", "short")
        ]

        for u, p in test_logins:
            try:
                print(f"Спроба входу [{u}]: ", end="")
                if login(u, p):
                    print("УСПІШНО (доступ надано)")
                else:
                    print("ВІДМОВЛЕНО (невірний логін або пароль)")
            except (ValueError, ValidationError) as ve:
                print(f"ПОМИЛКА ВАЛІДАЦІЇ -> {ve}")

        print(f"\n[4] Усі спроби входу успішно записані до: {LOG_FILE}")

    except FileNotFoundError as e:
        print(f"[Критична помилка]: Файл не знайдено - {e}")
    except PermissionError as e:
        print(f"[Критична помилка]: Немає прав доступу до файлу - {e}")
    except IOError as e:
        print(f"[Критична помилка]: Помилка вводу/виводу - {e}")
    except Exception as e:
        print(f"[Невідома помилка]: {e}")


if __name__ == '__main__':
    main()