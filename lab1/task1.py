import random

try:
    from shared.student import STUDENT_NAME, VARIANT
except ImportError:
    STUDENT_NAME = "Бігей Євген Андрійович"
    VARIANT = "2"

passwords = [
    "Hello123!", "simple", "CompL3x@Pass", "password",
    "Str0ng#2023", "weak", "MySecur3!", "12345",
    "Advanced@1", "basic"
]

criteria = {
    "min_length": 10,
    "require_digits": True,
    "require_upper": True,
    "require_special": True
}

forbidden_passwords = {"password", "simple", "weak", "basic", "12345", "hello"}

duplicates = random.sample(passwords, 3)
passwords.extend(duplicates)


def criteria_counter(text) -> int:
    crit1 = any(char.isdigit() for char in text)
    crit2 = any(char.isupper() for char in text)
    crit3 = any(char.islower() for char in text)
    crit4 = any(not char.isalnum() for char in text)
    return sum([crit1, crit2, crit3, crit4])


def run_task1():
    checked_passwords = []

    for pw in passwords:
        if pw in forbidden_passwords or pw.lower() in forbidden_passwords or len(pw) < criteria["min_length"]:
            status = "Forbidden"
        else:
            score = criteria_counter(pw)

            if score == 4:
                is_unique = passwords.count(pw) == 1
                if len(pw) >= criteria["min_length"] + 4 and is_unique:
                    status = "MEGA STRONG 0_0"
                else:
                    status = "Strong"
            elif score > 1:
                status = "Medium"
            else:
                status = "Weak"

        checked_passwords.append((pw, status))

    print(f"Студент: {STUDENT_NAME} | Варіант: {VARIANT}")
    print("-" * 45)
    print(f"{'Пароль':<20} | {'Надійність'}")
    print("-" * 45)

    for pw, status in checked_passwords:
        print(f"{pw:<20} | {status}")


if __name__ == '__main__':
    run_task1()