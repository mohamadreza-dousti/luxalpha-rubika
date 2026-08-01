import datetime
import mysql.connector
from mysql.connector import pooling
from datetime import timedelta
from pathlib import Path
import os
from dotenv import load_dotenv

base_dir = Path(__file__).resolve().parent.parent
env_path = base_dir / ".env"
load_dotenv(dotenv_path=env_path)

load_dotenv()
host = os.getenv("HOST")
user = os.getenv("USERR")
passw = os.getenv("PASS")
db = os.getenv("DB")

################################################### MEMBERS TABLE ################################################################

##################################################POOL CLASS##################################################
class DBPool:
    _instance = None

    def __init__(self):
        self.is_connected = False
        self.db_config = {
            "host": host,
            "user": user,
            "password": passw,
            "database": db,
            "port": 3306
        }
        try:
            print("connecting")
            self.pool = pooling.MySQLConnectionPool(
                pool_name="luxalpha_pool",
                pool_size=16, 
                **self.db_config
            )
            print("connected")
            self.is_connected = True
        except mysql.connector.Error as err:
            print(f"not connected:{err}")
        
    def get_is_connected(self):
        return self.is_connected

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = DBPool()
        return cls._instance

    def get_connection(self):
        return self.pool.get_connection()

    def check_connection(self):
        if self.pool is None:
            return False

        try:
            with self.get_connection() as con:
                con.ping(reconnect=True, attempts=2, delay=1)
                return True
        except Exception as e:
            print(f"Connection check failed: {e}")
            return False

################################################### ADMIN TABLE ########################################################
class general:
    def __init__(self, db_pool):
        self.db_pool = db_pool
    def create_table_update(self):
        query = """
        CREATE TABLE IF NOT EXISTS updates (
            offsset VARCHAR(255)
        )
        """
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query)
                    con.commit()
        except Exception as e:
            print(f"Error in exist_user: {e},,,,,,,,,,table")
    
    def make_offset(self):
        queryd = "DELETE FROM updates"
        query = "INSERT INTO updates (offsset) VALUES (%s)"
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(queryd)
                    cursor.execute(query, ('6a1dc4fb53aceb20000d7dac',))
                    con.commit()
        except Exception as e:
            print(f"Error in exist_user: {e},,,,,,,,,make")

    
    def get_offset(self):
        query = "SELECT offsset FROM updates WHERE 1"
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query)
                    res = cursor.fetchone()
                    return res[0]
        except Exception as e:
            print(f"Error in exist_user: {e},,,,,,,,,,,,,,,get")

    def set_offset(self, of):
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute("UPDATE updates SET offsset = %s", (of,))
                    con.commit()
        except Exception as e:
            print(f"Error in exist_user: {e},,,,,,,,,,set")

    def create_table_admin(self):
        query = """
        CREATE TABLE IF NOT EXISTS admins (
            id VARCHAR(255)
        )
        """
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query)
                    con.commit()
        except:
            pass

    def register_admin(self, chat_id):
        query = "INSERT INTO admins (id) VALUES (%s)"
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query, (chat_id,))
                    con.commit()
        except:
            pass

    def delete_admin(self, chat_id):
        query = """DELETE FROM admins WHERE id = %s"""
        params = (str(chat_id),)
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query, params)
                    con.commit()
        except:
            pass

    def get_admins(self):
        query = """SELECT id FROM admins"""
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query)
                    res = cursor.fetchall()
                    return res
        except:
            pass
