users = {
    "sysadmin02": {"role": "system_admin", "clearance": 4, "department": "Infrastructure", "active": True},
    "analyst234": {"role": "security_analyst", "clearance": 3, "department": "SOC", "active": True},
    "developer567": {"role": "developer", "clearance": 2, "department": "Development", "active": True},
    "intern890": {"role": "intern", "clearance": 1, "department": "HR", "active": True},
    "external123": {"role": "external", "clearance": 1, "department": "Vendor", "active": False}
}

resources = [
    ("prod_database", 4), ("dev_environment", 2), ("documentation", 1),
    ("source_code", 3), ("server_configs", 4), ("test_data", 2),
    ("compliance_docs", 3), ("system_logs", 4), ("project_files", 2),
    ("public_wiki", 1)
]

security_levels = ("Open", "Internal", "Restricted", "Top Secret")
blocked_users = {"external123", "old_account", "test_user"}


def run_task2():
    print(" Список ресурсів системи ")
    for res_name, res_level in resources:
        level_name = security_levels[res_level - 1]
        print(f"Ресурс: {res_name:<18} | Рівень: {level_name}")

    print("\n" + "=" * 65)
    print(" " * 15 + "ЖУРНАЛ АУДИТУ ДОСТУПУ")
    print("=" * 65)

    all_users = set(users.keys()).union(blocked_users)

    for user in sorted(all_users):
        print(f"\n Таблиця дозволів для користувача: {user} ")

        for res_name, res_level in resources:

            if user not in users:
                status = "DENY (User not found)"
            elif user in blocked_users:
                status = "DENY (User is blocked)"
            elif not users[user].get("active", False):
                status = "DENY (Account inactive)"
            elif users[user].get("clearance", 0) >= res_level:
                status = "ALLOW"
            else:
                status = "DENY (Insufficient clearance)"

            print(f"user=[{user:<12}] resource=[{res_name:<16}] -> {status}")


if __name__ == '__main__':
    run_task2()