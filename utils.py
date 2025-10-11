from models import Category

def summarize_categories(categories: list[Category]):
    summary = {}
    for c in categories:
        summary[c.name] = [f.name for f in c.foods]
    return summary