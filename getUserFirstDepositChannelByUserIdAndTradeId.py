import csv
import mysql.connector
from collections import defaultdict

def connect_to_database(host, database, port):
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

def get_shard_and_suffix(user_id):
    last_two_digits = int(user_id[-2:])
    shard_index = last_two_digits // 20
    shard_suffix = str(last_two_digits).zfill(2)
    
    if 0 <= last_two_digits < 20:
        shard_host = 'sporty-ng-prod-bet-pocket-shard-00.cluster-ro-cvdgobmslfew.eu-central-1.rds.amazonaws.com'
    elif 20 <= last_two_digits < 40:
        shard_host = 'sporty-ng-prod-bet-pocket-shard-20.cluster-ro-cvdgobmslfew.eu-central-1.rds.amazonaws.com'
    elif 40 <= last_two_digits < 60:
        shard_host = 'sporty-ng-prod-bet-pocket-shard-40.cluster-ro-cvdgobmslfew.eu-central-1.rds.amazonaws.com'
    elif 60 <= last_two_digits < 80:
        shard_host = 'sporty-ng-prod-bet-pocket-shard-60.cluster-ro-cvdgobmslfew.eu-central-1.rds.amazonaws.com'
    elif 80 <= last_two_digits < 100:
        shard_host = 'sporty-ng-prod-bet-pocket-shard-80.cluster-ro-cvdgobmslfew.eu-central-1.rds.amazonaws.com'
    else:
        raise ValueError(f"Invalid last two digits of user_id: {last_two_digits}")

    return shard_host, shard_suffix

def get_pay_channels_batch(cursor, user_trade_pairs, shard_suffix):
    if not user_trade_pairs:
        return {}

    if shard_suffix:
        table = f"t_pocket_pay_record_{shard_suffix}"
    else:
        table = "t_pocket_pay_record"

    placeholders = ', '.join(['(%s, %s)'] * len(user_trade_pairs))
    query = f"""
    SELECT user_id, trade_id, pay_id, pay_ch_id 
    FROM {table} 
    WHERE (user_id, trade_id) IN ({placeholders})
    """
    flat_params = [item for pair in user_trade_pairs for item in pair]

    try:
        print(f"\nExecuting SQL on table: {table}")
        print(f"SQL Query: {query}")
        print(f"Params: {flat_params}")
        cursor.execute(query, flat_params)
        results = cursor.fetchall()
        print(f"Query returned {len(results)} results")
        return {(row[0], row[1]): (row[2], row[3]) for row in results}  
    except mysql.connector.Error as err:
        print(f"Error querying {table}: {err}")
        return {}

def process_csv(input_file, output_file, row_limit=None):
    central_host = 'sportybet-ng-prod-pocket.cluster-ro-cvdgobmslfew.eu-central-1.rds.amazonaws.com'
    central_cnx = connect_to_database(central_host, 'afbet_pocket', '3306')
    if not central_cnx:
        print("Unable to connect to central database. Exiting.")
        return
    central_cursor = central_cnx.cursor()

    pay_ch_id_stats = {'340': defaultdict(int), '350': defaultdict(int)}
    results_to_write = []

    shard_data = defaultdict(list)
    with open(input_file, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for i, row in enumerate(reader):
            if row_limit is not None and i >= row_limit:
                break
            if row['need_query_his'] == 'No':
                user_id = row['user_id']
                shard_host, shard_suffix = get_shard_and_suffix(user_id)
                shard_data[(shard_host, shard_suffix)].append(row)
    
    shard_connections = {}

    for (shard_host, shard_suffix), rows in sorted(shard_data.items()):
        if shard_host not in shard_connections:
            shard_connections[shard_host] = connect_to_database(shard_host, 'afbet_pocket_shard', '3580')

        shard_cnx = shard_connections[shard_host]
        shard_cursor = shard_cnx.cursor()

        user_trade_pairs = [(row['user_id'], row['trade_id']) for row in rows]
        pay_channels = get_pay_channels_batch(shard_cursor, user_trade_pairs, shard_suffix)

        missing_pairs = [pair for pair in user_trade_pairs if pair not in pay_channels]

        if missing_pairs:
            central_pay_channels = get_pay_channels_batch(central_cursor, missing_pairs, '')
            pay_channels.update(central_pay_channels)

        for row in rows:
            user_id = row['user_id']
            trade_id = row['trade_id']
            status = row['status']
            pay_id, pay_ch_id = pay_channels.get((user_id, trade_id), (None, None))
            
            if pay_ch_id is not None:
                pay_ch_id_stats[status][pay_ch_id] += 1
                print(f"Processed user_id: {user_id}, status: {status}, pay_ch_id: {pay_ch_id}")
                if status == '350':
                    results_to_write.append({
                        'user_id': user_id,
                        'trade_id': trade_id,
                        'pay_id': pay_id,
                        'pay_ch_id': pay_ch_id,
                        'status': status
                    })
            else:
                print(f"No pay_ch_id found for user_id: {user_id}")

        shard_cursor.close()

    for cnx in shard_connections.values():
        cnx.close()

    central_cursor.close()
    central_cnx.close()

    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['user_id', 'trade_id', 'pay_id', 'pay_ch_id', 'status']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for result in results_to_write:
            writer.writerow(result)

    # Print statistics
    print("\nPay Channel ID Statistics:")
    for status in ['340', '350']:
        print(f"\nStatus {status}:")
        for pay_ch_id, count in pay_ch_id_stats[status].items():
            print(f"pay_ch_id {pay_ch_id}: {count}")

def main():
    input_file = "user_transactions.csv"  
    output_file = "status_350_results.csv"  
    row_limit = 20  
    process_csv(input_file, output_file)

if __name__ == "__main__":
    main()
