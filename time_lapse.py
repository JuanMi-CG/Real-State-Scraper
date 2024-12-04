from datetime import datetime



def days_since_last_email():
    file_path = 'last_sent_email.txt'
    try:
        with open(file_path, 'r') as file:
            last_date_str = file.read().strip()
        
        # Parse the date
        last_date = datetime.strptime(last_date_str, '%d/%m/%Y')

        # Calculate the difference
        today = datetime.today()
        difference = today - last_date

        return difference.days

    except FileNotFoundError:
        print(f"File {file_path} not found.")
        return -1  # Indicate an error with -1
    except ValueError:
        print("The date format in the file is incorrect. Please ensure it is in DD/MM/YYYY format.")
        return -1  # Indicate an error with -1
    

def update_last_email_date():
    file_path = 'last_sent_email.txt'
    try:
        # Get today's date in DD/MM/YYYY format
        today_str = datetime.today().strftime('%d/%m/%Y')

        # Write the current date to the file
        with open(file_path, 'w') as file:
            file.write(today_str)

        print(f"The file {file_path} has been updated with the current date: {today_str}")
        return True
    except Exception as e:
        print(f"An error occurred while updating the file: {e}")
        return False