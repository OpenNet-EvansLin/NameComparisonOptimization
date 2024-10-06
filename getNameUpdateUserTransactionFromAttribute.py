import csv
import json
import mysql.connector
from datetime import datetime, timedelta

def connect_to_database(host, database, port='3306'):
    config = {
        'user': '',
        'password': '',
        'host': host,
        'database': database,
        'port': port,
        'charset': 'utf8mb4',
        'collation': 'utf8mb4_unicode_ci',
    }
    try:
        print(f"\nConnecting to MySQL database:")
        print(f"Host: {host}")
        print(f"Database: {database}")
        print(f"Port: {port}")
        cnx = mysql.connector.connect(**config)
        print("Connection successful!")
        return cnx
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL database: {err}")
        return None

def get_transaction_info_batch(cursor, user_ids):
    placeholders = ', '.join(['%s'] * len(user_ids))
    query = f"SELECT user_id, value FROM t_pocket_user_attribute WHERE user_id IN ({placeholders}) AND `attribute` = 100"
    print(f"\nExecuting SQL: {query}")
    cursor.execute(query, user_ids)
    results = cursor.fetchall()
    
    transaction_info = {}
    for user_id, value in results:
        try:
            data = json.loads(value)
            trade_id = data.get('tradeId')
            create_time = datetime.fromtimestamp(data.get('createTime') / 1000)
            transaction_info[user_id] = (trade_id, create_time)
        except json.JSONDecodeError:
            print(f"Error decoding JSON for user {user_id}")
    
    return transaction_info

def process_csv(input_file, output_file, batch_size=1000):
    central_host = 'sportybet-ng-prod-pocket.cluster-ro-cvdgobmslfew.eu-central-1.rds.amazonaws.com'
    
    print("\nConnecting to central database...")
    central_cnx = connect_to_database(central_host, 'afbet_pocket')
    if not central_cnx:
        print("Unable to connect to central database. Exiting.")
        return
    
    central_cursor = central_cnx.cursor()
    
    six_months_ago = datetime.now() - timedelta(days=180)
    
    with open(input_file, 'r') as csvfile, open(output_file, 'w', newline='') as outfile:
        reader = csv.DictReader(csvfile)
        writer = csv.writer(outfile)
        writer.writerow(['user_id', 'trade_id', 'need_query_his', 'status'])
        
        batch_users = []
        batch_data = []
        
        for row in reader:
            user_id = row['user_id']
            status = row['status']
            
            if status in ['340', '350']:
                batch_users.append(user_id)
                batch_data.append((user_id, status))
            
            if len(batch_users) >= batch_size:
                process_batch(central_cursor, batch_users, batch_data, writer, six_months_ago)
                batch_users = []
                batch_data = []
        
        if batch_users:
            process_batch(central_cursor, batch_users, batch_data, writer, six_months_ago)
    
    central_cnx.close()
    print("\nDatabase connection closed.")

def process_batch(cursor, batch_users, batch_data, writer, six_months_ago):
    transaction_info = get_transaction_info_batch(cursor, batch_users)
    
    for user_id, status in batch_data:
        trade_id, create_time = transaction_info.get(user_id, (None, None))
        
        if trade_id and create_time:
            need_query_his = 'Yes' if create_time <= six_months_ago else 'No'
            writer.writerow([user_id, trade_id, need_query_his, status])
            print(f"Processed user_id: {user_id}, trade_id: {trade_id}, need_query_his: {need_query_his}, status: {status}")
        else:
            print(f"No transaction info found for user_id: {user_id}")

def main():
    input_file = "input_data.csv" 
    output_file = "user_transactions.csv"
    process_csv(input_file, output_file)
    print(f"Results have been written to {output_file}")

if __name__ == "__main__":
    main()