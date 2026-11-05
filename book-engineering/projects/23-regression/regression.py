"""Two one-feature regressions, hand gradient descent and sklearn; synthetic data."""
import numpy as np
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, accuracy_score, log_loss
from sklearn.model_selection import train_test_split


def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-np.clip(z, -500.0, 500.0)))


def loss_and_gradient(X, y, weights, task):
    if len(y) == 0 or X.ndim != 2 or X.shape != (len(y), len(weights)):
        raise ValueError('incompatible or empty data')
    z = X @ weights
    if task == 'linear':
        residual = z - y
        return float(np.mean(residual ** 2)), 2 * X.T @ residual / len(y)
    if task == 'logistic':
        if not np.isin(y, (0, 1)).all():
            raise ValueError('logistic labels must be 0 or 1')
        loss = np.mean(np.logaddexp(0.0, z) - y * z)
        return float(loss), X.T @ (sigmoid(z) - y) / len(y)
    raise ValueError('unknown task')


def fit_gradient(X, y, task, rate=0.1, steps=3000):
    if rate <= 0 or steps <= 0: raise ValueError('rate and steps must be positive')
    weights = np.zeros(X.shape[1], dtype=float)
    for _ in range(steps):
        _, grad = loss_and_gradient(X, y, weights, task)
        weights -= rate * grad
    return weights


def data():
    rng = np.random.default_rng(42)
    x = rng.normal(size=240)
    y_linear = 1.5 + 2.0 * x + rng.normal(0, 0.3, len(x))
    y_binary = (rng.random(len(x)) < sigmoid(-0.3 + 1.2 * x)).astype(int)
    train, test = train_test_split(np.arange(len(x)), test_size=0.25, random_state=42, stratify=y_binary)
    return x, y_linear, y_binary, train, test


def main():
    x, yr, yc, train, test = data()
    X = np.column_stack((np.ones(len(x)), x))
    w_linear = fit_gradient(X[train], yr[train], 'linear')
    w_log = fit_gradient(X[train], yc[train], 'logistic')
    library_linear = LinearRegression().fit(x[train, None], yr[train])
    # No penalty: comparable objective to the manual implementation (sklearn 1.6).
    library_log = LogisticRegression(penalty=None, max_iter=2000, tol=1e-9).fit(x[train, None], yc[train])
    for name, pred in [('manual', X[test] @ w_linear), ('library', library_linear.predict(x[test,None]))]:
        print(f'{name}_regression MAE={mean_absolute_error(yr[test],pred):.6f} MSE={mean_squared_error(yr[test],pred):.6f}')
    for name, prob in [('manual', sigmoid(X[test] @ w_log)), ('library', library_log.predict_proba(x[test,None])[:,1])]:
        print(f'{name}_classification accuracy={accuracy_score(yc[test],prob>=0.5):.6f} logloss={log_loss(yc[test],prob,labels=[0,1]):.6f}')
    print(f'linear_manual_intercept={w_linear[0]:.6f} coef={w_linear[1]:.6f}')
    print(f'logistic_manual_intercept={w_log[0]:.6f} coef={w_log[1]:.6f}')
    print(f'train={len(train)} test={len(test)} seed=42 synthetic=true')

if __name__ == '__main__': main()
