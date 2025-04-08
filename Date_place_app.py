import streamlit as st
import requests
import time

# ❗ MUST BE FIRST STREAMLIT COMMAND
st.set_page_config(page_title="Date Recommender", page_icon="🍽️")

# Google API Key
GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]

# Indian Cities
INDIAN_CITIES = [
    "Mumbai", "Delhi", "Bangalore", "Chennai", "Hyderabad", "Kolkata",
    "Goa", "Jaipur", "Pune", "Ahmedabad", "Chandigarh", "Kochi",
    "Lucknow", "Indore", "Vadodara"
]

# --- CSS Styling ---
st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
        }
        .restaurant-card {
            border-radius: 12px;
            padding: 16px;
            background-color: #8391a1;
            box-shadow: 0 4px 12px rgba(0,0,0,0.5);
            margin-bottom: 20px;
            height: 400px;
            overflow: hidden;
        }
        .restaurant-card img {
            border-radius: 8px;
            object-fit: cover;
            height: 180px;
            width: 100%;
            margin-bottom: 10px;
        }
        .restaurant-card h4 {
            font-size: 18px;
            font-weight: 600;
            margin: 5px 0 8px 0;
        }
        .restaurant-card p {
            margin: 4px 0;
            font-size: 14px;
            color: #333;
        }
        .restaurant-card a {
            color: #e91e63;
            text-decoration: none;
            font-weight: bold;
            font-size: 14px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Function to get restaurants ---
def get_restaurants(location, cuisine, price_level, min_rating, type_of_place):
    base_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"

    all_results = []
    params = {
        "query": f"{cuisine} {type_of_place} restaurants in {location}",
        "key": GOOGLE_API_KEY
    }

    for _ in range(3):  # Max 3 pages
        response = requests.get(base_url, params=params)
        data = response.json()
        results = data.get("results", [])
        all_results.extend(results)

        next_token = data.get("next_page_token")
        if not next_token:
            break
        time.sleep(2)  # Google delay
        params = {
            "pagetoken": next_token,
            "key": GOOGLE_API_KEY
        }

    filtered_restaurants = [
        r for r in all_results
        if r.get("rating", 0) >= min_rating and r.get("price_level") == price_level
    ]

    return filtered_restaurants

# --- Streamlit UI ---
st.title("🍽️ Date Recommender")
st.markdown("Find the perfect restaurant for your next date 💕")

with st.sidebar:
    st.header("🔍 Search Filters")
    location = st.selectbox("📍 Select City", INDIAN_CITIES)
    cuisine = st.selectbox(
    "🍴 Cuisine Type", 
    [
        "Desserts", "Indian", "Italian", "Punjabi", "Gujarati", "South Indian", "Chinese", "Mexican", "Japanese",
        "American", "Thai", "Mediterranean", "Continental", "French",
        "Middle Eastern", "Korean", "Greek", "Spanish", "Multi-Cuisine"
    ]
    )
    
    type_of_place = st.selectbox(
    "What type of place are you looking for", 
    [
        "Restaurant", "Cafe", "Dessert Place", "Bakery", "Fast Food", "Road Side", "Brewpub"
    ]
    )

    budget_option = st.selectbox(
        "💰 Budget per Person (Approx)",
        ["₹ (Under ₹200)", "₹₹ (₹200–₹500)", "₹₹₹ (₹500–₹1000)", "₹₹₹₹ (₹1000+)"]
    )
    budget_map = {
        "₹ (Under ₹200)": 1,
        "₹₹ (₹200–₹500)": 2,
        "₹₹₹ (₹500–₹1000)": 3,
        "₹₹₹₹ (₹1000+)": 4
    }
    price_level = budget_map[budget_option]
    min_rating = st.slider("⭐ Minimum Rating", 1.0, 5.0, 4.0, step=0.1)

if "restaurants" not in st.session_state:
    st.session_state.restaurants = []
if "visible_count" not in st.session_state:
    st.session_state.visible_count = 6


if st.button("Search Restaurants 🚀"):
    with st.spinner("Fetching delicious options..."):
        results = get_restaurants(location, cuisine, price_level, min_rating, type_of_place)

    if results:
        st.success(f"Found {len(results)} options!")
        st.session_state.restaurants = results
        st.session_state.visible_count = 6
    else:
        st.warning("No matching restaurants found. Try adjusting your filters!")
        st.session_state.restaurants = []
        st.session_state.visible_count = 6

# ✅ Always render restaurant cards if any are in session_state
restaurants_to_show = st.session_state.restaurants[:st.session_state.visible_count]

if restaurants_to_show:
    price_display = {
        1: "Under ₹200",
        2: "₹200–₹500",
        3: "₹500–₹1000",
        4: "₹1000+"
    }

    for i in range(0, len(restaurants_to_show), 2):
        cols = st.columns(2)
        for col_idx in range(2):
            if i + col_idx < len(restaurants_to_show):
                r = restaurants_to_show[i + col_idx]
                name = r.get("name", "Unknown")
                rating = r.get("rating", "N/A")
                address = r.get("formatted_address", "No Address")
                level = r.get("price_level", 0)
                price_text = price_display.get(level, "Unknown")
                maps_url = f"https://www.google.com/maps/place/?q=place_id:{r.get('place_id')}"

                if "photos" in r:
                    photo_ref = r["photos"][0]["photo_reference"]
                    image_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_ref}&key={GOOGLE_API_KEY}"
                else:
                    image_url = "https://via.placeholder.com/400x180?text=No+Image"

                with cols[col_idx]:
                    html_card = f"""
                    <div class="restaurant-card">
                        <img src="{image_url}" alt="Restaurant Image" />
                        <h4>{name}</h4>
                        <p>⭐ {rating} &nbsp; | &nbsp; 💸 {price_text}</p>
                        <p>{address}</p>
                        <a href="{maps_url}" target="_blank">📍 View on Map</a>
                    </div>
                    """
                    st.markdown(html_card, unsafe_allow_html=True)

    # ✅ Always allow loading more if available
    if st.session_state.visible_count < len(st.session_state.restaurants):
        if st.button("🔄 Load More"):
            st.session_state.visible_count += 6
else:
    if st.session_state.restaurants:
        st.info("No more results to show.")

