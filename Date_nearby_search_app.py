import streamlit as st
import requests
import time

# --- CONFIG ---
st.set_page_config(page_title="Where - Date Recommender", page_icon="🍽️", layout="wide")
GOOGLE_API_KEY = "AIzaSyB_hTKCkfWDcaXQvv6iiKAuPSlF1KM3pYM"  # Replace this with your Google Places API key

# --- CITIES ---
TIER1_CITIES = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Hyderabad", "Kolkata", "Pune", "Ahmedabad"]
TIER2_CITIES = ["Jaipur", "Lucknow", "Indore", "Bhopal", "Chandigarh", "Surat", "Nagpur", "Kochi", "Vadodara", "Goa"]
ALL_CITIES = sorted(set(TIER1_CITIES + TIER2_CITIES))

# --- SESSION STATE ---
if "restaurants" not in st.session_state:
    st.session_state.restaurants = []
if "next_token" not in st.session_state:
    st.session_state.next_token = None
if "load_count" not in st.session_state:
    st.session_state.load_count = 0

# --- JAVASCRIPT FOR LOCATION ---
st.markdown("""
    <script>
    navigator.geolocation.getCurrentPosition(
        (position) => {
            const coords = position.coords.latitude + "," + position.coords.longitude;
            window.location.href = `/?coords=${coords}`;
        },
        (error) => {
            console.log("Location access denied.");
        }
    );
    </script>
""", unsafe_allow_html=True)

# --- GET LOCATION FROM URL ---
coords = st.query_params.get("coords", [None])[0]
use_location = coords is not None

# --- SIDEBAR ---
with st.sidebar:
    st.header("🔍 Search Filters")

    if use_location:
        st.success("📍 Using your current location!")
    else:
        st.warning("Couldn't fetch location. Select city manually.")
        selected_city = st.selectbox("🏙️ Select City", ALL_CITIES)

    cuisine = st.selectbox("🍴 Cuisine Type", ["Italian", "Mexican", "Indian", "Chinese", "Japanese"])
    dish = st.text_input("🍛 Specific Dish (optional)")

    budget_option = st.selectbox(
        "💰 Budget per Person",
        ["₹ (Under ₹200)", "₹₹ (₹200–₹500)", "₹₹₹ (₹500–₹1000)", "₹₹₹₹ (₹1000+)"]
    )
    budget_map = {"₹ (Under ₹200)": 1, "₹₹ (₹200–₹500)": 2, "₹₹₹ (₹500–₹1000)": 3, "₹₹₹₹ (₹1000+)": 4}
    price_level = budget_map[budget_option]

    min_rating = st.slider("⭐ Minimum Rating", 1.0, 5.0, 4.0, step=0.1)

# --- GET COORDINATES FROM CITY ---
def get_coordinates_from_city(city):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={city}&key={GOOGLE_API_KEY}"
    res = requests.get(url).json()
    if res["status"] == "OK":
        loc = res["results"][0]["geometry"]["location"]
        return f"{loc['lat']},{loc['lng']}"
    return None

# --- FETCH RESTAURANTS ---
def get_restaurants(coords, cuisine, dish, price_level, min_rating, token=None):
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    keyword = f"{cuisine} {dish} restaurant" if dish else f"{cuisine} restaurant"
    params = {
        "location": coords,
        "radius": 8000,
        "type": "restaurant",
        "keyword": keyword,
        "key": GOOGLE_API_KEY
    }
    if token:
        params = {"pagetoken": token, "key": GOOGLE_API_KEY}
        time.sleep(2)  # required for next_page_token

    res = requests.get(url, params=params).json()
    results = [
        r for r in res.get("results", [])
        if r.get("rating", 0) >= min_rating and r.get("price_level") == price_level
    ]
    return results, res.get("next_page_token")

# --- DISPLAY RESTAURANTS ---
def display_restaurants(restaurants):
    num_cols = 3
    for i in range(0, len(restaurants), num_cols):
        cols = st.columns(num_cols)
        for col_idx in range(num_cols):
            if i + col_idx < len(restaurants):
                r = restaurants[i + col_idx]
                name = r.get("name", "Unknown")
                rating = r.get("rating", "N/A")
                address = r.get("vicinity", "No address available")
                place_id = r.get("place_id")
                price = {1: "Under ₹200", 2: "₹200–₹500", 3: "₹500–₹1000", 4: "₹1000+"}.get(r.get("price_level"), "?")
                img_url = "https://via.placeholder.com/400x250?text=No+Image"
                if "photos" in r:
                    ref = r["photos"][0]["photo_reference"]
                    img_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={ref}&key={GOOGLE_API_KEY}"
                maps_url = f"https://www.google.com/maps/place/?q=place_id:{place_id}"

                # Updated CSS for cleaner and more visible card
                card_html = f"""
                <div style="
                    background-color: #e3f2fd; /* Light blue */;
                    border-radius: 12px;
                    border: 1px solid #ddd;
                    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
                    overflow: hidden;
                    text-align: left;
                    padding: 15px;
                    height: 550px;
                    display: flex;
                    flex-direction: column;
                    justify-content: space-between;
                ">
                    <div style="height: 220px; overflow: hidden;">
                        <img src="{img_url}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 10px;" />
                    </div>
                    <div style="padding: 12px 0;">
                        <h4 style="margin: 0; font-size: 18px; color: #333; font-weight: 600;">{name}</h4>
                        <p style="margin: 5px 0; font-size: 14px; color: #444;">⭐ <strong>{rating}</strong> | 💸 <strong>{price}</strong></p>
                        <p style="margin: 8px 0 0; font-size: 13px; color: #666;">📍 {address}</p>
                    </div>
                    <div>
                        <a href="{maps_url}" target="_blank" style="
                            display: block;
                            text-align: center;
                            padding: 10px;
                            background-color: #f04e30;
                            color: white;
                            font-size: 14px;
                            font-weight: bold;
                            text-decoration: none;
                            border-radius: 8px;
                        ">📍 View on Map</a>
                    </div>
                </div>
                """

                with cols[col_idx]:
                    st.markdown(card_html, unsafe_allow_html=True)

# --- MAIN ---
st.title("🍽️ Where - Date Recommender")
st.markdown("Find a restaurant that fits your vibe ✨")

if st.button("Search Restaurants 🚀"):
    if not use_location:
        coords = get_coordinates_from_city(selected_city)

    if not coords:
        st.error("❌ Could not determine location. Try again.")
    else:
        st.session_state.restaurants = []
        st.session_state.load_count = 0
        st.session_state.next_token = None
        new, token = get_restaurants(coords, cuisine, dish, price_level, min_rating)
        st.session_state.restaurants.extend(new)
        st.session_state.next_token = token
        st.session_state.load_count += 1

if st.session_state.restaurants:
    st.success(f"Found {len(st.session_state.restaurants)} options so far")
    display_restaurants(st.session_state.restaurants)

    if st.session_state.next_token and len(st.session_state.restaurants) < 60:
        if st.button("🔄 Load More Restaurants"):
            new, token = get_restaurants(coords, cuisine, dish, price_level, min_rating, st.session_state.next_token)
            existing_ids = {r.get("place_id") for r in st.session_state.restaurants}
            fresh = [r for r in new if r.get("place_id") not in existing_ids]
            st.session_state.restaurants.extend(fresh)
            st.session_state.next_token = token
            st.session_state.load_count += 1