###########################################################USER CLASS#########################################################
class userDB:
    def __init__(self, db_pool):
        self.db_pool = db_pool

    def create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS users (
                name VARCHAR(50),
                family_name VARCHAR(50),
                phone_number VARCHAR(12),
                code VARCHAR(7),
                tag VARCHAR(10),
                new_member BOOLEAN DEFAULT 1,
                invited_with VARCHAR(15),
                invited_persons INT DEFAULT 0,
                chat_id VARCHAR (255) PRIMARY KEY,
                user_id VARCHAR (255) DEFAULT NULL,
                INDEX (chat_id),
                INDEX (user_id)
        ) ENGINE=InnoDB;
        """ 
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query)
                    con.commit()
        except:
            print("error in create table")

################################################################## EXPORT ##############################################################

    def export_users(self):
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute("""
                        SELECT name, family_name, phone_number
                        FROM users
                    """)
                    users = cursor.fetchall()
        except:
            print("error in export users")
        return users
    
    def export_new_users(self):
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute("""
                        SELECT name, family_name, phone_number
                        FROM users WHERE new_member = 1
                    """)
                    users = cursor.fetchall()
        except:
            print("error in export new users")
        return users
    
    def set_new_member(self):
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(f"UPDATE users SET new_member = {0}")
                    con.commit()
        except:
            print("f")
        
################################################################### USER INFO ############################################################

    def check_user(self, id):
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute("SELECT 1 FROM users WHERE chat_id = %s LIMIT 1", (str(id),))
                    res = cursor.fetchone() is not None
                    return res
        except Exception as e:
            print("ERROR IN CHECK USER", e)
            
    def get_invited(self, id):
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute("SELECT invited_with FROM users WHERE chat_id = %s", (str(id),))
                    res = cursor.fetchone()
                    cursor.execute("UPDATE users SET invited_with = 'None' WHERE chat_id = %s", (str(id),))
                    con.commit()
                    return res
        except:
            return []
    
    def exist_code(self, code):
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute("SELECT 1 FROM users WHERE code = %s LIMIT 1", (code,))
                    res = cursor.fetchone() is not None
                    return res
        except:
            pass
    
    def add_person(self, code):
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute("UPDATE users SET invited_persons = invited_persons+1 WHERE code = %s", (code,))
                    con.commit()
        except:
            pass

    def register_user(self, name, family_name, phone_number, code, chat_id, tag, invited_with, chat):
        query = """
        INSERT INTO users (name, family_name, phone_number, code, chat_id, tag, invited_with, user_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (name, family_name, phone_number, code, str(chat_id), tag, invited_with, str(chat))
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query, params=params)
                    con.commit()
        
        except Exception as e:
            print(f"error in register user:{e}")

    def exist_user(self, chat_id):
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute("SELECT 1 FROM users WHERE user_id = %s LIMIT 1", (str(chat_id),))
                    res = cursor.fetchone() is not None
                    return res
        except Exception as e:
            print(f"Error in exist_user: {e}")
        
    def update_info(self, name, family_name, number, chat_id):
        query = """UPDATE users
        SET name = %s,
        family_name = %s, 
        phone_number = %s
        WHERE chat_id = %s"""
        params = (name, family_name, number, str(chat_id))
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query, params=params)
                    con.commit()
        except:
            print("error in update info")

    def get_info(self, chat_id):
        query = """SELECT * FROM users WHERE chat_id = %s"""
        params = (str(chat_id),)
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query, params=params)
                    res = cursor.fetchone()
                    return res
        except:
            return []
############################################################### service table #######################################################################

