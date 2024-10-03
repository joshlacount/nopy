import dataclasses
import datetime
import typing

import colour

from . import dataclass_base

@dataclasses.dataclass
class Badge(dataclass_base.DataclassBase):
    animation_url: str
    icon_url: str
    name: str
    tooltip: str

    def to_json(self) -> dict[str, object]:
        return dataclasses.asdict(self)

@dataclasses.dataclass
class ProfileMode(dataclass_base.DataclassBase):
    name: str

    def to_json(self) -> dict[str, object]:
        return dataclasses.asdict(self)

@dataclasses.dataclass
class Book(dataclass_base.DataclassBase):
    authors: list[str]
    cover_url: str
    description: str
    id: str
    published_date: datetime.date
    publisher: str
    title: str

    @classmethod
    def from_json(cls, json_obj: str | dict[str, typing.Any]) -> typing.Self:
        if type(json_obj) is str:
            json_obj = json.loads(json_obj)
        json_obj["published_date"] = json_obj.pop("publishedDate")
        return super(Book, cls).from_json(json_obj)

    def to_json(self) -> dict[str, typing.Any]:
        ret = super().to_json()
        ret["publishedDate"] = ret.pop("published_date")
        return ret

@dataclasses.dataclass
class Show(dataclass_base.DataclassBase):
    first_air_date: datetime.date
    id: int
    name: str
    overview: str
    poster_url: str
    type: str
    vote_average: float

@dataclasses.dataclass
class Track(dataclass_base.DataclassBase):
    artist: str
    id: str
    image_url: str
    name: str
    preview_url: str

@dataclasses.dataclass
class Status(dataclass_base.DataclassBase):
    book: Book
    created_at: datetime.datetime
    eating: str
    irl: str
    mood: str
    playing: str
    profile_id: str
    show: Show
    track: Track
    updated_at: datetime.datetime

    @classmethod
    def from_json(cls, json_obj: str | dict[str, typing.Any]) -> typing.Self:
        if type(json_obj) is str:
            json_obj = json.loads(json_obj)
        for opt_field in ["book", "eating", "irl", "mood", "playing", "show", "track"]:
            if opt_field not in json_obj:
                json_obj[opt_field] = None
        return super(Status, cls).from_json(json_obj)

@dataclasses.dataclass
class Theme(dataclass_base.DataclassBase):
    background: colour.Color
    box_background_color: colour.Color
    box_corner_radius: float
    box_line_gradient_end: colour.Color
    box_line_gradient_start: colour.Color
    box_line_width: int
    box_secondary_text_color: colour.Color
    box_text_color: colour.Color
    created_at: datetime.datetime
    hide_image_border: bool
    image_corner_radius: float
    image_line_width: int
    level_hidden: bool
    mode_hidden: bool
    profile_id: str
    secondary_text_color: colour.Color
    text_color: colour.Color
    updated_at: datetime.datetime

@dataclasses.dataclass
class Profile(dataclass_base.DataclassBase):
    age: int
    badges: list[Badge]
    bio: str
    birthday: datetime.datetime
    blocked_by_me: bool
    created_at: datetime.datetime
    current_badge: str
    gender: str
    is_connection: bool
    level: int
    muted_by_me: bool
    mutual_connections: list[dict[str, typing.Any]]
    mutual_connections_total_count: int
    nsfw_flag: bool
    onboarding_completed: bool
    profile_id: str
    profile_modes: list[ProfileMode]
    profile_picture_url: str
    sequential_id: int
    status: Status
    streaks: list[str]
    target: str
    theme: Theme
    username: str
    xp: float

