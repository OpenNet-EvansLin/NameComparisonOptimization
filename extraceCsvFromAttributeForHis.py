import csv

INPUT_FILE_PATH = r'user_transactions.csv'
OUTPUT_FILE_PATH = r'user_transactions.txt'

def process_csv():
    try:
        with open(INPUT_FILE_PATH, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            records = [row for row in csv_reader if row['need_query_his'].lower() == 'yes' and row['status'] == '350']
    except FileNotFoundError:
        print(f"找不到文件 '{INPUT_FILE_PATH}'")
        return
    except Exception as e:
        print(f"讀取文件時發生錯誤: {e}")
        return

    if not records:
        print("沒有找到符合條件的記錄 (need_query_his = yes 且 status = 340)")
        return

    sql_query = "SELECT pay_ch_id FROM afbet_pocket.t_pocket_pay_record_his WHERE (user_id, trade_id) IN ("
    sql_query += ", ".join(f"('{record['user_id']}', '{record['trade_id']}')" for record in records)
    sql_query += ")"

    try:
        with open(OUTPUT_FILE_PATH, 'w', encoding='utf-8') as output_file:
            output_file.write(sql_query)
        print(f"SQL查詢已成功寫入到 {OUTPUT_FILE_PATH}")
    except Exception as e:
        print(f"寫入文件時發生錯誤: {e}")

if __name__ == "__main__":
    process_csv()