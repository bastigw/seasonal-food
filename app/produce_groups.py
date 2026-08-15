"""Grocery-style subcategories for produce names, used to group the email
by more than just fruit/vegetable. Keys are the lowercase produce names as
they appear in eufic_seasonal_produce_matrix.json.
"""

VEGETABLE_GROUP_ORDER = [
    "Leafy Greens & Salad",
    "Brassicas & Cabbages",
    "Root & Tuber Vegetables",
    "Alliums",
    "Legumes & Pods",
    "Fruiting Vegetables",
    "Stems & Shoots",
    "Mushrooms & Fungi",
    "Other",
]

FRUIT_GROUP_ORDER = [
    "Pome Fruit",
    "Stone Fruit",
    "Berries",
    "Citrus",
    "Melons",
    "Tropical & Exotic",
    "Other",
]

VEGETABLE_GROUPS = {
    "artichoke": "Stems & Shoots",
    "arugula": "Leafy Greens & Salad",
    "asparagus": "Stems & Shoots",
    "aubergine": "Fruiting Vegetables",
    "batavia lettuce": "Leafy Greens & Salad",
    "bay bolete mushroom": "Mushrooms & Fungi",
    "bean": "Legumes & Pods",
    "beech hat mushroom": "Mushrooms & Fungi",
    "beetle bean": "Legumes & Pods",
    "beetroot": "Root & Tuber Vegetables",
    "bell pepper": "Fruiting Vegetables",
    "black bean": "Legumes & Pods",
    "black eyed pea": "Legumes & Pods",
    "black radish": "Root & Tuber Vegetables",
    "boletus mushroom": "Mushrooms & Fungi",
    "broad bean": "Legumes & Pods",
    "broccoli": "Brassicas & Cabbages",
    "broccolini": "Brassicas & Cabbages",
    "brown bean": "Legumes & Pods",
    "brussels sprout": "Brassicas & Cabbages",
    "butternut squash": "Fruiting Vegetables",
    "cabbage": "Brassicas & Cabbages",
    "cardoon": "Stems & Shoots",
    "carrot": "Root & Tuber Vegetables",
    "catalogna/puntarelle": "Leafy Greens & Salad",
    "cauliflower": "Brassicas & Cabbages",
    "cavolo nero": "Leafy Greens & Salad",
    "celeriac": "Root & Tuber Vegetables",
    "celery": "Stems & Shoots",
    "chanterelle mushroom": "Mushrooms & Fungi",
    "chard": "Leafy Greens & Salad",
    "chayote": "Fruiting Vegetables",
    "chicory": "Leafy Greens & Salad",
    "chili": "Fruiting Vegetables",
    "chinese cabbage": "Brassicas & Cabbages",
    "courgette": "Fruiting Vegetables",
    "cress": "Leafy Greens & Salad",
    "cucumber": "Fruiting Vegetables",
    "curly endive": "Leafy Greens & Salad",
    "emperor mushroom": "Mushrooms & Fungi",
    "endive": "Leafy Greens & Salad",
    "enoki mushroom": "Mushrooms & Fungi",
    "fennel": "Stems & Shoots",
    "fire bean": "Legumes & Pods",
    "frillice lettuce": "Leafy Greens & Salad",
    "frisee lettuce": "Leafy Greens & Salad",
    "friseline": "Leafy Greens & Salad",
    "garden orache": "Leafy Greens & Salad",
    "garden patience": "Leafy Greens & Salad",
    "garlic": "Alliums",
    "gherkin": "Fruiting Vegetables",
    "green amaranth": "Leafy Greens & Salad",
    "green bean": "Legumes & Pods",
    "green bell pepper": "Fruiting Vegetables",
    "haricot bean": "Legumes & Pods",
    "heart of lettuce": "Leafy Greens & Salad",
    "horseradish": "Root & Tuber Vegetables",
    "iceberg lettuce": "Leafy Greens & Salad",
    "jerusalem artichoke": "Root & Tuber Vegetables",
    "kale": "Leafy Greens & Salad",
    "kalette": "Leafy Greens & Salad",
    "kidney bean": "Legumes & Pods",
    "kohlrabi": "Root & Tuber Vegetables",
    "lamb's lettuce": "Leafy Greens & Salad",
    "leek": "Alliums",
    "lettuce": "Leafy Greens & Salad",
    "lollo bionda lettuce": "Leafy Greens & Salad",
    "lollo rosso lettuce": "Leafy Greens & Salad",
    "lovage": "Leafy Greens & Salad",
    "mangetout": "Legumes & Pods",
    "mangold": "Leafy Greens & Salad",
    "marrow": "Fruiting Vegetables",
    "morel": "Mushrooms & Fungi",
    "mushroom": "Mushrooms & Fungi",
    "new potato": "Root & Tuber Vegetables",
    "oak leaf lettuce": "Leafy Greens & Salad",
    "okra": "Fruiting Vegetables",
    "olive": "Other",
    "onion": "Alliums",
    "oxheart cabbage": "Brassicas & Cabbages",
    "oyster mushroom": "Mushrooms & Fungi",
    "pak choi": "Brassicas & Cabbages",
    "parsley root": "Root & Tuber Vegetables",
    "parsnip": "Root & Tuber Vegetables",
    "pea": "Legumes & Pods",
    "pickle": "Fruiting Vegetables",
    "portobello mushroom": "Mushrooms & Fungi",
    "potato": "Root & Tuber Vegetables",
    "pumpkin": "Fruiting Vegetables",
    "purple sprouting broccoli": "Brassicas & Cabbages",
    "purslane": "Leafy Greens & Salad",
    "radicchio": "Leafy Greens & Salad",
    "radish": "Root & Tuber Vegetables",
    "ramson": "Alliums",
    "red cabbage": "Brassicas & Cabbages",
    "red chicory": "Leafy Greens & Salad",
    "red lettuce": "Leafy Greens & Salad",
    "red oak leaf lettuce": "Leafy Greens & Salad",
    "red onion": "Alliums",
    "red radish": "Root & Tuber Vegetables",
    "rhubarb": "Stems & Shoots",
    "romaine lettuce": "Leafy Greens & Salad",
    "romanesco": "Brassicas & Cabbages",
    "rucola": "Leafy Greens & Salad",
    "runner bean": "Legumes & Pods",
    "rutabaga": "Root & Tuber Vegetables",
    "salsify": "Root & Tuber Vegetables",
    "samphire": "Other",
    "savoy cabbage": "Brassicas & Cabbages",
    "scallion": "Alliums",
    "shallot": "Alliums",
    "shiitake mushroom": "Mushrooms & Fungi",
    "snap pea": "Legumes & Pods",
    "snow pea": "Legumes & Pods",
    "sorrel": "Leafy Greens & Salad",
    "soybean": "Legumes & Pods",
    "spinach": "Leafy Greens & Salad",
    "spring onion": "Alliums",
    "squash": "Fruiting Vegetables",
    "summer cabbage": "Brassicas & Cabbages",
    "swede": "Root & Tuber Vegetables",
    "sweet corn": "Fruiting Vegetables",
    "sweet potato": "Root & Tuber Vegetables",
    "swiss chard": "Leafy Greens & Salad",
    "taro": "Root & Tuber Vegetables",
    "tomato": "Fruiting Vegetables",
    "truffle (black)": "Mushrooms & Fungi",
    "truffle (white)": "Mushrooms & Fungi",
    "turnip": "Root & Tuber Vegetables",
    "watercress": "Leafy Greens & Salad",
    "white asparagus": "Stems & Shoots",
    "white bean": "Legumes & Pods",
    "white cabbage": "Brassicas & Cabbages",
    "white radish": "Root & Tuber Vegetables",
    "wild garlic": "Alliums",
    "wild greens": "Leafy Greens & Salad",
    "winter melon": "Fruiting Vegetables",
}

