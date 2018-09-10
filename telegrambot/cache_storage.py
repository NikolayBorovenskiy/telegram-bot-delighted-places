import redis
import json
from django.conf import settings

TITLE, LOCATION, PHOTO, CONFIRMATION = range(4)


class UserPlace:
    redis = None
    expire_time = 60 * 20
    user_state_key = "user:state:{user_id}"
    user_data_key = "user:data:{user_id}"

    def __init__(self):
        self.redis = redis.from_url(settings.REDIS_URL)

    def update_user_state(self, user_id, state):
        key = self.user_state_key.format(user_id=user_id)
        self.redis.set(key, state, ex=self.expire_time)

    def get_user_state(self, user_id):
        key = self.user_state_key.format(user_id=user_id)
        if not self.redis.exists(key):
            return None
        return int(self.redis.get(key).decode("utf-8"))

    def update_user_data(self, user_id, data):
        key = self.user_data_key.format(user_id=user_id)
        self.redis.rpush(key, data)

    def get_user_data(self, user_id):
        key = self.user_data_key.format(user_id=user_id)
        raw_data = self.redis.lrange(key, 0, -1)
        title_, location_, photo_name_, photo_ = raw_data
        title = title_.decode("utf-8")
        location = json.loads(location_.decode("utf-8"))
        photo_name = photo_name_.decode("utf-8")

        return title, location, photo_name, photo_

    def reset_user(self, user_id):
        state_key = self.user_state_key.format(user_id=user_id)
        data_key = self.user_data_key.format(user_id=user_id)
        self.redis.delete(state_key, data_key)


user_place = UserPlace()