class serviceManagement:
    def __init__(self, db_pool):
        self.db_pool = db_pool
    
    def create_table_services(self):
        query = """
        CREATE TABLE IF NOT EXISTS services (
                id VARCHAR (255),
                service_bot VARCHAR (30),
                service_and VARCHAR (30),
                service_pro VARCHAR (30),
                service_andu VARCHAR (30),
                temp_service_and VARCHAR (30),
                temp_service_bot VARCHAR (30),
                temp_service_pro VARCHAR (30),
                temp_service_andu VARCHAR (30),
                INDEX (id)
        ) ENGINE=InnoDB;
        """ 
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query)
                    con.commit()
        except:
            print("error in create table services")

    def get_service(self, chat_id):
        query = """SELECT service_and FROM services WHERE id = %s"""
        params = (str(chat_id),)
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query, params=params)
                    res = cursor.fetchone()
                    return res
        except Exception as e:
            print(e)

    def get_service_u(self, chat_id):
        query = """SELECT service_andu FROM services WHERE id = %s"""
        params = (str(chat_id),)
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query, params=params)
                    res = cursor.fetchone()
                    return res
        except Exception as e:
            print(e)

    def get_service_bot(self, chat_id):
        query = """SELECT service_bot FROM services WHERE id = %s"""
        params = (str(chat_id),)
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query, params=params)
                    res = cursor.fetchone()
                    return res
        except:
            return []
        
    def get_service_pro(self, chat_id):
        query = """SELECT service_pro FROM services WHERE id = %s"""
        params = (str(chat_id),)
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query, params=params)
                    res = cursor.fetchone()
                    return res
        except:
            return []
    
    def set_service_bot(self, chat_id, service):
        query = """UPDATE services
        SET service_bot = %s
        WHERE id = %s"""
        params = (service, str(chat_id))
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query, params=params)
                    con.commit()
        except:
            print("error in ser_service_bot")

    def set_service_pro(self, chat_id, service):
        query = """UPDATE services
        SET service_pro = %s
        WHERE id = %s"""
        params = (service, str(chat_id))
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query, params=params)
                    con.commit()
        except:
            print("error in ser_service_pro")

    def set_service_u(self, chat_id, service):
        query = """UPDATE services
        SET service_andu = %s
        WHERE id = %s"""
        params = (service, str(chat_id))
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query, params=params)
                    con.commit()
        except:
            print("error in ser_service_pro")
    
    def set_service(self, chat_id, service):
        try:
            ser = self.get_service(chat_id)[0]
        except:
            ser = 'Nonee'
        if ser == 'Nonee' or ser == []:
            query = """
            INSERT INTO services (id, service_and)
            VALUES (%s, %s)
            """
            params = (str(chat_id), service)
            try:
                with self.db_pool.get_connection() as con:
                    with con.cursor(buffered=True) as cursor:
                        cursor.execute(query, params=params)
                        con.commit()
            except:
                print("error in ser_service")
        
        else:
            query = """UPDATE services
            SET service_and = %s
            WHERE id = %s"""
            params = (service, str(chat_id))
            try:
                with self.db_pool.get_connection() as con:
                    with con.cursor(buffered=True) as cursor:
                        cursor.execute(query, params=params)
                        con.commit()
            except:
                print("error in ser_service")

    def get_temp_bot(self, chat_id):
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute("SELECT temp_service_bot FROM services WHERE id = %s", (str(chat_id),))
                    res = cursor.fetchone()
                    return res
        except:
            return []
        
    def get_temp_pro(self, chat_id):
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute("SELECT temp_service_pro FROM services WHERE id = %s", (str(chat_id),))
                    res = cursor.fetchone()
                    return res
        except:
            return []
        
    def get_temp(self, chat_id):
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute("SELECT temp_service_and FROM services WHERE id = %s", (str(chat_id),))
                    res = cursor.fetchone()
                    return res
        except:
            return []

    def get_temp_u(self, chat_id):
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute("SELECT temp_service_andu FROM services WHERE id = %s", (str(chat_id),))
                    res = cursor.fetchone()
                    return res
        except:
            return []
        
    def update_temp_service(self, plan, char_id):
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute("UPDATE services SET temp_service_and = %s WHERE id = %s", (plan , str(char_id)))
                    con.commit()
        except:
            print("error in update_temp_service")

    def update_temp_service_u(self, plan, char_id):
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute("UPDATE services SET temp_service_andu = %s WHERE id = %s", (plan , str(char_id)))
                    con.commit()
        except:
            print("error in update_temp_service")
    
    def update_temp_service_bot(self, plan, char_id):
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute("UPDATE services SET temp_service_bot = %s WHERE id = %s", (plan , str(char_id)))
                    con.commit()
        except:
            print("error in update_temp_service_bot")

    def update_temp_service_pro(self, plan, char_id):
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute("UPDATE services SET temp_service_pro = %s WHERE id = %s", (plan , str(char_id)))
                    con.commit()
        except:
            print("error in update_temp_service_pro")
        
    def get_user_status(self):
        query = """SELECT service_and, COUNT(*) FROM services GROUP BY service_and"""
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query)
                    results = cursor.fetchall()
                    stats = {}
                    for row in results:
                        stats[row[0]] = row[1]

                    return stats
        except:
            return []

    def get_user_status_u(self):
        query = """SELECT service_andu, COUNT(*) FROM services GROUP BY service_andu"""
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query)
                    results = cursor.fetchall()
                    stats = {}
                    for row in results:
                        stats[row[0]] = row[1]

                    return stats
        except:
            return []

    def get_deactive_user_ids(self):
        query = "SELECT id FROM services WHERE service_and = 'None'"
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query)
                    ids = [row[0] for row in cursor.fetchall()]
                    return ids
        except:
            return []

    def get_deactive_user_ids_u(self):
        query = "SELECT id FROM services WHERE service_andu = 'None'"
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query)
                    ids = [row[0] for row in cursor.fetchall()]
                    return ids
        except:
            return []

    def get_active_user_ids(self):
        query = "SELECT id FROM services WHERE service_and != 'None'"
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query)
                    ids = [row[0] for row in cursor.fetchall()]
                    return ids
        except:
            return []

    def get_active_user_ids_u(self):
        query = "SELECT id FROM services WHERE service_andu != 'None'"
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query)
                    ids = [row[0] for row in cursor.fetchall()]
                    return ids
        except:
            return []
    
    def get_trial_user_ids(self):
        query = "SELECT id FROM services WHERE service_and = 'trial'"
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query)
                    ids = [row[0] for row in cursor.fetchall()]
                    return ids
        except:
            return []

    def get_trial_user_ids_u(self):
        query = "SELECT id FROM services WHERE service_andu = 'trial'"
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query)
                    ids = [row[0] for row in cursor.fetchall()]
                    return ids
        except:
            return []

    def get_basic_user_ids(self):
        query = "SELECT id FROM services WHERE service_and = 'یک ماهه'"
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query)
                    ids = [row[0] for row in cursor.fetchall()]
                    return ids
        except:
            return []

    def get_basic_user_ids_u(self):
        query = "SELECT id FROM services WHERE service_andu = 'یک ماهه الترا'"
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query)
                    ids = [row[0] for row in cursor.fetchall()]
                    return ids
        except:
            return []
    
    def get_pro_user_ids(self):
        query = "SELECT id FROM services WHERE service_and = 'سه ماهه'"
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query)
                    ids = [row[0] for row in cursor.fetchall()]
                    return ids
        except:
            return []

    def get_pro_user_ids_u(self):
        query = "SELECT id FROM services WHERE service_andu = 'سه ماهه الترا'"
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query)
                    ids = [row[0] for row in cursor.fetchall()]
                    return ids
        except:
            return []

    def get_elite_user_ids(self):
        query = "SELECT id FROM services WHERE service_and = 'شش ماهه'"
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query)
                    ids = [row[0] for row in cursor.fetchall()]
                    return ids
        except:
            return []

    def get_elite_user_ids_u(self):
        query = "SELECT id FROM services WHERE service_andu = 'شش ماهه الترا'"
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query)
                    ids = [row[0] for row in cursor.fetchall()]
                    return ids
        except:
            return []


    def get_user_status_bot(self):
        query = """SELECT service_bot, COUNT(*) FROM services GROUP BY service_bot"""
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query)
                    results = cursor.fetchall()
                    stats = {}
                    for row in results:
                        stats[row[0]] = row[1]

                    return stats
        except:
            return []

    def get_deactive_user_ids_bot(self):
        query = "SELECT id FROM services WHERE service_bot = 'None'"
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query)
                    ids = [row[0] for row in cursor.fetchall()]
                    return ids
        except:
            return []

    def get_active_user_ids_bot(self):
        query = "SELECT id FROM services WHERE service_bot != 'None'"
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query)
                    ids = [row[0] for row in cursor.fetchall()]
                    return ids
        except:
            return []
    
    def get_trial_user_ids_bot(self):
        query = "SELECT id FROM services WHERE service_bot = 'trial'"
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query)
                    ids = [row[0] for row in cursor.fetchall()]
                    return ids
        except:
            return []

    def get_basic_user_ids_bot(self):
        query = "SELECT id FROM services WHERE service_bot = 'بات یک ماهه'"
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query)
                    ids = [row[0] for row in cursor.fetchall()]
                    return ids
        except:
            return []
    
    def get_pro_user_ids_bot(self):
        query = "SELECT id FROM services WHERE service_bot = 'بات سه ماهه'"
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query)
                    ids = [row[0] for row in cursor.fetchall()]
                    return ids
        except:
            return []

    def get_elite_user_ids_bot(self):
        query = "SELECT id FROM services WHERE service_bot = 'بات شش ماهه'"
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query)
                    ids = [row[0] for row in cursor.fetchall()]
                    return ids
        except:
            return []
        

    def get_user_status_pro(self):
        query = """SELECT service_pro, COUNT(*) FROM services GROUP BY service_pro"""
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query)
                    results = cursor.fetchall()
                    stats = {}
                    for row in results:
                        stats[row[0]] = row[1]

                    return stats
        except:
            return []

    def get_deactive_user_ids_pro(self):
        query = "SELECT id FROM services WHERE service_pro = 'None'"
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query)
                    ids = [row[0] for row in cursor.fetchall()]
                    return ids
        except:
            return []

    def get_active_user_ids_pro(self):
        query = "SELECT id FROM services WHERE service_pro != 'None'"
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query)
                    ids = [row[0] for row in cursor.fetchall()]
                    return ids
        except:
            return []
    
    def get_trial_user_ids_pro(self):
        query = "SELECT id FROM services WHERE service_pro = 'trial'"
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query)
                    ids = [row[0] for row in cursor.fetchall()]
                    return ids
        except:
            return []

    def get_basic_user_ids_pro(self):
        query = "SELECT id FROM services WHERE service_pro = 'بات پرو یک ماهه'"
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query)
                    ids = [row[0] for row in cursor.fetchall()]
                    return ids
        except:
            return []
    
    def get_pro_user_ids_pro(self):
        query = "SELECT id FROM services WHERE service_pro = 'بات پرو سه ماهه'"
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query)
                    ids = [row[0] for row in cursor.fetchall()]
                    return ids
        except:
            return []

    def get_elite_user_ids_pro(self):
        query = "SELECT id FROM services WHERE service_pro = 'بات پرو شش ماهه'"
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query)
                    ids = [row[0] for row in cursor.fetchall()]
                    return ids
        except:
            return []
  
        
