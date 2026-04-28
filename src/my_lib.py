import numpy as np

class ManualKMeans:
    def __init__(self, n_clusters=3, max_iter=300, tol=1e-4, init='random', random_state=None):
        self.n_clusters = n_clusters
        self.max_iter = max_iter
        self.tol = tol
        self.init = init
        self.random_state = random_state
        self.centroids = None
        self.labels = None
        self.inertia_ = 0
        self.n_iter_ = 0

    def fit(self, X):
        if self.random_state is not None:
            np.random.seed(self.random_state)

        n_samples, n_features = X.shape

        if self.init == 'k-means++':
            self.centroids = [X[np.random.randint(n_samples)]]
            for _ in range(1, self.n_clusters):
                dists_sq = np.array([min([np.sum((x - c)**2) for c in self.centroids]) for x in X])
                probs = dists_sq / dists_sq.sum()
                cumulative_probs = probs.cumsum()
                r = np.random.rand()
                
                for i, p in enumerate(cumulative_probs):
                    if r < p:
                        self.centroids.append(X[i])
                        break
            self.centroids = np.array(self.centroids)
        else:
            random_indices = np.random.permutation(n_samples)[:self.n_clusters]
            self.centroids = X[random_indices]

        for i in range(self.max_iter):
            self.n_iter_ = i
            distances = np.sqrt(((X - self.centroids[:, np.newaxis])**2).sum(axis=2))
            self.labels = np.argmin(distances, axis=0)
            new_centroids = np.array([X[self.labels == k].mean(axis=0) for k in range(self.n_clusters)])
            
            for k in range(self.n_clusters):
                if np.isnan(new_centroids[k]).any():
                    new_centroids[k] = X[np.random.randint(n_samples)]

            shift = np.sum((self.centroids - new_centroids)**2)
            if shift < self.tol:
                break
            self.centroids = new_centroids

        final_dists = np.sqrt(((X - self.centroids[:, np.newaxis])**2).sum(axis=2))
        min_dists = np.min(final_dists, axis=0)
        self.inertia_ = np.sum(min_dists ** 2)

class ManualDBSCAN:
    def __init__(self, eps=0.5, min_samples=5):
        self.eps = eps
        self.min_samples = min_samples
        self.labels_ = None
        self.n_clusters_ = 0
        self.n_noise_ = 0

    def fit(self, X):
        n_samples = X.shape[0]
        self.labels_ = np.full(n_samples, -1)
        cluster_id = 0

        for i in range(n_samples):
            if self.labels_[i] != -1:
                continue

            neighbors = self._region_query(X, i)

            if len(neighbors) < self.min_samples:
                self.labels_[i] = -1
            else:
                self._expand_cluster(X, i, neighbors, cluster_id)
                cluster_id += 1

        self.n_clusters_ = cluster_id
        self.n_noise_ = list(self.labels_).count(-1)

    def _expand_cluster(self, X, point_idx, neighbors, cluster_id):
        self.labels_[point_idx] = cluster_id
        i = 0
        while i < len(neighbors):
            neighbor_idx = neighbors[i]
            if self.labels_[neighbor_idx] == -1:
                self.labels_[neighbor_idx] = cluster_id
            
            current_point_neighbors = self._region_query(X, neighbor_idx)
            if len(current_point_neighbors) >= self.min_samples:
                for n in current_point_neighbors:
                    if n not in neighbors:
                        neighbors.append(n)
            
            if self.labels_[neighbor_idx] == -1:
                 self.labels_[neighbor_idx] = cluster_id
            i += 1

    def _region_query(self, X, point_idx):
        distances = np.sqrt(np.sum((X - X[point_idx])**2, axis=1))
        return np.where(distances <= self.eps)[0].tolist()