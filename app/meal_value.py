"""
returns a value score 0-100 (higher = more bang for your buck ), and it's gonna adjust to missing macros
required to work: price (in same currency), kcal, satiety_score(1-10).
don't need it but use if have: protein_g, fiber_g, sugar_g, fat_g, micronutrient_index (0-1).
"""
def meal_value_score(price, kcal, satiety_score,
                     protein_g=None, fiber_g=None,
                     sugar_g=None, fat_g=None,
                     micronutrient_index=None,
                     weight_g=None,
                     # tuning weights (sum not required; function normalizes)
                     w_cost=0.25, w_satiety=0.30, w_protein=0.20,
                     w_nutrient=0.15, w_penalty=0.10,
                     # sensible defaults / caps
                     max_kcal_per_dollar=2000.0,
                     max_satiety_per_dollar=40.0,
                     max_protein_per_dollar=200.0):


    # basic guards
    if price is None or price <= 0:
        raise ValueError("price must be > 0")
    if kcal is None or kcal <= 0:
        raise ValueError("kcal must be > 0")
    if satiety_score is None:
        satiety_score = 5.0

    # cost/calorie (higher score the better, more food for less money)
    kcal_per_dollar = kcal / price
    # normalize to 0-1 with a reasonable cap
    cost_score = min(kcal_per_dollar / max_kcal_per_dollar, 1.0)

    # satiety per dollar (more is better)
    sat_per_dollar = satiety_score / price
    sat_score = min(sat_per_dollar / max_satiety_per_dollar, 1.0)

    # protein per dollar (veryyyyyy important for the gains)
    # if missing, it's gonna estimate protein based on kcal (usually like 10-15% kcal from protein ~ 0.04 g/kcal)
    if protein_g is None:
        protein_g = kcal * 0.04  # default 4 g protein per 100 kcal (tunable but lowkey this is fine)
    protein_per_dollar = protein_g / price
    protein_score = min(protein_per_dollar / max_protein_per_dollar, 1.0)

    # mutrient density
    # if a micronutrient_index provided (0-1), prefer it. otherwise we're gonna use fiber & sugar heuristics.
    if micronutrient_index is not None:
        nutrient_score = max(0.0, min(1.0, micronutrient_index))
    else:
        # use fiber per 100 kcal and sugar penalty as rough proxy
        fiber_p100 = (fiber_g / kcal * 100.0) if (fiber_g is not None) else 1.0
        sugar_p100 = (sugar_g / kcal * 100.0) if (sugar_g is not None) else 3.0
        # map fiber_p100 to 0-1 (0-6 g/100kcal common range)
        fiber_score = min(fiber_p100 / 6.0, 1.0)
        # sugar penalty mapped so high sugar lowers nutrient score
        sugar_pen = min(sugar_p100 / 12.0, 1.0)  # 12 g/100kcal is high :(
        nutrient_score = max(0.0, fiber_score * (1.0 - 0.6 * sugar_pen))

    # penalize the not so good stufffff (processed / high sugar / energy density) 
    # produce a penalty score 0-1 where higher means worse (we convert to a component that reduces value)
    penalty = 0.0
    # sugar penalty :(
    if sugar_g is not None:
        sugar_p100 = sugar_g / kcal * 100.0
        if sugar_p100 > 8.0:
            penalty += min((sugar_p100 - 8.0) / 12.0, 1.0) * 0.6
    # excessive fat proportion penalty (optional)
    if fat_g is not None:
        fat_p100 = fat_g / kcal * 100.0
        if fat_p100 > 20.0:
            penalty += min((fat_p100 - 20.0) / 40.0, 1.0) * 0.4

    penalty = min(penalty, 1.0)
    penalty_score = 1.0 - penalty  # higher is better (1 means no penalty it's supa healthy)

    # combine the individual componetns (weighted) & normalize the weights
    total_w = w_cost + w_satiety + w_protein + w_nutrient + w_penalty
    w_cost /= total_w
    w_satiety /= total_w
    w_protein /= total_w
    w_nutrient /= total_w
    w_penalty /= total_w

    combined = (w_cost * cost_score
                + w_satiety * sat_score
                + w_protein * protein_score
                + w_nutrient * nutrient_score
                + w_penalty * penalty_score)

    # scale 0-1 to 0-100
    value_0_100 = round(combined * 100.0, 2)
    return value_0_100