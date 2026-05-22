def calculate_consumption(area, coefficient=1.0):
    try:
        area_value = float(area)
    except (TypeError, ValueError):
        return 0
    return round(area_value * coefficient, 2)
