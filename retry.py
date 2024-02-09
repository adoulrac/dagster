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





def call_with_retry(func, max_retries, *args, **kwargs):
    retries = 0
    while retries < max_retries:
        try:
            result = func(*args, **kwargs)
            return result  # If successful, exit the loop
        except Exception as e:
            print(f"Error: {e}")
            retries += 1
            print(f"Retrying... ({retries}/{max_retries})")

    print("Max retries reached. Unable to execute the function.")
    return None  # or raise an exception, depending on your needs

# Example function to be retried
def example_function(arg1, arg2):
    # Your function code here
    # ...
    if arg1 == arg2:
        raise ValueError("Example error")

# Call your function with retry
result = call_with_retry(example_function, max_retries=3, arg1="value1", arg2="value2")

# Now you can use 'result' as needed