####################################################################TRIAL TABLE#########################################################
    def create_table_trial(self):
        query = """
        CREATE TABLE IF NOT EXISTS trial (
                id VARCHAR (255),
                start_at DATE,
                expires_at DATE,
                is_activet BOOLEAN DEFAULT 1,
                INDEX (id)
        ) ENGINE=InnoDB;
        """ 
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query)
                    con.commit()
        except:
            print("error in create table trial")
    
    def set_date_3(self, chat_id):
        now = datetime.date.today()
        ex_date = datetime.date.today() + timedelta(days=3)
        query = """INSERT INTO trial (id, start_at, expires_at) VALUES (%s, %s, %s)"""
        params = (str(chat_id), now, ex_date)
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query, params=params)
                    con.commit()
        except Exception as e:
           print(f"error in set_date_3:{e}")

    def get_date_3(self, chat_id):
        query = """SELECT expires_at FROM trial WHERE id = %s"""
        params = (str(chat_id),)
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query, params=params)
                    res = cursor.fetchone()
                    return res
        except Exception as e:
            print(e)
            
        
    def set_expiration_notified3(self, chat_id):
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute("UPDATE trial SET is_activet = %s WHERE id = %s", (0, str(chat_id)))
                    con.commit()
        except:
            print("error in set_expiration_trial")

    def get_trial(self):
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute("SELECT id, expires_at FROM trial WHERE is_activet = %s", (1,))
                    res = cursor.fetchall()
                    return res
        except:
            return []
