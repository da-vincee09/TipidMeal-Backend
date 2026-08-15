from sklearn.feature_extraction.text import TfidfVectorizer


class MealTfidfEngine:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        self.matrix = None
        self.meals = []

    def fit(self, meals):
        self.meals = meals

        documents = [
            " ".join(
                "_".join(ingredient.ingredient.strip().lower().split())
                for ingredient in meal.ingredients
            )
            for meal in meals
        ]

        self.matrix = self.vectorizer.fit_transform(documents)

        return self.matrix


    def calculate_weighted_ingredient_coverage(
        self,
        meal_index: int,
        available_ingredients: set[str],
    ) -> float:
        if self.matrix is None:
            raise ValueError("TF-IDF engine has not been fitted.")

        feature_names = self.vectorizer.get_feature_names_out()
        meal_vector = self.matrix[meal_index].toarray().flatten()

        total_weight = meal_vector.sum()

        if total_weight == 0:
            return 0.0

        available_weight = sum(
            weight
            for ingredient, weight in zip(feature_names, meal_vector)
            if ingredient in available_ingredients
        )

        return available_weight / total_weight