def get_stableswap_price(x, y, A):
    k = x + y
    numerator = 1 + 2 * A * (x ** 2) * y / ((k / 2) ** 3)
    denominator = 1 + 2 * A * x * (y ** 2) / ((k / 2) ** 3)
    return y / x * numerator / denominator

