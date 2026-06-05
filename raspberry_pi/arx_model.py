import numpy as np

# ─── ARX Model ────────────────────────────────────────────────────────────────
# ARX: y(t) = a1*y(t-1) + ... + ana*y(t-na) + b1*u(t-1) + ... + bnb*u(t-nb)
# y = soil moisture (%), u = irrigation duration (sec)
# Coefficients will be replaced with MATLAB-trained values later.
# For now we use placeholder coefficients for testing.

class ARXModel:
    def __init__(self):
        # AR coefficients (soil moisture history)
        self.A = np.array([0.85, 0.10])        # na = 2
        # Exogenous coefficients (irrigation input history)
        self.B = np.array([0.003, 0.002])       # nb = 2
        # Noise offset
        self.offset = 0.5

        print("[ARX] Model initialized with placeholder coefficients.")
        print(f"[ARX] A = {self.A}, B = {self.B}")

    def load_coefficients(self, A: np.ndarray, B: np.ndarray):
        """Load trained coefficients exported from MATLAB."""
        self.A = A
        self.B = B
        print(f"[ARX] Coefficients updated. A = {A}, B = {B}")

    def predict(self, y_history: list, u_history: list) -> float:
        """
        Predict next soil moisture value.
        y_history: list of past moisture readings (most recent last)
        u_history: list of past irrigation inputs in seconds (most recent last)
        Returns: predicted moisture %
        """
        na = len(self.A)
        nb = len(self.B)

        # Pad histories if not enough data yet
        y = np.array(y_history[-na:] if len(y_history) >= na
                     else [y_history[0]] * (na - len(y_history)) + y_history)
        u = np.array(u_history[-nb:] if len(u_history) >= nb
                     else [0.0] * (nb - len(u_history)) + u_history)

        y_pred = float(np.dot(self.A, y) + np.dot(self.B, u) + self.offset)

        # Clamp to valid range
        return max(0.0, min(100.0, y_pred))

    def predict_horizon(self, y_history: list, u_sequence: list) -> list:
        """
        Predict moisture over a future horizon given a sequence of inputs.
        u_sequence: list of future irrigation durations (Np steps)
        Returns: list of predicted moisture values
        """
        y_hist = list(y_history)
        u_hist = [0.0] * len(self.B)
        predictions = []

        for u in u_sequence:
            y_next = self.predict(y_hist, u_hist)
            predictions.append(y_next)
            y_hist.append(y_next)
            u_hist.append(u)

        return predictions


# ─── Quick Test ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    model = ARXModel()

    # Simulate 5 past readings at ~40% moisture
    y_history = [40.0, 39.5, 39.0, 38.5, 38.0]
    # No irrigation in past
    u_history = [0.0, 0.0]

    # Predict next value with no irrigation
    y_no_irr = model.predict(y_history, u_history)
    print(f"[ARX] Predicted moisture (no irrigation): {y_no_irr:.2f}%")

    # Predict next value with 120 sec irrigation
    y_irr = model.predict(y_history, [0.0, 120.0])
    print(f"[ARX] Predicted moisture (120s irrigation): {y_irr:.2f}%")

    # Predict over 10-step horizon
    u_seq = [120.0] + [0.0] * 9
    horizon = model.predict_horizon(y_history, u_seq)
    print(f"[ARX] 10-step horizon: {[round(v,1) for v in horizon]}")
    print("[ARX] Test passed ✓")