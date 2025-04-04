import streamlit as st
import requests
import time

# ❗ MUST BE FIRST STREAMLIT COMMAND
st.set_page_config(page_title="Date Recommender", page_icon="🍽️")

# Google API Key
GOOGLE_API_KEY = "AIzaSyB_hTKCkfWDcaXQvv6iiKAuPSlF1KM3pYM"

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
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
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
def get_restaurants(location, cuisine, price_level, min_rating):
    base_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"

    all_results = []
    params = {
        "query": f"{cuisine} restaurants in {location}",
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
    cuisine = st.selectbox("🍴 Cuisine Type", ["Italian", "Mexican", "Indian", "Chinese", "Japanese"])

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

if st.button("Search Restaurants 🚀"):
    with st.spinner("Fetching delicious options..."):
        restaurants = get_restaurants(location, cuisine, price_level, min_rating)

    if restaurants:
        st.success(f"Found {len(restaurants)} options!")

        price_display = {
            1: "Under ₹200",
            2: "₹200–₹500",
            3: "₹500–₹1000",
            4: "₹1000+"
        }

        for i in range(0, len(restaurants), 2):
            cols = st.columns(2)
            for col_idx in range(2):
                if i + col_idx < len(restaurants):
                    r = restaurants[i + col_idx]
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
    else:
        st.warning("No matching restaurants found. Try adjusting your filters!")
