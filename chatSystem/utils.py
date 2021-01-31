import string
import random

def get_random_alphanumeric_string():
    letters_and_digits = string.digits
    result_str = ''.join((random.choice(letters_and_digits) for i in range(32)))
    return result_str
