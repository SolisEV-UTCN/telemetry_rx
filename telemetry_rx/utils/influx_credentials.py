from dataclasses import dataclass


@dataclass
class InfluxCreds(object):
    bucket: str = ""
    org: str = ""
    token: str = ""
    url: str = ""

    def as_dict(self) -> dict[str, str]:
        return {
            "bucket": self.bucket,
            "org": self.org,
            "token": self.token,
            "url": self.url,
        }

    def __iter__(self):
        return iter(self.as_dict())