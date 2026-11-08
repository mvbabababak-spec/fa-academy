"""Bayes calculation and seeded Bernoulli simulation on synthetic data."""
import math
import random
import statistics


def posterior_positive(prevalence, sensitivity, specificity):
    values = (prevalence, sensitivity, specificity)
    if any(not math.isfinite(v) or not 0 <= v <= 1 for v in values):
        raise ValueError('probabilities must be finite and between 0 and 1')
    numerator = prevalence * sensitivity
    positive = numerator + (1 - prevalence) * (1 - specificity)
    if positive == 0:
        raise ValueError('positive result has zero probability')
    return numerator / positive


def coin_fraction(n, seed=42):
    if type(n) is not int or n <= 0:
        raise ValueError('n must be a positive integer')
    rng = random.Random(seed)
    return sum(rng.random() < 0.5 for _ in range(n)) / n


def main():
    data = [2, 3, 3, 4, 8]
    print('mean=', statistics.mean(data), 'median=', statistics.median(data))
    print('sample_variance=', statistics.variance(data))
    print('posterior=', round(posterior_positive(0.01, 0.9, 0.95), 6))
    print('coin_fraction=', round(coin_fraction(10000), 4), 'seed=42')


if __name__ == '__main__':
    main()
