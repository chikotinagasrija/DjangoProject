from locust import HttpUser, task, between


class NearbyDriverUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def nearby_drivers(self):
        self.client.get(
            "/api/v1/rides/nearby-drivers/"
        )