##############################################################andicator table##############################################################
    def create_table_andicator(self):
        query = """
        CREATE TABLE IF NOT EXISTS andicators (
                id VARCHAR (255),
                t_id_1 VARCHAR (255),
                t_id_2 VARCHAR (255),
                start_at DATE,
                expires_at DATE,
                is_active BOOLEAN,
                message_sent BOOLEAN,
                INDEX (id)
        ) ENGINE=InnoDB;
        """ 
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query)
                    con.commit()
        except:
            print("error in create table ADNICATORS")
    
    def get_date(self, chat_id):
        query = """SELECT expires_at FROM andicators WHERE id = %s"""
        params = (str(chat_id),)
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query, params)
                    res = cursor.fetchone()
                    return res
        except Exception as e:
            print(e)
        
    def get_ids(self, chat_id):
        query = """SELECT t_id_1, t_id_2 FROM andicators WHERE id = %s"""
        params = (str(chat_id),)
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query, params=params)
                    res = cursor.fetchone()
                    res = [res[0], res[1]]
                    return res
        except:
            return []
        
    def set_ids(self, chat_id, t1, t2):
        query = "SELECT EXISTS(SELECT 1 FROM andicators WHERE id = %s)"

        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query, (str(chat_id),))
                    result = cursor.fetchone()
                    res = bool(result[0])

        except Exception as e:
            print(f"Error checking id: {e}")
            res = False
        if not res:
            query = """
            INSERT INTO andicators (id, t_id_1, t_id_2)
            VALUES (%s, %s, %s)
            """
            params = (str(chat_id), t1, t2)
            try:
                with self.db_pool.get_connection() as con:
                    with con.cursor(buffered=True) as cursor:
                        cursor.execute(query, params=params)
                        con.commit()
            except:
                print("error in set_ids")
        else:
            query = """UPDATE andicators
            SET t_id_1 = %s,
            t_id_2 = %s
            WHERE id = %s"""
            params = (t1, t2, str(chat_id))
            try:
                with self.db_pool.get_connection() as con:
                    with con.cursor(buffered=True) as cursor:
                        cursor.execute(query, params=params)
                        con.commit()
            except:
                print("error in set_ids")

    def get_expired_users_to_notify(self):
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute("SELECT id, expires_at, t_id_1, t_id_2 FROM andicators WHERE message_sent = 0")
                    res = cursor.fetchall()
                    return res
        except:
            return []

    def get_expired_users_to_ban(self):
        p = (1,)
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute("SELECT id, expires_at, t_id_1, t_id_2 FROM andicators WHERE is_active = %s", p)
                    res = cursor.fetchall()
                    return res
        except Exception as e:
            print(e)
            return []
    
    def set_expiration_ban(self, chat_id):
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute("UPDATE andicators SET is_active = %s WHERE id = %s", (0, str(chat_id)))
                    con.commit()
        except:
            print("error in set ban")

    def set_expiration_notified(self, chat_id):
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute("UPDATE andicators SET message_sent = %s WHERE id = %s", (1, str(chat_id)))
                    con.commit()
        except Exception as e:
            print("error in set notified", e)
    
    def set_date(self, chat_id, service):
        now = datetime.date.today()
        p = (str(chat_id),)
        query1 = "SELECT expires_at FROM andicators WHERE id = %s"
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query1, p)
                    re = cursor.fetchone()
        except Exception as e:
            print("failed", e)
            re = []
        month = re[0].month
        year = re[0].year
        day = re[0].day
        if service == 'یک ماهه':
            ex = 1
        elif service == 'سه ماهه':
            ex = 3
        else:
            ex = 6
        ex_month = month + ex
        if ex_month > 12:
            ex_month = ex_month - 12
            year += 1
        ex_date = datetime.date(year, ex_month, day)
        query = """UPDATE andicators
        SET expires_at = %s,
        start_at = %s,
        is_active = %s,
        message_sent = %s
        WHERE id = %s"""
        params = (ex_date, now, 1, 0, str(chat_id))
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query, params=params)
                    con.commit()
        except Exception as e:
            print(f"error in set_date:{e}")

    def set_date_buy(self, chat_id, service):
        now = datetime.date.today()
        year = now.year
        month = now.month
        day = now.day
        if service == 'یک ماهه':
            ex = 1
        elif service == 'سه ماهه':
            ex = 3
        else:
            ex = 6
        ex_month = month + ex
        if ex_month > 12:
            ex_month = ex_month - 12
            year += 1
        ex_date = datetime.date(year, ex_month, day)
        query = """UPDATE andicators
        SET expires_at = %s,
        start_at = %s,
        is_active = %s,
        message_sent = %s
        WHERE id = %s"""
        params = (ex_date, now, 1, 0, str(chat_id))
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query, params=params)
                    con.commit()
        except Exception as e:
            print(f"error in set_date:{e}")

