import os
import streamlit as st

from openai import OpenAI
if "recipe_md" not in st.session_state:
    st.session_state.recipe_md = ""


api_key = os.getenv("OPENAI_API_KEY")

# Fail fast if the key is missing (clear error for you)
if not api_key:
    raise RuntimeError("OPENAI_API_KEY is missing. Put it into .env as: OPENAI_API_KEY=sk-...")

client = OpenAI(api_key=api_key)

# -----------------------------
# Ingredient categorization map
# -----------------------------
INGREDIENT_CATEGORIES = {
    "chicken": "protein",
    "beef": "protein",
    "eggs": "protein",
    "tofu": "protein",

    "rice": "carb",
    "pasta": "carb",
    "potatoes": "carb",
    "bread": "carb",

    "broccoli": "veggie",
    "carrot": "veggie",
    "onion": "veggie",
    "tomato": "veggie",

    "soy sauce": "sauce",
    "garlic": "spice",
    "olive oil": "fat",
}

def categorize_ingredients(ingredients):
    categorized = {
        "protein": [],
        "carb": [],
        "veggie": [],
        "sauce": [],
        "spice": [],
        "fat": [],
        "other": []
    }
    for item in ingredients:
        category = INGREDIENT_CATEGORIES.get(item, "other")
        categorized[category].append(item)
    return categorized

def decide_dish_type(categorized):
    if categorized["protein"] and categorized["carb"]:
        return "Main dish"
    if categorized["veggie"] and not categorized["carb"]:
        return "Salad"
    return "Snack"

def build_summary(categorized, dish_type):
    counts = {k: len(v) for k, v in categorized.items()}
    key_line = (
        f"Detected: {counts['protein']} protein, {counts['carb']} carb, "
        f"{counts['veggie']} veggie, {counts['sauce']} sauce"
    )

    if dish_type == "Main dish":
        interpretation = "You have the core components for a complete main dish."
    elif dish_type == "Salad":
        interpretation = "This looks best as a salad or a cold veggie-based dish."
    else:
        interpretation = "This looks best as a snack, side dish, or a simple plate."

    return key_line, interpretation

def build_prompt(ingredients, categorized, dish_type, mode, style, servings):
    ingredients_list = ", ".join(ingredients)

    return f"""
You are GastroGuide AI, a practical cooking assistant.

STRICT RULES (must follow):
- Use ONLY these user ingredients: {ingredients_list}
- You may add ONLY: salt, pepper, water, oil.
- Never refer to package instructions. Always describe steps explicitly.
- Keep it aligned with Mode = {mode} and Style = {style}.
- Output must be in English.
- Output must be concise and realistic.
- Target servings: {servings}
- Use g and kg instead of pounds
- Oil is considered a basic kitchen ingredient and may be used when appropriate.


OUTPUT FORMAT (Markdown exactly):
## Title
(one line)

## Ingredients
- ingredient — quantity (scaled for {servings} servings)

## Steps
1. ...
2. ...
3. ...

## Nutrition (estimate)
- Calories per serving: ___ kcal
- Protein per serving: ___ g

## Tips
- 1–3 short tips
"""


def generate_recipe(prompt):
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.6,
    )
    return resp.choices[0].message.content


# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="GastroGuide AI", page_icon="🍳", layout="wide")
st.set_page_config(page_title="GastroGuide AI", page_icon="🍳", layout="wide")

st.markdown("""
<style>
.stApp {
  background: radial-gradient(circle at top, #0b1220, #020617);
}

.block-container {
  padding-top: 2rem;
  padding-bottom: 2rem;
}

.gg-card {
  background: rgba(2, 6, 23, 0.75);
  border: 1px solid rgba(148, 163, 184, 0.18);
  border-radius: 18px;
  padding: 18px;
  margin-top: 12px;
}

button[kind="primary"] {
  border-radius: 12px !important;
  font-weight: 650 !important;
}

input, textarea {
  border-radius: 12px !important;
}

div[data-baseweb="select"] > div {
  border-radius: 12px !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
/* page */
.stApp {
  background: radial-gradient(circle at top, #0b1220, #020617);
}

/* main container width */
.block-container {
  padding-top: 2rem;
  padding-bottom: 2rem;
}

/* cards */
.gg-card {
  background: rgba(2, 6, 23, 0.75);
  border: 1px solid rgba(148, 163, 184, 0.18);
  border-radius: 18px;
  padding: 18px 18px;
  margin-top: 12px;
  backdrop-filter: blur(6px);
}

/* buttons */
button[kind="primary"] {
  border-radius: 12px !important;
  font-weight: 650 !important;
}

/* inputs */
input, textarea {
  border-radius: 12px !important;
}
div[data-baseweb="select"] > div {
  border-radius: 12px !important;
}

/* headings */
h1, h2, h3 {
  letter-spacing: -0.02em;
}
</style>
""", unsafe_allow_html=True)

