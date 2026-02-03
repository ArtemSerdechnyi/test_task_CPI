from pydantic import BaseModel


class CpiPeriod(BaseModel):
    year: int
    month: int

    def __hash__(self) -> int:
        return hash((self.year, self.month))