##############################################################andicator ultra table##############################################################
    def create_table_andicator_u(self):
        query = """
        CREATE TABLE IF NOT EXISTS andicators_u (
                id VARCHAR (255),
                t_id_1 VARCHAR (255),
                t_id_2 VARCHAR (255),
                start_at DATE,
                expires_at DATE,
                is_active BOOLEAN DEFAULT 1,
                message_sent BOOLEAN DEFAULT 0,
                INDEX (id)
        ) ENGINE=InnoDB;
        """ 
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query)
                    con.commit()
        except:
            print("error in create table ADNICATORS")
    
    def get_date_u(self, chat_id):
        query = """SELECT expires_at FROM andicators_u WHERE id = %s"""
        params = (str(chat_id),)
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query, params)
                    res = cursor.fetchone()
                    return res
        except Exception as e:
            print(e)
        
    def get_ids_u(self, chat_id):
        query = """SELECT t_id_1, t_id_2 FROM andicators_u WHERE id = %s"""
        params = (str(chat_id),)
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query, params=params)
                    res = cursor.fetchone()
                    res = [res[0], res[1]]
                    return res
        except:
            return []
        
    def set_ids_u(self, chat_id, t1, t2):
        query = "SELECT EXISTS(SELECT 1 FROM andicators_u WHERE id = %s)"

        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query, (str(chat_id),))
                    result = cursor.fetchone()
                    res = bool(result[0])

        except Exception as e:
            print(f"Error checking id: {e}")
            res = False
        if not res:
            query = """
            INSERT INTO andicators_u (id, t_id_1, t_id_2)
            VALUES (%s, %s, %s)
            """
            params = (str(chat_id), t1, t2)
            try:
                with self.db_pool.get_connection() as con:
                    with con.cursor(buffered=True) as cursor:
                        cursor.execute(query, params=params)
                        con.commit()
            except:
                print("error in set_ids")
        else:
            query = """UPDATE andicators_u
            SET t_id_1 = %s,
            t_id_2 = %s
            WHERE id = %s"""
            params = (t1, t2, str(chat_id))
            try:
                with self.db_pool.get_connection() as con:
                    with con.cursor(buffered=True) as cursor:
                        cursor.execute(query, params=params)
                        con.commit()
            except:
                print("error in set_ids")

    def get_expired_users_to_notify_u(self):
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute("SELECT id, expires_at, t_id_1, t_id_2 FROM andicators_u WHERE message_sent = 0")
                    res = cursor.fetchall()
                    return res
        except:
            return []

    def get_expired_users_to_ban_u(self):
        p = (1,)
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute("SELECT id, expires_at, t_id_1, t_id_2 FROM andicators_u WHERE is_active = %s", p)
                    res = cursor.fetchall()
                    return res
        except Exception as e:
            print(e)
            return []
    
    def set_expiration_ban_u(self, chat_id):
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute("UPDATE andicators_u SET is_active = %s WHERE id = %s", (0, str(chat_id)))
                    con.commit()
        except:
            print("error in set ban")

    def set_expiration_notified_u(self, chat_id):
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute("UPDATE andicators_u SET message_sent = %s WHERE id = %s", (1, str(chat_id)))
                    con.commit()
        except Exception as e:
            print("error in set notified", e)
    
    def set_date_u(self, chat_id, service):
        now = datetime.date.today()
        p = (str(chat_id),)
        query1 = "SELECT expires_at FROM andicators_u WHERE id = %s"
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query1, p)
                    re = cursor.fetchone()
        except Exception as e:
            print("failed", e)
            re = []
        month = re[0].month
        year = re[0].year
        day = re[0].day
        if service == 'یک ماهه الترا':
            ex = 1
        elif service == 'سه ماهه الترا':
            ex = 3
        else:
            ex = 6
        ex_month = month + ex
        if ex_month > 12:
            ex_month = ex_month - 12
            year += 1
        ex_date = datetime.date(year, ex_month, day)
        query = """UPDATE andicators_u
        SET expires_at = %s,
        start_at = %s,
        is_active = %s,
        message_sent = %s
        WHERE id = %s"""
        params = (ex_date, now, 1, 0, str(chat_id))
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query, params=params)
                    con.commit()
        except Exception as e:
            print(f"error in set_date:{e}")

    def set_date_buy_u(self, chat_id, service):
        now = datetime.date.today()
        year = now.year
        month = now.month
        day = now.day
        if service == 'یک ماهه الترا':
            ex = 1
        elif service == 'سه ماهه الترا':
            ex = 3
        else:
            ex = 6
        ex_month = month + ex
        if ex_month > 12:
            ex_month = ex_month - 12
            year += 1
        ex_date = datetime.date(year, ex_month, day)
        query = """UPDATE andicators_u
        SET expires_at = %s,
        start_at = %s,
        is_active = %s,
        message_sent = %s
        WHERE id = %s"""
        params = (ex_date, now, 1, 0, str(chat_id))
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query, params=params)
                    con.commit()
        except Exception as e:
            print(f"error in set_date:{e}")

    def set_date_3_u(self, chat_id):
        now = datetime.date.today()
        ex_date = datetime.date.today() + timedelta(days=3)
        query = """UPDATE andicators_u
        SET expires_at = %s,
        start_at = %s
        WHERE id = %s"""
        params = (ex_date, now, str(chat_id))
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query, params=params)
                    con.commit()
        except Exception as e:
           print(f"error in set_date_3_u:{e}")