st.markdown(
    """
    <style>
    /* Page background */
    .stApp {
        background: radial-gradient(circle at top, #0f172a, #020617);
        color: #e5e7eb;
    }

    /* Titles */
    h1, h2, h3 {
        font-family: "Inter", sans-serif;
        letter-spacing: -0.02em;
    }

    /* Input fields */
    input, textarea {
        background-color: #020617 !important;
        border: 1px solid #1e293b !important;
        border-radius: 8px !important;
    }

    /* Select boxes */
    div[data-baseweb="select"] > div {
        background-color: #020617 !important;
        border-radius: 8px !important;
        border: 1px solid #1e293b !important;
    }

    /* Buttons */
    button[kind="primary"] {
        background: linear-gradient(135deg, #6366f1, #22d3ee);
        color: black;
        border-radius: 10px;
        font-weight: 600;
        padding: 0.6em 1.2em;
    }

    /* Info boxes */
    .stAlert {
        border-radius: 12px;
        background-color: #020617;
        border: 1px solid #1e293b;
    }

    /* Recipe block spacing */
    section[data-testid="stMarkdownContainer"] {
        line-height: 1.6;
    }
    </style>
    """,
    unsafe_allow_html=True
)


left, right = st.columns([1, 1], gap="large")

with left:
    st.title("GastroGuide AI")
    st.write("Generate a recipe from the ingredients you have.")

    ingredients_input = st.text_input(
        "Ingredients (comma-separated)",
        placeholder="e.g. chicken, rice, broccoli, soy sauce",
    )

    mode = st.selectbox(
        "Mode",
        [
            "Quick",
            "Budget",
            "Diet-friendly",
            "Student-friendly",
            "High-protein",
            "Meal prep",
            "One-pan / minimal dishes",
            "Low-calorie",
        ],
    )

    style = st.selectbox(
        "Style",
        [
            "Home-style",
            "Asian",
            "Mediterranean",
            "Italian",
            "Mexican",
            "Indian-inspired",
            "Healthy / light",
            "Comfort food",
            "Georgian",
        ],
    )

    
        
    

    
      
    

    servings = st.number_input("Servings", min_value=1, max_value=8, value=2, step=1, key="servings_input",)
    show_debug = st.checkbox("Show debug details", key="debug_checkbox")
    generate = st.button(
        "Generate recipe",
        type="primary",
    )



    

    



    
with right:
    st.markdown("## Output")

    # show previous/generated recipe (if exists)
    if st.session_state.recipe_md:
        with st.expander("Show recipe", expanded=True):
            st.markdown(st.session_state.recipe_md)

    # generate on button click
    if generate:
        if ingredients_input.strip() == "":
            st.error("Please enter at least one ingredient.")
        else:
            ingredients = [i.strip().lower() for i in ingredients_input.split(",") if i.strip()]
            categorized = categorize_ingredients(ingredients)
            dish_type = decide_dish_type(categorized)
            key_line, interpretation = build_summary(categorized, dish_type)

            prompt = build_prompt(ingredients, categorized, dish_type, mode, style, servings)

            with st.spinner("Generating recipe with AI..."):
                st.session_state.recipe_md = generate_recipe(prompt)

            # show freshly generated recipe
            with st.expander("Show recipe", expanded=True):
                st.markdown(st.session_state.recipe_md)

            if show_debug:
                with st.expander("🧠 Analysis", expanded=True):
                    st.info(key_line)
                    st.write(f"**Dish type:** {dish_type}")
                    st.write(interpretation)
                    st.json(categorized)



      




