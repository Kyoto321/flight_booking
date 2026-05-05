class BaseProvider:
    name = "base"

    def search(self, payload):
        raise NotImplementedError("Provider must implement search method")