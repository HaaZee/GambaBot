def parse_string_to_int(input_str):
    input_str = input_str.lower()
    suffixes = {'k': 1000, 'm': 1000000, 'b': 1000000000, 't': 1000000000000, 'q': 1000000000000000} # what do make next
    
    if input_str.isdigit():
        return int(input_str)
    elif input_str[-1] in suffixes:
        multiplier = suffixes[input_str[-1]]
        try:
            number = float(input_str[:-1])
            return int(number * multiplier)
        except ValueError:
            raise ValueError("Invalid input format")
    else:
        raise ValueError("Invalid input format")
