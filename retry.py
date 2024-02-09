max_retries = 3

def your_function():
    # Your function code here
    # ...

def call_with_retry():
    retries = 0
    while retries < max_retries:
        try:
            result = your_function()
            return result  # If successful, exit the loop
        except Exception as e:
            print(f"Error: {e}")
            retries += 1
            print(f"Retrying... ({retries}/{max_retries})")

    print("Max retries reached. Unable to execute the function.")
    return None  # or raise an exception, depending on your needs

# Call your function with retry
result = call_with_retry()

# Now you can use 'result' as needed