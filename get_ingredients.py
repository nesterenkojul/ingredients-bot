from bs4 import BeautifulSoup
from copy import deepcopy
import requests
from database import Ingredients, session
from db_tracker import Recipes, tracker_session
from random import randint
import re


def parse_ingredient_list(recipe_id):
    stopwords = ('cut', 'inch', 'salt', 'water', 'baking', 'soda', 'temperature', 'yeast', 'or', 'and', 'well', 'for',
                 'in', 'but', 'topping', 'color', 'coloring', 'beverage', 'according', 'ice', 'mix', 'tartar', 'spray',
                 'plastic', 'substitute')
    extrawords = ('ground', 'fresh', 'large', 'taste', 'nonfat', 'solid-pack', 'whole', 'miniature', 'mini',
                  'extra', 'big', 'small', 'dry', 'hot', 'cold', 'fat-free', 'halves', 'breast', 'thigh', 'roma',
                  'seasoning', 'torn', 'clove', 'ripe', 'extract', 'fat', 'free', 'piec', 'the', 'pinch', 'floret',
                  'chunk', 'your', 'choice', 'light', 'dog', 'toothpick', 'eagle', 'liquid', 'halv', 'plain', 'slic',
                  'coarse', 'fine', 'sea', 'rib', 'smith', 'ready', 'light', 'dark', 'minute', 'white', 'black',
                  'fruit', 'vegetabl', 'creamy', 'original', 'kraft', 'gold', 'swis', 'with', 'some', 'giorno',
                  'philadelphia', 'soft', 'hard', 'young', 'flavor', 'flavour', 'layer', 'strip', 'pod', 'calorie',
                  'tart', 'crispy', 'peel', 'juice', 'pure', 'leav', 'such', 'russet', 'thin', 'thick', 'squares',
                  'top', 'skewer', 'stem', 'cube', 'sweet', 'savory', 'leaves', 'zest', 'cooking', 'imitation',
                  'artificial', 'chunky', 'cocktail', 'root', 'yellow', 'red', 'green', 'curl', 'stick', 'real',
                  'lowfat', 'warm', 'smooth', 'solid', 'pack', 'puree', 'split', 'food', 'boiling', 'stew', 'strong',
                  'into', 'without', 'wide', 'spears', 'rind', 'round', 'square', 'grill', 'crunchy', 'creamy', 'fine',
                  'superfine', 'wing', 'chil', 'jumbo', 'kernel', 'style', 'bit', 'sodium', 'low', 'high', 'gluten',
                  'vegan', 'dairy', 'vegetarian', 'keto', 'paleo', 'spear', 'sodium', 'meat', 'leg', 'wing', 'nut',
                  'garnish', 'select', 'sprig', 'skim', 'select', 'old', 'tiny', 'premium', 'made', 'from')
    s_complications = ('dates', 'oats', 'clams', 'capers', 'olives', 'peas', 'preserves', 'apples', 'molasses',
                       'cloves', 'noodles', 'crumbs', 'cookies', 'cornflakes', 'flakes', 'whites', 'chives', 'couscous',
                       'hummus', 'grapes', 'sprinkles', 'pickles', 'asparagus', 'prunes')

    try:
        r = requests.get(f"https://www.allrecipes.com/recipe/{recipe_id}/")
        page = BeautifulSoup(r.text, 'html.parser')
        ingredients = page.findAll('div')[-14].attrs['data-recipe_food_main_ingredients'].split(',')
        filtered_ingredients = []

        for ing in ingredients:
            accepted_words = []
            ing = ing.split()
            for word in ing:
                word = word.strip().lower()
                if word in stopwords:
                    accepted_words = []
                    break
                if word not in s_complications:
                    if word[-3:] == 'ies':
                        word = word[:-3] + 'y'
                    if word[-2:] == 'es':
                        word = word[:-2]
                    if word[-1] == 's':
                        word = word[:-1]
                if word in extrawords or re.match(r".*ed", word) or re.match(r".*an", word) or re.match(r".*en", word) \
                        or re.match(r".*ly", word) or re.match(r".*®", word) or re.match(r".*les", word) or \
                        re.match(r".*™", word) or not word.isalpha() or len(word) < 3:
                    continue
                accepted_words.append(word)

            if accepted_words:
                accepted_ingredient = ' '.join(accepted_words)
                l = accepted_ingredient.find('(')
                if l != -1:
                    accepted_ingredient = accepted_ingredient[:l - 1]

                filtered_ingredients.append(accepted_ingredient)

        return filtered_ingredients

    except Exception as e:
        if e is ConnectionError:
            return "ConErr"
        return None


def update_database(recipe_id):
    ingredient_list = parse_ingredient_list(recipe_id)
    if not ingredient_list:
        return None
    if ingredient_list == "ConErr":
        return "ConErr"
    s = session()
    for ing in ingredient_list:
        pairs = deepcopy(ingredient_list)
        pairs.remove(ing)
        for pair in pairs:
            record = s.query(Ingredients).filter((Ingredients.ingredient == ing) & (Ingredients.pairing == pair)).first()
            if record is None:
                data = Ingredients(ingredient=ing, pairing=pair, count=1)
                s.add(data)
            else:
                record.count += 1
                s.add(record)
    s.commit()
    print(f"Added {len(ingredient_list)} new ingredients!")
    return 'OK'


def get_new_recipes(quantity):
    s = tracker_session()
    k = 0
    all = 0
    while k < quantity and all < 10**3:
        id = randint(6700, 80000)
        record = s.query(Recipes).filter((Recipes.recipe_page == id)).first()
        if record is None:
            all += 1
            data = Recipes(recipe_page=id)
            s.add(data)
            result = update_database(id)
            if result == "ConErr":
                print("Connection Error! Shutting down.")
                break
            if result:
                k += 1
        else:
            all += 1
    s.commit()
    print(f"Browsed {k} new recipes!")


if __name__ == "__main__":
    get_new_recipes(10)