#####################################################license table###########################################
    def create_table_license(self):
        query = """
        CREATE TABLE IF NOT EXISTS licenses (
                id VARCHAR (255),
                license_key VARCHAR (255),
                account_1_id VARCHAR (255),
                account_2_id VARCHAR (255),
                is_active BOOLEAN DEFAULT 1,
                start_at DATE,
                expires_at DATE,
                message_sent BOOLEAN DEFAULT 0,
                counter INT,
                INDEX (id)
        ) ENGINE=InnoDB;
        """ 
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query)
                    con.commit()
        except:
            print("error in create table licenses")
    
    def get_date_bot(self, chat_id):
        query = """SELECT expires_at FROM licenses WHERE id = %s"""
        params = (str(chat_id),)
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query, params)
                    res = cursor.fetchone()
                    return res
        except Exception as e:
            return []
        
    def get_expired_users_to_notify_bot(self):
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute("SELECT id, expires_at FROM licenses WHERE message_sent = 0")
                    res = cursor.fetchall()
                    return res
        except:
            return []

    def get_expired_users_to_ban_bot(self):
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute("SELECT id, expires_at FROM licenses WHERE is_active = 1")
                    res = cursor.fetchall()
                    return res
        except:
            return []
    
    def set_expiration_ban_bot(self, chat_id):
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute("UPDATE licenses SET is_active = %s WHERE id = %s", (0, str(chat_id)))
                    con.commit()
        except:
            print("error in set ban")

    def set_expiration_notified_bot(self, chat_id):
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute("UPDATE licenses SET message_sent = %s WHERE id = %s", (1, str(chat_id)))
                    con.commit()
        except Exception as e:
            print("error in set notified bot", e)
    
    def increase_counter(self, chat_id):
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute("UPDATE licenses SET counter = counter + 1 WHERE id = %s", (str(chat_id),))
                    con.commit()
                    if cursor.rowcount > 0:
                        print("update success")
        except:
            print("error in increase counter")
        
    def get_counter(self, chat_id):
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute("SELECT counter FROM licenses WHERE id = %s", (str(chat_id),))
                    res = cursor.fetchone()
                    return res
        except Exception as e:
            print(e)
            return []

    def register_licese(self, chat_id, li, count):
        query = """INSERT INTO licenses (id, license_key, counter) VALUES (%s, %s, %s)"""
        P = (str(chat_id), li, count)
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query, P)
                    con.commit()
        except:
            print("error in r l")
    
    def update_license(self, chat_id, li):
        query = """UPDATE licenses
        SET license_key = %s
        WHERE id = %s"""
        p = (li, str(chat_id))
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query, p)
                    con.commit()
        except:
            print("error in p l")

    def del_license(self, chat_id):
        query = """DELETE FROM licenses WHERE id = %s"""
        p = (str(chat_id),)
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query, p)
                    con.commit()
        except:
            print("error in d l")
    
    def set_date_3_bot(self, chat_id):
        now = datetime.date.today()
        ex_date = datetime.date.today() + timedelta(days=3)
        query = """UPDATE licenses
        SET expires_at = %s,
        start_at = %s
        WHERE id = %s"""
        params = (ex_date, now, str(chat_id))
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query, params=params)
                    con.commit()
        except Exception as e:
           print(f"error in set_date_3_b:{e}")

    def set_account_id(self, chat_id, val):
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute("UPDATE licenses SET account_2_id = %s WHERE id = %s", (val, str(chat_id)))
                    con.commit()
        except:
            print("error in set ban")
    
    def set_date_bot(self, chat_id, service):
        now = datetime.date.today()
        query1 = "SELECT expires_at FROM licenses WHERE id = %s"
        p = (str(chat_id),)
        print(p)
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query1, p)
                    re = cursor.fetchone()
        except Exception as e:
            print("error", e)
        print(re)
        month = re[0].month
        year = re[0].year
        day = re[0].day
        if service == 'بات یک ماهه':
            ex = 1
        elif service == 'بات سه ماهه':
            ex = 3
        else:
            ex = 6
        ex_month = month + ex
        if ex_month > 12:
            ex_month = ex_month - 12
            year += 1
        ex_date = datetime.date(year, ex_month, day)
        query = """UPDATE licenses
        SET expires_at = %s,
        start_at = %s,
        is_active = %s,
        message_sent = %s
        WHERE id = %s"""
        params = (ex_date, now, 1, 0, str(chat_id))
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query, params=params)
                    con.commit()
        except Exception as e:
            print(f"error in set_date:{e}")

    def set_date_buy_bot(self, chat_id, service):
        now = datetime.date.today()
        year = now.year
        month = now.month
        day = now.day
        if service == 'بات یک ماهه':
            ex = 1
        elif service == 'بات سه ماهه':
            ex = 3
        else:
            ex = 6
        ex_month = month + ex
        if ex_month > 12:
            ex_month = ex_month - 12
            year += 1
        ex_date = datetime.date(year, ex_month, day)
        query = """UPDATE licenses
        SET expires_at = %s,
        start_at = %s,
        is_active = %s,
        message_sent = %s
        WHERE id = %s"""
        params = (ex_date, now, 1, 0, str(chat_id))
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query, params=params)
                    con.commit()
        except Exception as e:
            print(f"error in set_date:{e}")
     

