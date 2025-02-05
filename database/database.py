import sqlite3

from account.account import EncryptedAccount

DATABASE_PATH = "database/main.db"

class Database:
    def __init__(self):
        self.__conn, self.__cursor = self.__connect()
        self.__create_account_table()
        self.__create_company_table()
        self.__create_company_account_table()
        self.account = EncryptedAccount()

    def __connect(self):
        conn = sqlite3.connect(DATABASE_PATH, autocommit=True)
        cursor = conn.cursor()
        return conn, cursor

    # Account Table

    def __create_account_table(self):
        self.__cursor.execute("""
        CREATE TABLE IF NOT EXISTS Account (
            Username TEXT PRIMARY KEY,
            Email TEXT NOT NULL,
            Password TEXT NOT NULL,
            DateOfBirth TEXT,
            MaximumInvestment INTEGER,
            LookingToInvest INTEGER
        )
        """)

    def add_account(self, username, email, password):
        self.__cursor.execute("""
        INSERT INTO Account (Username, Email, Password) VALUES (
            :username,
            :email,
            :password
        )
        """,
        {
            "username": username,
            "email": email,
            "password": password
        })

        self.account.add_to_file(username, email, password)

    def check_account(self, email, password):
        self.__cursor.execute("""
        SELECT * FROM Account
        WHERE Email = :email AND Password = :password
        """,
        {
            "email": email,
            "password": password
        })

        account_list = self.__cursor.fetchall()
        return account_list

    def log_in(self, username, email, password):
        self.account.add_to_file(username, email, password)

    def retrieve_account_settings(self):
        self.__cursor.execute("""
        SELECT DateOfBirth, MaximumInvestment, LookingToInvest FROM Account
        WHERE Username = :username
        """,
        {
            "username": self.account.get_username()
        })
        print(self.account.get_username())
        return self.__cursor.fetchone()

    def update_account_table(self, dob, max_investment, looking_to_invest):
        self.__cursor.execute("""
        UPDATE Account
        SET DateOfBirth = :dob,
        MaximumInvestment = :max_investment,
        LookingToInvest = :looking_to_invest
        WHERE Username = :username
        """,
        {
            "dob": dob,
            "max_investment": max_investment,
            "looking_to_invest": looking_to_invest,
            "username": self.account.get_username()
        })

    # Company Table

    def __create_company_table(self):
        self.__cursor.execute("""
        CREATE TABLE IF NOT EXISTS Company (
            CompanyName TEXT PRIMARY KEY,
            LookingForInvestor INTEGER,
            MinimumAskingInvestment INTEGER,
            MinimumInvestorAge INTEGER
        )
        """)

    def __create_company_account_table(self):
        self.__cursor.execute("""
        CREATE TABLE IF NOT EXISTS CompanyAccount (
            Username,
            CompanyName,
            FOREIGN KEY (Username) REFERENCES Account(Username),
            FOREIGN KEY (CompanyName) REFERENCES Company(CompanyName),
            PRIMARY KEY (Username, CompanyName)
        )
        """)

    def register_company(self, company_name, looking_for_investor, minimum_asking_investment, minimum_investor_age):
        self.__cursor.execute("""
            INSERT INTO Company VALUES (
                :company_name,
                :looking_for_investor,
                :minimum_asking_investment,
                :minimum_investor_age
            )
        """,
        {
            "company_name": company_name,
            "looking_for_investor": looking_for_investor,
            "minimum_asking_investment": minimum_asking_investment,
            "minimum_investor_age": minimum_investor_age
        })

        self.__cursor.execute("""
            INSERT INTO CompanyAccount VALUES (
                :username,
                :company_name
            )
        """,
        {
             "username": self.account.get_username(),
             "company_name": company_name
        })

    def __del__(self):
        self.__conn.close()
