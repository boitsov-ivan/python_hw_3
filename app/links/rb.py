class RBLink:
    def __init__(self,
                 id_user: int | None = None,
                 original_URL: str | None = None,
                 short_URL: str | None = None):
        self.id_user = id_user
        self.original_URL = original_URL
        self.short_URL = short_URL

    def to_dict(self) -> dict:
        data = {'id_user': self.id_user, 'original_URL': self.original_URL, 'short_URL': self.short_URL}
        # Создаем копию словаря, чтобы избежать изменения словаря во время итерации
        filtered_data = {key: value for key, value in data.items() if value is not None}
        return filtered_data