FRUIT_GROUPS = {
    "apple": "Pome Fruit",
    "apricot": "Stone Fruit",
    "autumn apple": "Pome Fruit",
    "avocado": "Tropical & Exotic",
    "banana": "Tropical & Exotic",
    "bilberry": "Berries",
    "black rowan": "Berries",
    "blackberry": "Berries",
    "blackcurrant": "Berries",
    "blackthorn": "Berries",
    "blood orange": "Citrus",
    "blue honeysuckle berry": "Berries",
    "blueberry": "Berries",
    "bramley apple": "Pome Fruit",
    "carob": "Tropical & Exotic",
    "cherry": "Stone Fruit",
    "cherry plum": "Stone Fruit",
    "chokeberry": "Berries",
    "citrus": "Citrus",
    "clementine": "Citrus",
    "cloudberry": "Berries",
    "crab apple": "Pome Fruit",
    "cranberry": "Berries",
    "custard apple": "Tropical & Exotic",
    "donut peach": "Stone Fruit",
    "elderberry": "Berries",
    "fig": "Tropical & Exotic",
    "gooseberry": "Berries",
    "grape": "Other",
    "grapefruit": "Citrus",
    "greengage": "Stone Fruit",
    "guava": "Tropical & Exotic",
    "jujube": "Tropical & Exotic",
    "kiwi": "Tropical & Exotic",
    "lemon": "Citrus",
    "lingonberry": "Berries",
    "loganberry": "Berries",
    "loquat": "Other",
    "mandarin": "Citrus",
    "mango": "Tropical & Exotic",
    "mantores tangerine": "Citrus",
    "medlar": "Pome Fruit",
    "melon": "Melons",
    "mirabelle plum": "Stone Fruit",
    "mulberry": "Berries",
    "muskmelon": "Melons",
    "nectarine": "Stone Fruit",
    "orange": "Citrus",
    "papaya": "Tropical & Exotic",
    "peach": "Stone Fruit",
    "pear": "Pome Fruit",
    "persimmon": "Tropical & Exotic",
    "pineapple": "Tropical & Exotic",
    "plum": "Stone Fruit",
    "pomegranate": "Tropical & Exotic",
    "pomelo": "Citrus",
    "prickly pear": "Tropical & Exotic",
    "prune": "Stone Fruit",
    "quince": "Pome Fruit",
    "raspberry": "Berries",
    "red berry": "Berries",
    "redcurrant": "Berries",
    "sea buckthorn": "Berries",
    "strawberry": "Berries",
    "summer apple": "Pome Fruit",
    "summer orange": "Citrus",
    "tangerine": "Citrus",
    "tayberry": "Berries",
    "watermelon": "Melons",
    "white currant": "Berries",
    "white mulberry": "Berries",
    "winter apple": "Pome Fruit",
}

