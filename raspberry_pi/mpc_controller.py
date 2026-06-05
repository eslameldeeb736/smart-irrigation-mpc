import numpy as np
import cvxpy as cp
from arx_model import ARXModel

# ─── MPC Controller ───────────────────────────────────────────────────────────
class MPCController:
    def __init__(self, model: ARXModel):
        self.model = model

        self.Np = 10
        self.Nc = 3

        self.moisture_ref  = 60.0
        self.moisture_min  = 30.0
        self.moisture_max  = 85.0

        self.u_min = 0.0
        self.u_max = 300.0

        self.Q = 2.0
        self.R = 0.01
        self.S = 0.05

        print("[MPC] Controller initialized.")
        print(f"[MPC] Ref={self.moisture_ref}%, Horizon Np={self.Np}, Nc={self.Nc}")

    def compute(self, y_history: list, u_history: list) -> float:
        u = cp.Variable(self.Nc, nonneg=True)

        cost        = 0
        constraints = [u >= self.u_min, u <= self.u_max]

        y_hist = list(y_history)
        u_hist = list(u_history)
        u_prev = u_hist[-1] if u_hist else 0.0

        for k in range(self.Np):
            uk = u[min(k, self.Nc - 1)]

            na = len(self.model.A)
            nb = len(self.model.B)

            y_vec = (y_hist[-na:] if len(y_hist) >= na
                     else [y_hist[0]] * (na - len(y_hist)) + y_hist)
            u_vec = (u_hist[-nb:] if len(u_hist) >= nb
                     else [0.0] * (nb - len(u_hist)) + u_hist)

            y_next = (float(np.dot(self.model.A, y_vec)) +
                      float(np.dot(self.model.B[:-1], u_vec[1:])) +
                      self.model.B[-1] * uk +
                      self.model.offset)

            cost += self.Q * cp.square(self.moisture_ref - y_next)
            cost += self.R * cp.square(uk)

            if k == 0:
                cost += self.S * cp.square(uk - u_prev)
            else:
                cost += self.S * cp.square(uk - u[min(k-1, self.Nc-1)])

            slack_low  = cp.maximum(0, self.moisture_min - y_next)
            slack_high = cp.maximum(0, y_next - self.moisture_max)
            cost += 10.0 * cp.square(slack_low)
            cost += 10.0 * cp.square(slack_high)

            y_next_val = (float(np.dot(self.model.A, y_vec)) +
                          float(np.dot(self.model.B, u_vec)) +
                          self.model.offset)
            y_hist.append(y_next_val)
            u_hist.append(0.0)

        problem = cp.Problem(cp.Minimize(cost), constraints)
        problem.solve(solver=cp.OSQP, warm_starting=True, verbose=False)

        if problem.status in ["optimal", "optimal_inaccurate"]:
            u_optimal = float(u.value[0])
            u_optimal = max(self.u_min, min(self.u_max, u_optimal))
            print(f"[MPC] Optimal u* = {u_optimal:.1f} sec | Status: {problem.status}")
            return u_optimal
        else:
            print(f"[MPC] Solver failed: {problem.status}. Defaulting to 0.")
            return 0.0


# ─── Quick Test ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    model = ARXModel()
    mpc   = MPCController(model)

    y_history = [35.0, 34.5, 34.0, 33.5, 33.0]
    u_history = [0.0, 0.0]

    u_star = mpc.compute(y_history, u_history)
    print(f"[MPC] Recommended irrigation: {u_star:.1f} seconds")
    print(f"[MPC] That's {u_star/60:.1f} minutes of irrigation.")
    print("[MPC] Test passed ✓")