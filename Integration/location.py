def CoordinatestoLocation(latitude, longitude):
    location = None
    if 4.385422 < latitude < 4.385959 and 100.979104 < longitude < 100.979822:
        location = "Gate 1" 
    elif 4.372665 < latitude < 4.373278 and 100.969167 < longitude < 100.969711:
        location = "Gate 3"
    else:
        location = "Neither Gate 1 nor Gate 3"

    return location