#####################################################license pro table###########################################
    def create_table_license_pro(self):
        query = """
        CREATE TABLE IF NOT EXISTS licenses_pro (
                id VARCHAR (255),
                license_key VARCHAR (255),
                account_1_id VARCHAR (255),
                account_2_id VARCHAR (255),
                is_active BOOLEAN DEFAULT 1,
                start_at DATE,
                expires_at DATE,
                message_sent BOOLEAN DEFAULT 0,
                counter INT,
                INDEX (id)
        ) ENGINE=InnoDB;
        """ 
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query)
                    con.commit()
        except:
            print("error in create table licenses_pro")
    
    def get_date_bot_pro(self, chat_id):
        query = """SELECT expires_at FROM licenses_pro WHERE id = %s"""
        params = (str(chat_id),)
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query, params)
                    res = cursor.fetchone()
                    return res
        except Exception as e:
            return []
        
    def get_expired_users_to_notify_bot_pro(self):
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute("SELECT id, expires_at FROM licenses_pro WHERE message_sent = 0")
                    res = cursor.fetchall()
                    return res
        except:
            return []

    def get_expired_users_to_ban_bot_pro(self):
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute("SELECT id, expires_at FROM licenses_pro WHERE is_active = 1")
                    res = cursor.fetchall()
                    return res
        except:
            return []
    
    def set_expiration_ban_bot_pro(self, chat_id):
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute("UPDATE licenses_pro SET is_active = %s WHERE id = %s", (0, str(chat_id)))
                    con.commit()
        except:
            print("error in set ban_pro")

    def set_expiration_notified_bot_pro(self, chat_id):
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute("UPDATE licenses_pro SET message_sent = %s WHERE id = %s", (1, str(chat_id)))
                    con.commit()
        except Exception as e:
            print("error in set notified bot_pro", e)
    
    def increase_counter_pro(self, chat_id):
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute("UPDATE licenses_pro SET counter = counter + 1 WHERE id = %s", (str(chat_id),))
                    con.commit()
                    if cursor.rowcount > 0:
                        print("update success")
        except:
            print("error in increase counter_pro")
        
    def get_counter_pro(self, chat_id):
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute("SELECT counter FROM licenses_pro WHERE id = %s", (str(chat_id),))
                    res = cursor.fetchone()
                    return res
        except Exception as e:
            print(e)
            return []

    def register_licese_pro(self, chat_id, li, count):
        query = """INSERT INTO licenses_pro (id, license_key, counter) VALUES (%s, %s, %s)"""
        P = (str(chat_id), li, count)
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query, P)
                    con.commit()
        except:
            print("error in r l_pro")
    
    def update_license_pro(self, chat_id, li):
        query = """UPDATE licenses_pro
        SET license_key = %s
        WHERE id = %s"""
        p = (li, str(chat_id))
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query, p)
                    con.commit()
        except:
            print("error in p l_pro")

    def del_license_pro(self, chat_id):
        query = """DELETE FROM licenses_pro WHERE id = %s"""
        p = (str(chat_id),)
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query, p)
                    con.commit()
        except:
            print("error in d l")
    
    def set_date_3_bot_pro(self, chat_id):
        now = datetime.date.today()
        ex_date = datetime.date.today() + timedelta(days=3)
        query = """UPDATE licenses_pro
        SET expires_at = %s,
        start_at = %s
        WHERE id = %s"""
        params = (ex_date, now, str(chat_id))
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query, params=params)
                    con.commit()
        except Exception as e:
           print(f"error in set_date_3_b_pro:{e}")

    def set_account_id_pro(self, chat_id, val):
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute("UPDATE licenses_pro SET account_2_id = %s WHERE id = %s", (val, str(chat_id)))
                    con.commit()
        except:
            print("error in set ban")
    
    def set_date_bot_pro(self, chat_id, service):
        now = datetime.date.today()
        query1 = "SELECT expires_at FROM licenses_pro WHERE id = %s"
        p = (str(chat_id),)
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query1, p)
                    re = cursor.fetchone()
        except Exception as e:
            print("error", e)
        month = re[0].month
        year = re[0].year
        day = re[0].day
        if service == 'بات پرو یک ماهه':
            ex = 1
        elif service == 'بات پرو سه ماهه':
            ex = 3
        else:
            ex = 6
        ex_month = month + ex
        if ex_month > 12:
            ex_month = ex_month - 12
            year += 1
        ex_date = datetime.date(year, ex_month, day)
        query = """UPDATE licenses_pro
        SET expires_at = %s,
        start_at = %s,
        is_active = %s,
        message_sent = %s
        WHERE id = %s"""
        params = (ex_date, now, 1, 0, str(chat_id))
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query, params=params)
                    con.commit()
        except Exception as e:
            print(f"error in set_date:{e}")

    def set_date_buy_bot_pro(self, chat_id, service):
        now = datetime.date.today()
        year = now.year
        month = now.month
        day = now.day
        if service == 'بات پرو یک ماهه':
            ex = 1
        elif service == 'بات پرو سه ماهه':
            ex = 3
        else:
            ex = 6
        ex_month = month + ex
        if ex_month > 12:
            ex_month = ex_month - 12
            year += 1
        ex_date = datetime.date(year, ex_month, day)
        query = """UPDATE licenses_pro
        SET expires_at = %s,
        start_at = %s,
        is_active = %s,
        message_sent = %s
        WHERE id = %s"""
        params = (ex_date, now, 1, 0, str(chat_id))
        try:
            with self.db_pool.get_connection() as con:
                with con.cursor(buffered=True) as cursor:
                    cursor.execute(query, params=params)
                    con.commit()
        except Exception as e:
            print(f"error in set_date:{e}")
     