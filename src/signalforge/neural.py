"""A CPU PyTorch classifier with the sklearn estimator contract."""

import numpy as np
import torch
from sklearn.base import BaseEstimator, ClassifierMixin
from torch import nn


class TorchClassifier(ClassifierMixin, BaseEstimator):
    def __init__(self, hidden=32, epochs=70, lr=0.01, random_state=42):
        self.hidden = hidden
        self.epochs = epochs
        self.lr = lr
        self.random_state = random_state

    def fit(self, X, y):
        torch.set_num_threads(1)
        torch.manual_seed(self.random_state)
        self.classes_ = np.array([0, 1])
        self.n_features_in_ = X.shape[1]
        self.network_ = nn.Sequential(
            nn.Linear(X.shape[1], self.hidden),
            nn.ReLU(),
            nn.Dropout(0.15),
            nn.Linear(self.hidden, 1),
        )
        inputs = torch.tensor(np.asarray(X), dtype=torch.float32)
        labels = torch.tensor(np.asarray(y), dtype=torch.float32).reshape(-1, 1)
        weight = (len(labels) - labels.sum()) / labels.sum().clamp(min=1)
        loss_fn = nn.BCEWithLogitsLoss(pos_weight=weight)
        optimizer = torch.optim.Adam(self.network_.parameters(), lr=self.lr, weight_decay=0.001)
        self.network_.train()
        for _ in range(self.epochs):
            optimizer.zero_grad()
            loss = loss_fn(self.network_(inputs), labels)
            loss.backward()
            optimizer.step()
        self.network_.eval()
        return self

    def predict_proba(self, X):
        with torch.no_grad():
            p = torch.sigmoid(self.network_(torch.tensor(np.asarray(X), dtype=torch.float32)))
        p = p.numpy().reshape(-1)
        return np.column_stack([1 - p, p])

    def predict(self, X):
        return (self.predict_proba(X)[:, 1] >= 0.5).astype(int)
