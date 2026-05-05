# app/services/food_entry_factory.py
from app.constants import ENTRY_SIMPLE, ENTRY_MACRO, MSG_INVALID_ENTRY_TYPE


class IFoodEntry:
    """Base class for all food entries."""

    def get_calories(self):
        raise NotImplementedError("Subclasses must implement get_calories()")


class SimpleFoodEntry(IFoodEntry):
    """User enters total calories directly."""

    def __init__(self, calories):
        self.calories = float(calories)

    def get_calories(self):
        return self.calories


class MacroFoodEntry(IFoodEntry):
    """Calories calculated from protein, carbs and fat."""

    def __init__(self, protein, carbs, fat):
        self.protein = float(protein)
        self.carbs = float(carbs)
        self.fat = float(fat)

    def get_calories(self):
        return (self.protein * 4) + (self.carbs * 4) + (self.fat * 9)


class FoodEntryFactory:
    """Factory that creates the correct FoodEntry based on type."""

    @staticmethod
    def create(entry_type, **kwargs):
        if entry_type == ENTRY_SIMPLE:
            return SimpleFoodEntry(calories=kwargs["calories"])
        elif entry_type == ENTRY_MACRO:
            return MacroFoodEntry(
                protein=kwargs["protein"],
                carbs=kwargs["carbs"],
                fat=kwargs["fat"]
            )
        else:
            raise ValueError(MSG_INVALID_ENTRY_TYPE)