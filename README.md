# Name Change Analysis Process

This document outlines the steps for analyzing user name change requests and related data.

## 1. Extract User Data for Name Change Requests

Execute the following SQL query to get user data for name change requests after August 1, 2024:

```sql
SELECT * 
FROM afbet_patron.t_patron_name_update_submission a 
INNER JOIN afbet_patron.t_patron_user_certification b 
ON a.user_id = b.user_id 
WHERE a.create_time > '2024-08-01'
```

Save the results as raw data for further analysis.

## 2. Analyze Name Change Proportions

Run `nameComfirmWith340and350.py` to analyze the overall proportion of name changes for users 340 and 350, as well as the distribution of similarity between user names and proposed updated names.

Output:
- `name_similarity_distribution.png`: Distribution of name similarities
- `status_distribution.png`: Distribution of name change statuses

## 3. Extract First Deposit Transaction Data

Execute `getNameUpdateUserTransactionFromAttribute.py` to obtain the First Deposit transaction ID and time for users requesting name changes. The script will output this data as a CSV file.

## 4. Analyze Historical First Deposit Channels

For transactions older than six months:
1. Run `extraceCsvFromAttributeForHis.py` to generate SQL queries for users 340 and 350.
2. Execute the generated SQL queries in your SQL tool to get the count of each first deposit channel.

## 5. Analyze Recent First Deposit Channels

For transactions within the last six months:
1. Run `getUserFirstDepositChannelByUserIdAndTradeId.py` to get the count of each first deposit channel.

## 6. Visualize First Deposit Channel Distribution

Execute `getUserFirstDepositChannelView.py` to create a proportion chart of first deposit channels.

## 7. Investigate Opay Users (350) Requiring Name Updates

1. Extract 350 users with Opay as their First Deposit method using the following SQL query:

```sql
SELECT a.id, a.phone, b.submission_content 
FROM afbet_patron.t_patron_user a 
INNER JOIN afbet_patron.t_patron_name_update_submission b 
ON a.id = b.user_id 
WHERE a.id IN (...)  -- Insert relevant user IDs here
```

2. Run `useFirstDepositNameToComparePSApiName.py` using the phone numbers obtained from the query.

Output:
- Distribution data comparing Opay users' original names with their requested name changes
- Distribution data comparing Opay users' original names with bank-returned names

## Notes

- Ensure all Python scripts mentioned are in your working directory.
- Make sure you have the necessary database access and permissions to run the SQL queries.
- The analysis process may require adjustments based on your specific data structure and requirements.
