import csv
import os

def load_csv(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found")
        return []
    except Exception as e:
        print(f"Error: {str(e)}")
        return []

def generate_mysql_where_in(user_ids):
    formatted_ids = ', '.join(f"'{uid}'" for uid in user_ids)
    return f"WHERE user_id IN ({formatted_ids})"

def write_to_file(content, output_file):
    try:
        with open(output_file, 'w') as f:
            f.write(content)
        print(f"SQL query has been written to {output_file}")
    except Exception as e:
        print(f"Error writing to file: {str(e)}")

def main():
    input_file = "/Users/evanslin/Desktop/BATCH&SHELL/path_to_your_csv_file.csv"  # Replace with your actual CSV file name
    output_file = "/Users/evanslin/Desktop/BATCH&SHELL/verified_users_query.sql"  # Output SQL file
    
    data = load_csv(input_file)
    
    if not data:
        print("Unable to process data. Program terminated.")
        return

    verified_user_ids = [row['user_id'] for row in data if row['status'] == '350']

    mysql_where_in = generate_mysql_where_in(verified_user_ids)
    
    write_to_file(mysql_where_in, output_file)

if __name__ == "__main__":
    main()