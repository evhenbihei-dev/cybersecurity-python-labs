import argparse
import sys
from .task1 import User, UserAccount, AuditLog
from .task2 import main as task2_main

def run_demo():
    print("=== Демонстрація Завдання 1 ===")
    audit_log = AuditLog()
    
    user1 = User("yevhen_dev", "yevhen.dev@example.com")
    user1.set_password("SecurePass123!")
    account1 = UserAccount(user1, audit_log)
    
    print(f"Створено користувача: {account1['user']}")
    
    print("\nСпроба входу з правильним паролем...")
    if account1.login("SecurePass123!", "192.168.1.10"):
        print("Вхід виконано успішно!")
    
    print(f"Аутентифіковано: {account1.is_authenticated()}")
    
    account1.logout()
    print("Вихід із системи.")
    
    print("\n=== Журнал аудиту ===")
    audit_log.show_all()

def main():
    parser = argparse.ArgumentParser(description="Головна точка входу для Лабораторної 2")
    subparsers = parser.add_subparsers(dest="command", help="Доступні команди")
    
    subparsers.add_parser("demo", help="Запуск демонстрації Завдання 1")
    
    subparsers.add_parser("analyze", help="Запуск утиліти FIM (Завдання 2)")
    
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
        
    args, unknown = parser.parse_known_args()
    
    if args.command == "demo":
        run_demo()
    elif args.command == "analyze":
        sys.argv = [sys.argv[0]] + unknown
        task2_main()

if __name__ == "__main__":
    main()