GROUP_ORDER = {
    "vegetable": VEGETABLE_GROUP_ORDER,
    "fruit": FRUIT_GROUP_ORDER,
}


def group_for(name: str, category: str) -> str:
    groups = VEGETABLE_GROUPS if category == "vegetable" else FRUIT_GROUPS
    return groups.get(name, "Other")


# One icon per subcategory, used as a fallback when an item has no more
# specific icon of its own (see *_ICON_OVERRIDES below).
VEGETABLE_GROUP_ICONS = {
    "Leafy Greens & Salad": "\U0001F96C",  # leafy green
    "Brassicas & Cabbages": "\U0001F966",  # broccoli
    "Root & Tuber Vegetables": "\U0001F955",  # carrot
    "Alliums": "\U0001F9C5",  # onion
    "Legumes & Pods": "\U0001FAD8",  # beans
    "Fruiting Vegetables": "\U0001F345",  # tomato
    "Stems & Shoots": "\U0001F331",  # seedling
    "Mushrooms & Fungi": "\U0001F344",  # mushroom
    "Other": "\U0001F33F",  # herb
}

FRUIT_GROUP_ICONS = {
    "Pome Fruit": "\U0001F34E",  # red apple
    "Stone Fruit": "\U0001F351",  # peach
    "Berries": "\U0001FAD0",  # blueberries
    "Citrus": "\U0001F34A",  # tangerine
    "Melons": "\U0001F348",  # melon
    "Tropical & Exotic": "\U0001F96D",  # mango
    "Other": "\U0001F347",  # grapes
}

GROUP_ICONS = {
    "vegetable": VEGETABLE_GROUP_ICONS,
    "fruit": FRUIT_GROUP_ICONS,
}

# Specific icons for items that have a well-known emoji of their own,
# distinct enough from their group's default to be worth calling out
# (e.g. potato vs. carrot within Root & Tuber Vegetables).
VEGETABLE_ICON_OVERRIDES = {
    "aubergine": "\U0001F346",  # eggplant
    "bell pepper": "\U0001FAD1",  # bell pepper
    "green bell pepper": "\U0001FAD1",
    "potato": "\U0001F954",  # potato
    "new potato": "\U0001F954",
    "sweet potato": "\U0001F954",
    "taro": "\U0001F954",
    "garlic": "\U0001F9C4",  # garlic
    "wild garlic": "\U0001F9C4",
    "ramson": "\U0001F9C4",
    "pea": "\U0001FADB",  # pea pod
    "snap pea": "\U0001FADB",
    "snow pea": "\U0001FADB",
    "mangetout": "\U0001FADB",
    "black eyed pea": "\U0001FADB",
    "cucumber": "\U0001F952",  # cucumber
    "gherkin": "\U0001F952",
    "pickle": "\U0001F952",
    "chayote": "\U0001F952",
    "courgette": "\U0001F952",
    "chili": "🌶",  # hot pepper
    "pumpkin": "\U0001F383",  # jack-o-lantern
    "squash": "\U0001F383",
    "butternut squash": "\U0001F383",
    "marrow": "\U0001F383",
    "sweet corn": "\U0001F33D",  # corn
    "cabbage": "\U0001F96C",
    "chinese cabbage": "\U0001F96C",
    "oxheart cabbage": "\U0001F96C",
    "red cabbage": "\U0001F96C",
    "savoy cabbage": "\U0001F96C",
    "summer cabbage": "\U0001F96C",
    "white cabbage": "\U0001F96C",
    "brussels sprout": "\U0001F96C",
    "pak choi": "\U0001F96C",
    "olive": "\U0001FAD2",  # olive
}

FRUIT_ICON_OVERRIDES = {
    "pear": "\U0001F350",  # pear
    "quince": "\U0001F350",
    "medlar": "\U0001F350",
    "cherry": "\U0001F352",  # cherries
    "cherry plum": "\U0001F352",
    "strawberry": "\U0001F353",  # strawberry
    "lemon": "\U0001F34B",  # lemon
    "watermelon": "\U0001F349",  # watermelon
    "banana": "\U0001F34C",  # banana
    "avocado": "\U0001F951",  # avocado
    "kiwi": "\U0001F95D",  # kiwi fruit
    "pineapple": "\U0001F34D",  # pineapple
}

ICON_OVERRIDES = {
    "vegetable": VEGETABLE_ICON_OVERRIDES,
    "fruit": FRUIT_ICON_OVERRIDES,
}


def icon_for(name: str, category: str) -> str:
    overrides = ICON_OVERRIDES["vegetable" if category == "vegetable" else "fruit"]
    if name in overrides:
        return overrides[name]
    return GROUP_ICONS[category][group_for(name, category)]
