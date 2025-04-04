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
    "Lucknow", "Indore", "Vadodara"  # ✅ Added your city
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
            border-radius: 10px;
            padding: 10px;
        }
        img {
            border-radius: 8px;
            object-fit: cover;
            height: 150px;
            width: 100%;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Function to get restaurants with cuisine + price in the query ---
def get_restaurants(location, cuisine, price_level, min_rating):
    base_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"

    price_keywords = {
        1: "cheap",
        2: "moderately priced",
        3: "expensive",
        4: "fine dining"
    }

    price_keyword = price_keywords.get(price_level, "")
    all_results = []

    # 🔍 Combined cuisine + price in query
    params = {
        "query": f"{price_keyword} {cuisine} restaurants in {location}",
        "key": GOOGLE_API_KEY
    }

    for _ in range(3):  # max 3 pages
        response = requests.get(base_url, params=params)
        data = response.json()
        results = data.get("results", [])
        all_results.extend(results)

        next_token = data.get("next_page_token")
        if not next_token:
            break
        time.sleep(2)  # Google requires a short delay
        params = {
            "pagetoken": next_token,
            "key": GOOGLE_API_KEY
        }

    # ✅ Filter by price level and rating
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
    
    # 💰 Budget selector
    budget_option = st.selectbox(
        "💰 Budget per Person (Approx)", 
        [
            "₹ (Under ₹200)",
            "₹₹ (₹200–₹500)",
            "₹₹₹ (₹500–₹1000)",
            "₹₹₹₹ (₹1000+)"
        ]
    )
    budget_map = {
        "₹ (Under ₹200)": 1,
        "₹₹ (₹200–₹500)": 2,
        "₹₹₹ (₹500–₹1000)": 3,
        "₹₹₹₹ (₹1000+)": 4
    }
    price_level = budget_map[budget_option]

    min_rating = st.slider("⭐ Minimum Rating", 1.0, 5.0, 4.0, step=0.1)

# 🚀 Fetch results
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

        # Display two cards per row
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

                    with cols[col_idx]:
                        with st.container():
                            if "photos" in r:
                                photo_ref = r["photos"][0]["photo_reference"]
                                image_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo_ref}&key={GOOGLE_API_KEY}"
                                st.image(image_url, use_container_width=True)
                            else:
                                st.image("https://via.placeholder.com/400x150?text=No+Image", use_container_width=True)

                            st.markdown(f"**{name}**")
                            st.write(f"⭐ {rating} | 💸 {price_text}")
                            st.caption(address)
                            st.markdown(f"[📍 Map]({maps_url})")
                            st.markdown("---")
    else:
        st.warning("No matching restaurants found. Try adjusting your filters!")
